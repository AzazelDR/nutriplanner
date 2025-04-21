import os
import json
import regex as re
from fastapi import WebSocket, WebSocketDisconnect
import google.generativeai as genai
from dotenv import load_dotenv

from services.support import SupportService  # servicio que carga doctores

# ---------- Configuración ----------------------------------------------------
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))


# ---------- Servicio ---------------------------------------------------------
class BotService:
    def __init__(
        self,
        plans_file: str = "accommodations.json",
        doctors_file: str = "doctores.json",
    ):
        # Modelo (puedes cambiar por otro). ***
        self.model = genai.GenerativeModel("gemini-2.0-flash")

        # ---------------------------------------------------------------------
        # Cargar planes
        try:
            with open(plans_file, encoding="utf-8") as f:
                self.plans = json.load(f).get("planes_nutricionales", [])
        except FileNotFoundError:
            self.plans = []

        # Cargar doctores a través del servicio
        self.support_service = SupportService(doctors_file)
        self.doctors = self.support_service.get_all()

       # --------------------------------------------------------------------
        # HISTORIAL / SYSTEM PROMPTS
        # --------------------------------------------------------------------
        self.history: list[dict] = [
            # PROMPT 1 – personalidad
            {
                "role": "user",
                "parts": (
                    "Actúa como un agente especialista en nutrición. "
                    "Tu nombre es **AR Nutrición**."
                ),
            },
            {"role": "model", "parts": "¡Hola! Soy AR Nutrición."},

            # PROMPT 2 – interacción y recetas con ingredientes
            {
                "role": "user",
                "parts": (
                    "Debes saludar e interactuar con los usuarios. "
                    "Ellos te darán listados de alimentos que tienen en casa "
                    "y tú debes proponer **recetas saludables** justificadas."
                ),
            },
            {"role": "model", "parts": "Entendido, pediré la lista de alimentos y sugeriré recetas."},

            # PROMPT 3 – detectar padecimientos y sugerir doctor
            {
                "role": "user",
                "parts": (
                    "Si el usuario menciona un padecimiento, "
                    "recomienda UN especialista adecuado de la siguiente lista: "
                    f"{self.doctors}"
                ),
            },
            {"role": "model", "parts": "He cargado la lista de especialistas y los usaré cuando sea necesario."},

            # PROMPT 4 – si no hay ingredientes suficientes
            {
                "role": "user",
                "parts": (
                    "Si el usuario no tiene suficientes alimentos para formar una receta saludable, "
                    "explícale por qué y sugiérele ingredientes fáciles de conseguir, saludables y económicos."
                ),
            },
            {"role": "model", "parts": "Comprendido, avisaré si faltan ingredientes y sugeriré opciones."},
        ]

        # --- Catálogo de planes como contexto --------------------------------
        if self.plans:
            self.history += [
                {"role": "user", "parts": f"Catálogo de planes: {self.plans}"},
                {
                    "role": "model",
                    "parts": "He cargado los planes nutricionales.",
                },
            ]

        # --- Reglas de formato unificadas ------------------------------------
        reglas = (
            "Reglas estrictas:\n"
            "1. Si el usuario NO menciona alergias/intolerancias/enfermedades, "
            "puedes sugerir cuantos platos o recetas sean útiles y "
            "recomendar hasta 3 planes nutricionales.\n"
            "2. Si SÍ menciona alguna condición, añade UN doctor adecuado además de las recetas/planes.\n"
            "3. Cuando el usuario proporcione ingredientes, genera tantas recetas saludables "
            "como consideres necesarias (mínimo 1, máximo el número solicitado por el usuario), con:\n"
            "   • Título en negrita\n"
            "   • Lista corta de pasos\n"
            "   • Breve justificación nutricional.\n"
            "4. Si no hay ingredientes suficientes, díselo y sugiere al menos 3 alimentos fáciles de conseguir.\n"
            "5. Usa enlaces en el formato:\n"
            "     Enlace: https://nutriplanner-ia.vercel.app/accommodation/{id}\n"
            "6. Sin precios ni datos personales adicionales."
        )
        self.history += [
            {"role": "user", "parts": reglas},
            {"role": "model", "parts": "Seguiré todas las reglas al pie de la letra."},
        ]

    # ---------------------------- WebSocket loop ----------------------------
    async def chat(self, ws: WebSocket):
        await ws.accept()
        chat = self.model.start_chat(history=self.history)

        await ws.send_json(
            {
                "message": "¡Hola! Soy NutriPlanner AI. ¿En qué puedo ayudarte hoy?",
                "status": "success",
            }
        )

        try:
            while True:
                data = await ws.receive_json()
                user_msg = data.get("message", "").strip()
                if not user_msg:
                    await ws.send_json(
                        {
                            "message": "No recibí tu mensaje, inténtalo de nuevo.",
                            "status": "error",
                        }
                    )
                    continue

                # --------- ÚNICA llamada a Gemini -------------
                response = chat.send_message(user_msg)
                raw = response.candidates[0].content.parts[0].text
                formatted = self._format_response(raw)

                await ws.send_json({"message": formatted, "status": "success"})

        except WebSocketDisconnect:
            print("WebSocket desconectado")
        except Exception as exc:
            await ws.send_json(
                {"message": f"Error interno: {exc}", "status": "error"}
            )

    # -------------------------- Formateo utilitario -------------------------
    def _format_response(self, text: str) -> str:
        """
        • [etiqueta](url)  -> <a class="recommendation-link">etiqueta</a>
        • 'Enlace o contacto: URL' -> mismo anchor, con el nombre real del plan
        • Cada línea va envuelta en <p>
        """
        html = text  # punto de partida

        # 1) Markdown [etiqueta](url) -> anchor
        html = re.sub(
            r"\[([^\]]+)\]\((https?://[^\)]+)\)",
            lambda m: (
                f'<a href="{m.group(2)}" class="recommendation-link" '
                f'target="_blank" rel="noopener noreferrer">{m.group(1)}</a>'
            ),
            html,
        )

        # 2) 'Enlace o contacto:'  /  'Enlace:' -> anchor con nombre del plan
        def repl_plan_link(m):
            url = m.group(1)
            match_id = re.search(r"/accommodation/(\d+)", url)
            if match_id:
                pid = int(match_id.group(1))
                plan = next((p for p in self.plans if p.get("id") == pid), None)
                label = plan["nombre"] if plan else "Ver plan"
            else:
                label = "Ver link"

            return (
                f'<a href="{url}" class="recommendation-link" '
                f'target="_blank" rel="noopener noreferrer">{label}</a>'
            )

        # admite cualquier variante: Enlace: ó Enlace o contacto:
        html = re.sub(
            r"Enlace(?:\s+o\s+contacto)?:\s*(https?://\S+)",
            repl_plan_link,
            html,
            flags=re.IGNORECASE,
        )

        # 3) <p> por línea
        return "".join(
            f"<p>{line}</p>" if line.strip() else "<p></p>"
            for line in html.split("\n")
        )

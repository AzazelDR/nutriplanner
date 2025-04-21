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

        # ---------------------------------------------------------------------
        # Historial inicial / system‑prompt
        self.history = [
            {
                "role": "user",
                "parts": (
                    "Eres un nutricionista virtual experto. "
                    "Tu tarea es recomendar planes nutricionales y, "
                    "si detectas alergias, intolerancias o enfermedades, "
                    "añadir un solo especialista de la lista disponible."
                ),
            },
            {
                "role": "model",
                "parts": "Entendido, seré un nutricionista virtual experto.",
            },
            {
                "role": "user",
                "parts": f"Catálogo de planes disponibles: {self.plans}",
            },
            {
                "role": "model",
                "parts": "He cargado los planes nutricionales.",
            },
            {
                "role": "user",
                "parts": f"Lista de doctores especialistas: {self.doctors}",
            },
            {
                "role": "model",
                "parts": "He cargado los doctores especialistas.",
            },
        ]

        # Reglas estrictas para Gemini
        reglas = (
            "Reglas estrictas para tus respuestas:\n"
            "1. Si el usuario NO menciona alergias, intolerancias ni enfermedades, "
            "solo recomienda un máximo de 3 planes (formato bullet).\n"
            "2. Si SÍ menciona alguna de esas condiciones, primero "
            "recomienda hasta 3 planes, luego UN doctor adecuado "
            "(nombre, especialidad, teléfono, link).\n"
            "3. Usa exactamente este formato:\n\n"
            "   Introducción breve\n"
            "   Te recomiendo:\n\n"
            "   - [Nombre] (descripción corta)\n"
            "     Enlace o contacto: https://nutriplanner-ia.vercel.app/accommodation/{id}\n\n"
            "   Frase motivacional final\n\n"
            "Si añades doctor:\n"
            "   Te recomiendo tambien este especialista con tu alergia, para asistencia personalizada:\n"
            "   - Dr. Nombre (Especialidad)\n"
            "   - Teléfono: +503 XXXXXXXX\n"
            "   - Link: https://...\n\n"
            "4. No incluyas precios ni datos adicionales.\n"
            "5. Para temas no nutricionales: "
            "'Lo siento, solo puedo ayudarte con nutrición o derivarte a un especialista.'"
        )
        self.history += [
            {"role": "user", "parts": reglas},
            {
                "role": "model",
                "parts": "Comprendido. Seguiré las reglas al pie de la letra.",
            },
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
        • Convierte [etiqueta](url) en <a class="recommendation-link">.
        • Reemplaza “Enlace o contacto: URL” por el mismo anchor.
        • Envuelve cada línea en <p>.
        """
        html = text  # <- punto de partida

        # 1) Markdown [etiqueta](url) -> <a>
        html = re.sub(
            r"\[([^\]]+)\]\((https?://[^\)]+)\)",
            lambda m: (
                f'<a href="{m.group(2)}" class="recommendation-link" '
                f'target="_blank" rel="noopener noreferrer">{m.group(1)}</a>'
            ),
            html,
        )

        # 2) “Enlace o contacto: URL” -> <a>
        def repl_plan_link(m):
            url = m.group(1)
            match = re.search(r"/accommodation/(\\d+)", url)
            if match:
                pid = int(match.group(1))
                plan = next((p for p in self.plans if p.get("id") == pid), None)
                label = plan["nombre"] if plan else "Ver plan"
            else:
                label = "Ver link"
            return (
                f'<a href="{url}" class="recommendation-link" '
                f'target="_blank" rel="noopener noreferrer">{label}</a>'
            )

        html = re.sub(r"Enlace:\s*(https?://\S+)", repl_plan_link, html)

        # 3) <p> por línea
        return "".join(
            f"<p>{line}</p>" if line.strip() else "<p></p>"
            for line in html.split("\n")
        )
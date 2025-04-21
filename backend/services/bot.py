import os, json, regex as re
from fastapi import WebSocket, WebSocketDisconnect
import google.generativeai as genai
from dotenv import load_dotenv
from services.support import SupportService

# ------------------------------------------------------------------- config
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# ------------------------------------------------------------------- servicio
class BotService:
    def __init__(self,
                 plans_file: str = "accommodations.json",
                 doctors_file: str = "doctores.json"):
        self.model = genai.GenerativeModel("gemini-2.0-flash")

        # -------- planes
        try:
            with open(plans_file, encoding="utf-8") as f:
                self.plans = json.load(f)["planes_nutricionales"]
        except Exception:
            self.plans = []

        # -------- doctores
        self.support_service = SupportService(doctors_file)
        self.doctors = self.support_service.get_all()

        # -------- historial / system‑prompts (PROMPTS 1‑4)
        self.history = [
            {"role": "user",
             "parts": "Actúa como un agente especialista en nutrición. Tu nombre es **AR Nutrición**."},
            {"role": "model", "parts": "¡Hola! Soy AR Nutrición."},

            {"role": "user",
             "parts": "Debes saludar e interactuar; los usuarios darán alimentos y tú generarás **recetas saludables** justificadas."},
            {"role": "model",
             "parts": "Entendido, solicitaré la lista de alimentos y propondré recetas."},

            {"role": "user",
             "parts": f"Si el usuario menciona un padecimiento, recomienda UN especialista adecuado de la lista: {self.doctors}"},
            {"role": "model",
             "parts": "He cargado los especialistas y los sugeriré cuando sea necesario."},

            {"role": "user",
             "parts": "Si el usuario no tiene suficientes alimentos, explícale por qué y sugiere ingredientes fáciles de conseguir."},
            {"role": "model",
             "parts": "Comprendido, avisaré si faltan ingredientes y sugeriré opciones."},
        ]

        if self.plans:
            self.history += [
                {"role": "user", "parts": f"Catálogo de planes: {self.plans}"},
                {"role": "model", "parts": "He cargado los planes nutricionales."},
            ]

        # ---------------- reglas estrictas
        reglas = (
            "Reglas estrictas:\n"
            "1. Si el usuario NO menciona alergias/padecimientos, sugiere cuantas recetas sean útiles y hasta 3 planes.\n"
            "2. Si SÍ menciona padecimiento, añade UN doctor adecuado.\n"
            "3. Cuando dé ingredientes, genera tantas recetas como creas necesarias (≥1), con:\n"
            "   • Título en negrita\n   • Lista de pasos\n   • Justificación breve.\n"
            "4. Si no hay ingredientes suficientes, explícalo y sugiere 3 alimentos fáciles de conseguir.\n"
            "5. Usa enlaces así: Enlace: https://nutriplanner-ia.vercel.app/accommodation/{id}\n"
            "6. Nada de precios ni datos personales.\n"
            "7. Encabeza cada receta con “🍽️”.\n"
            "8. Empieza cada paso con “➡️” y cada justificación con “✅”.\n"
            "9. Separa secciones con una línea que contenga solo “———”."
        )
        self.history += [
            {"role": "user",  "parts": reglas},
            {"role": "model", "parts": "Seguiré todas las reglas al pie de la letra."},
        ]

    # --------------------------------------------------- WebSocket
    async def chat(self, ws: WebSocket):
        await ws.accept()
        chat = self.model.start_chat(history=self.history)
        await ws.send_json({"message": "¡Hola! Soy NutriPlanner AI. ¿En qué puedo ayudarte hoy?",
                            "status": "success"})
        try:
            while True:
                user_msg = (await ws.receive_json()).get("message", "").strip()
                if not user_msg:
                    await ws.send_json({"message": "No recibí tu mensaje, inténtalo de nuevo.",
                                        "status": "error"})
                    continue

                resp = chat.send_message(user_msg)
                raw = resp.candidates[0].content.parts[0].text
                await ws.send_json({"message": self._format_response(raw),
                                    "status": "success"})
        except WebSocketDisconnect:
            print("WebSocket desconectado")
        except Exception as exc:
            await ws.send_json({"message": f"Error interno: {exc}", "status": "error"})

    # --------------------------------------------------- formateo
    def _format_response(self, text: str) -> str:
        html = text

        # markdown [...] -> anchor
        html = re.sub(
            r"\[([^\]]+)\]\((https?://[^\)]+)\)",
            lambda m: f'<a href="{m.group(2)}" class="recommendation-link" '
                      f'target="_blank" rel="noopener noreferrer">{m.group(1)}</a>',
            html)

        # Enlace: URL -> anchor con nombre real
        def repl_link(m):
            url = m.group(1)
            mid = re.search(r"/accommodation/(\d+)", url)
            label = "Ver plan"
            if mid:
                pid = int(mid.group(1))
                plan = next((p for p in self.plans if p["id"] == pid), None)
                if plan:
                    label = plan["nombre"]
            return (f'<a href="{url}" class="recommendation-link" target="_blank" '
                    f'rel="noopener noreferrer">{label}</a>')

        html = re.sub(r"Enlace(?:\s+o\s+contacto)?:\s*(https?://\S+)",
                      repl_link, html, flags=re.I)

        # Fusionar viñeta + enlace (‑ Plan X ... + <a>Plan X</a>)
        html = re.sub(
            r"<p>-\s*([^<]+?)\s*</p>\s*<p><a([^>]+)>([^<]+)</a></p>",
            r"<p>- <a\2>\1</a></p>",
            html, flags=re.DOTALL)

        # <p> por línea
        return "".join(f"<p>{ln}</p>" if ln.strip() else "<p></p>"
                       for ln in html.split("\n"))

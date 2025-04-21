import os
import json
import regex as re
from fastapi import WebSocket, WebSocketDisconnect
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

class BotService:
    def __init__(
        self,
        plans_file: str = "accommodations.json",
        doctors_file: str = "doctores.json"
    ):
        # Modelo de Gemini
        self.model = genai.GenerativeModel("gemini-2.0-flash")

        # 1) Carga los planes nutricionales
        try:
            with open(plans_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.plans = data.get("planes_nutricionales", [])
        except Exception:
            self.plans = []

        # 2) Carga el listado de doctores especialistas
        try:
            with open(doctors_file, "r", encoding="utf-8") as f:
                self.doctors = json.load(f)
        except Exception:
            self.doctors = []

        # Construcción del historial inicial
        self.history = [
            # System prompt
            {
                "role": "user",
                "parts": (
                    "Eres un nutricionista virtual experto. "
                    "Tu única misión es recomendar planes nutricionales y, "
                    "si el usuario menciona algún padecimiento, recomendarle "
                    "el especialista más adecuado."
                )
            },
            {
                "role": "model",
                "parts": "Entendido, seré un nutricionista virtual experto."
            }
        ]

        # Contexto de planes
        if self.plans:
            self.history += [
                {
                    "role": "user",
                    "parts": f"Tienes disponible este catálogo de planes: {self.plans}"
                },
                {
                    "role": "model",
                    "parts": "Comprendo, he cargado los planes nutricionales."
                }
            ]

        # Contexto de doctores
        if self.doctors:
            self.history += [
                {
                    "role": "user",
                    "parts": f"También tienes disponible esta lista de doctores especialistas: {self.doctors}"
                },
                {
                    "role": "model",
                    "parts": "Perfecto, he cargado los doctores especialistas."
                }
            ]

        # Reglas de formato
        reglas = (
            "Reglas estrictas para tus respuestas:\n"
            "1. Recomienda un máximo de 3 planes nutricionales si el usuario pide un plan.\n"
            "2. Si el usuario menciona un padecimiento, "
            "recomienda UN doctor de la lista, con su nombre, especialidad, teléfono y link.\n"
            "3. Usa este formato EXACTO:\n\n"
            "   Introducción breve\n"
            "   Te recomiendo:\n\n"
            "   - [Nombre del plan o doctor] (descripción corta)\n"
            "     Enlace o contacto: https://nutriplanner-ia.vercel.app/accommodation/{id} o {Telefono}\n\n"
            "   Frase motivacional final\n\n"
            "4. No agregues precios, ni información extra ni hagas preguntas.\n"
            "5. Para temas no nutricionales o no médicos: "
            "'Lo siento, solo puedo ayudarte con nutrición o derivarte a un especialista.'"
        )
        self.history += [
            {"role": "user", "parts": reglas},
            {"role": "model", "parts": "Entendido, seguiré esas reglas estrictamente."}
        ]

    async def chat(self, ws: WebSocket):
        await ws.accept()
        chat = self.model.start_chat(history=self.history)

        # Saludo inicial
        saludo = "¡Hola! Soy NutriPlanner AI. ¿En qué puedo ayudarte hoy?"
        await ws.send_json({"message": saludo, "status": "success"})

        try:
            while True:
                data = await ws.receive_json()
                user_msg = data.get("message", "").strip()
                if not user_msg:
                    await ws.send_json({
                        "message": "No recibí tu mensaje, inténtalo de nuevo.",
                        "status": "error"
                    })
                    continue
                resp = chat.send_message(user_msg)
                raw = resp.candidates[0].content.parts[0].text

                # Formatear enlaces Markdown → HTML
                formatted = self._format_response(raw)
                await ws.send_json({"message": formatted, "status": "success"})

        except WebSocketDisconnect:
            print("WebSocket desconectado")
        except Exception as e:
            await ws.send_json({
                "message": f"Error interno: {e}",
                "status": "error"
            })
    def _format_response(self, text: str) -> str:
        # Markdown [label](url) → <a>
        def md_link(m):
            label, url = m.group(1), m.group(2)
            return f'<a href="{url}" class="recommendation-link" target="_blank">{label}</a>'

        html = re.sub(
            r"\[([^\]]+)\]\((https?://[^\)]+)\)",
            md_link,
            text
        )
        # "Enlace: https://..." → <a>Ver plan</a>
        html = re.sub(
            r"Enlace:\s*(https?://\S+)",
            lambda m: f'<a href="{m.group(1)}" class="recommendation-link" target="_blank">Ver plan</a>',
            html
        )
        # Wrap lines in <p>
        return "".join(
            f"<p>{line}</p>" if line.strip() else "<p></p>"
            for line in html.split("\n")
        )

import regex as re
import os
import json
from fastapi import WebSocket, WebSocketDisconnect
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

class BotService:
    def __init__(self, data_file: str = "accommodations.json"):
        # Modelo de Gemini
        self.model = genai.GenerativeModel("gemini-2.0-flash")

        # Carga solo los planes nutricionales
        try:
            with open(data_file, "r", encoding="utf-8") as f:
                js = json.load(f)
                # tu JSON original tenía "planes_nutricionales"
                self.plans = js.get("planes_nutricionales", [])
        except Exception:
            self.plans = []

        # Construcción del history inicial
        # System prompt
        self.history = [
            {
                "role": "user",
                "parts": (
                    "Eres un nutricionista virtual experto. "
                    "Tu única misión es recomendar planes nutricionales."
                )
            },
            {
                "role": "model",
                "parts": "Entendido, seré un nutricionista virtual experto en planes."
            }
        ]

        # Incluir los datos de planes como contexto
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

        # Reglas de formato
        reglas = (
            "Cuando respondas:\n"
            "1. Recomienda un máximo de 3 planes.\n"
            "2. Usa este formato EXACTO:\n"
            "   Introducción breve\n"
            "   Te recomiendo:\n\n"
            "   - [Nombre del plan] (descripción corta)\n"
            "     Enlace: https://nutriplanner-ia.vercel.app/accommodation/{id}\n\n"
            "   Frase motivacional final\n"
            "3. No agregues precios, ni información extra ni hagas preguntas."
        )
        self.history += [
            {"role": "user", "parts": reglas},
            {"role": "model", "parts": "Entendido, seguiré esas reglas estrictamente."}
        ]
    def _format_response(self, text: str) -> str:
        """
        Convierte cualquier enlace Markdown [Etiqueta](URL) en un <a> con clase,
        y envuelve cada línea en <p> para que el front lo renderice adecuadamente.
        """
        def repl(m):
            label, url = m.group(1), m.group(2)
            return f'<a href="{url}" class="recommendation-link" target="_blank">{label}</a>'

        # Markdown links a HTML
        html = re.sub(r"\[([^\]]+)\]\((https?://[^\)]+)\)", repl, text)

        # wrap en <p>
        return "".join(
            f"<p>{line}</p>" if line.strip() else "<p></p>"
            for line in html.split("\n")
        )

    async def chat(self, ws: WebSocket):
        await ws.accept()

        # Inicio de chat con historial
        chat = self.model.start_chat(history=self.history)

        # Saludo inicial
        saludo = "¡Hola! Soy NutriPlanner AI. ¿En qué plan nutricional puedo ayudarte hoy?"
        await ws.send_json({"message": saludo})

        try:
            while True:
                data = await ws.receive_json()
                user_msg = data.get("message", "").strip()
                if not user_msg:
                    await ws.send_json({"message": "No recibí tu mensaje, inténtalo de nuevo.", "status": "error"})
                    continue

                response = chat.send_message(user_msg)
                raw = response.candidates[0].content.parts[0].text

                # formateo los enlaces aquí
                formatted = self._format_response(raw)

                await ws.send_json({"message": formatted, "status": "success"})

        except WebSocketDisconnect:
            print("WebSocket desconectado")
        except Exception as e:
            await ws.send_json({"message": f"Error interno: {e}", "status": "error"})
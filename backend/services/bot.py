import os
import json
import regex as re
from fastapi import WebSocket, WebSocketDisconnect
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

class BotService:
    def __init__(self,
                 plans_file: str = "accommodations.json",
                 doctors_file: str = "doctores.json"):
        # Modelo de Gemini
        self.model = genai.GenerativeModel("gemini-2.0-flash")

        # Cargar planes
        try:
            with open(plans_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.plans = data.get("planes_nutricionales", [])
        except Exception:
            self.plans = []

        # Cargar doctores
        try:
            with open(doctors_file, "r", encoding="utf-8") as f:
                self.doctors = json.load(f)
        except Exception:
            self.doctors = []

        # Historial inicial con tus 4 prompts
        self.history = [
            {"role": "user", "parts": "Tienes que actuar como un agente especialista en nutrición tu nombre es AR nutrición."},
            {"role": "model", "parts": "Entendido, soy AR nutrición, agente especialista en nutrición."},

            {"role": "user", "parts": (
                "Tienes que saludar a los usuarios e interactuar con ellos. "
                "Ellos te brindarán listados de alimentos que tienen en casa "
                "y tú debes darles recetas saludables y justificar cada una."
            )},
            {"role": "model", "parts": "Comprendido, saludaré e interactuaré, propondré recetas saludables y justificaré cada una."},

            {"role": "user", "parts": (
                "Debes analizar cada usuario y verificar si tiene algún problema de salud. "
                "Si detectas un padecimiento, recomiéndale el especialista más adecuado "
                "de este dataset de información: "
                f"{json.dumps(self.doctors, ensure_ascii=False)}"
            )},
            {"role": "model", "parts": "Entendido, analizaré su salud y recomendaré un especialista del dataset si es necesario."},

            {"role": "user", "parts": (
                "Si un usuario no tiene los alimentos suficientes para una receta saludable, "
                "informa que no es suficiente para una alimentación saludable, explica por qué y ofrece "
                "sugerencias de alimentos fáciles de conseguir y saludables."
            )},
            {"role": "model", "parts": "Comprendido, notificaré faltantes y sugeriré alternativas accesibles y saludables."},
        ]

        # Contexto adicional: catálogo de planes
        if self.plans:
            self.history += [
                {"role": "user", "parts": f"Tienes disponible este catálogo de planes nutricionales: {self.plans}"},
                {"role": "model", "parts": "Perfecto, he cargado los planes nutricionales."}
            ]

        # Reglas de formato (si quieres mantenerlas)
        reglas = (
            "Reglas estrictas:\n"
            "1. Recomienda máximo 3 planes.\n"
            "2. Formato EXACTO:\n"
            "   Introducción breve\n"
            "   Te recomiendo:\n\n"
            "   - [Nombre del plan] (desc corta)\n"
            "     Enlace: https://nutriplanner-ia.vercel.app/accommodation/{id}\n\n"
            "   Frase motivacional final\n"
            "3. No agregues precios ni info extra ni hagas preguntas.\n"
            "4. Para temas no nutricionales: 'Lo siento, solo puedo ayudar con nutrición.'"
        )
        self.history += [
            {"role": "user", "parts": reglas},
            {"role": "model", "parts": "Entendido, seguiré esas reglas estrictamente."}
        ]

    async def chat(self, ws: WebSocket):
        await ws.accept()

        # Iniciar chat con el historial
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

                # Enviar al modelo
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

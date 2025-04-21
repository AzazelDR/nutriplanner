import os
import json
import regex as re
import asyncio
from fastapi import WebSocket, WebSocketDisconnect
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

class BotService:
    def __init__(self):
        # Configuración de Gemini
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        self.model_name = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
        if not self.gemini_api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set")
        # Inicializar el cliente de Google Generative AI
        genai.configure(api_key=self.gemini_api_key)

        # Cargar datos de planes y lugares
        self._load_accommodations()
        # Preparar contexto base fijo
        self._initialize_base_context()

    def _load_accommodations(self):
        """Carga los datos de planes nutricionales y lugares recomendados desde JSON."""
        self.planes_nutricionales = []
        self.lugares_recomendados = []
        try:
            with open("accommodations.json", "r", encoding="utf-8") as f:
                data = json.load(f)
                self.planes_nutricionales = data.get("planes_nutricionales", [])
                self.lugares_recomendados = data.get("lugares_recomendados", [])
        except Exception as e:
            print(f"Error loading accommodations.json: {e}")

    def _initialize_base_context(self):
        """Construye el contexto inicial que no se reinicia en cada mensaje."""
        self.base_context = [
            {
                "role": "system",
                "content": (
                    "Eres un nutricionista virtual experto que recomienda planes nutricionales y lugares adecuados. "
                    "Tu misión es analizar las necesidades del usuario y recomendar los planes nutricionales o lugares más apropiados según su solicitud."
                )
            },
            {
                "role": "assistant",
                "content": "Entendido. Actuaré como nutricionista virtual experto."
            }
        ]

        # Si tenemos datos, los inyectamos
        if self.planes_nutricionales or self.lugares_recomendados:
            data_str = json.dumps({
                "planes": self.planes_nutricionales,
                "lugares": self.lugares_recomendados
            }, ensure_ascii=False)
            self.base_context += [
                {"role": "user", "content": f"Tienes acceso a estos datos: {data_str}"},
                {"role": "assistant", "content": "Comprendo. Tengo acceso a los datos necesarios."}
            ]

        # Reglas fijas de formato
        reglas = (
            "Reglas estrictas para tus respuestas:\n"
            "1. Recomienda máximo 3 opciones relevantes\n"
            "2. Formato obligatorio:\n"
            "   - Introducción breve\n"
            "   - 'Te recomiendo:' con doble salto de línea\n"
            "   - Cada recomendación con:\n"
            "     * '- [Nombre]' (descripción breve)\n"
            "     * Enlace: [Ver plan/lugar: Nombre](link)\n"
            "     * Doble salto de línea\n"
            "   - Frase motivacional final\n"
            "3. Exclusivamente:\n"
            "   - Sin precios\n"
            "   - Sin información no solicitada\n"
            "   - Sin preguntas adicionales\n"
            "4. Para temas no nutricionales:\n"
            "   - 'Lo siento, solo puedo ayudarte con temas de nutrición.'"
        )
        self.base_context += [
            {"role": "user", "content": reglas},
            {"role": "assistant", "content": "Entendido completamente. Seguiré estrictamente el formato y reglas especificadas."}
        ]

    async def chat(self, websocket: WebSocket):
        """Maneja la conexión WebSocket, acepta mensajes y devuelve respuestas."""
        await websocket.accept()
        # Historial arranca con el contexto base
        self.conversation_history = list(self.base_context)

        while True:
            try:
                data = await websocket.receive_json()
                user_message = data.get("message", "").strip()
                if not user_message:
                    await self._send_error(websocket, "El mensaje no puede estar vacío")
                    continue

                result = await self._process_message(user_message)
                await websocket.send_json(result)

            except WebSocketDisconnect:
                print("Client disconnected")
                break
            except json.JSONDecodeError:
                await self._send_error(websocket, "Formato de mensaje inválido")
            except Exception as e:
                print(f"Error general: {e}")
                await self._send_error(websocket, "Error interno del servidor")

    async def _process_message(self, user_message: str) -> dict:
        """Añade el mensaje del usuario, llama a Gemini y retorna la respuesta formateada."""
        # Agregar a historial
        self.conversation_history.append({"role": "user", "content": user_message})

        # Llamada síncrona a Gemini en un executor para no bloquear el event loop
        ai_response = await asyncio.get_event_loop().run_in_executor(
            None, self._get_ai_response, self.conversation_history
        )

        # Guardar respuesta en historial
        self.conversation_history.append({"role": "assistant", "content": ai_response})

        # Truncar historial a base_context + últimas 20 interacciones
        max_hist = len(self.base_context) + 20
        if len(self.conversation_history) > max_hist:
            self.conversation_history = (
                self.base_context + self.conversation_history[-20:]
            )

        return {
            "message": self._format_response(ai_response),
            "status": "success"
        }

    def _get_ai_response(self, history: list) -> str:
        """
        Construye la lista de mensajes para Gemini y lanza la petición.
        Espera un dict con .last.content en la respuesta.
        """
        msgs = [
            {"author": msg["role"], "content": msg["content"]}
            for msg in history
        ]
        response = genai.chat.create(
            model=self.model_name,
            messages=msgs,
            temperature=0.7,
            max_output_tokens=800
        )
        return response.last.content

    async def _send_error(self, websocket: WebSocket, message: str):
        """Envía un error por WebSocket."""
        await websocket.send_json({"error": message, "status": "error"})

    def _format_response(self, text: str) -> str:
        """
        Reemplaza marcadores de enlace por HTML real y envuelve cada línea en <p>.
        Usa self.planes_nutricionales y self.lugares_recomendados.
        """
        # Mapeo de nombres a URLs
        plan_links = {
            p["nombre"]: self._create_link(p["id"], p["nombre"], "plan")
            for p in self.planes_nutricionales
        }
        place_links = {
            l["nombre"]: self._create_link(l["id"], l["nombre"], "lugar")
            for l in self.lugares_recomendados
        }

        # Sustituir patrones Markdown por enlaces HTML
        def repl(m):
            kind, name = m.group(1), m.group(2)
            return plan_links.get(name) if kind == "plan" else place_links.get(name)

        text = re.sub(
            r'\[Ver (plan|lugar): (.+?)\]\([^)]*\)',
            repl,
            text
        )

        # Envolver en <p>
        html = []
        for line in text.split("\n"):
            if not line.strip():
                html.append("<p></p>")
            else:
                html.append(f"<p>{line}</p>")
        return "".join(html)

    def _create_link(self, item_id: str, name: str, item_type: str) -> str:
        """Construye un <a> apuntando al plan o lugar en el frontend."""
        base_url = "https://nutriplanner-ia.vercel.app/"
        path = "accommodation" if item_type == "plan" else "recommended_place"
        return f'<a href="{base_url}{path}/{item_id}" class="recommendation-link">{name}</a>'

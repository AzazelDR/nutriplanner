import os
import json
import regex as re
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from dotenv import load_dotenv
from typing import Dict, List
import httpx

load_dotenv()

class BotService:
    def __init__(self):
        # Clave de API de Gemini REST (fija en .env)
        self.api_key = os.getenv('GEMINI_API_KEY')
        if not self.api_key:
            raise ValueError('Configura GEMINI_API_KEY en tu .env')
        # Modelo hardcodeado
        self.model_id = 'gemini-2.0-flash'
        # Endpoint REST de Gemini generateContent
        self.endpoint = (
            f"https://generativelanguage.googleapis.com/v1beta/"
            f"models/{self.model_id}:generateContent?key={self.api_key}"
        )
        # Cargar datos locales (planes y lugares)
        self._load_accommodations()
        # Construir contexto base y reglas
        self._initialize_base_context()

    def _load_accommodations(self):
        """Carga los datos de alojamientos"""
        self.planes_nutricionales = []
        self.lugares_recomendados = []
        try:
            with open('accommodations.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.planes_nutricionales = data.get('planes_nutricionales', [])
                self.lugares_recomendados = data.get('lugares_recomendados', [])
        except FileNotFoundError:
            print('⚠️ accommodations.json no encontrado; continúa sin datos.')
        except Exception as e:
            print(f'⚠️ Error cargando datos: {e}')

    def _initialize_base_context(self):
        """Inicializa solo el contexto base (reglas y datos)"""
        self.base_context = [
            {"role": "system", "content": (
                "Eres un nutricionista virtual experto que recomienda planes nutricionales y lugares adecuados."
            )},
            {"role": "assistant", "content": "Entendido. Actuaré como nutricionista virtual experto."}
        ]
        if self.planes_nutricionales or self.lugares_recomendados:
            data_str = json.dumps({
                'planes': self.planes_nutricionales,
                'lugares': self.lugares_recomendados
            }, ensure_ascii=False)
            self.base_context.extend([
                {"role": "user", "content": f"Tienes acceso a estos datos: {data_str}"},
                {"role": "assistant", "content": "Comprendo. Tengo acceso a los datos necesarios."}
            ])
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
            "3. Sin precios, sin información no solicitada, sin preguntas adicionales\n"
            "4. Para temas no nutricionales: 'Lo siento, solo puedo ayudarte con temas de nutrición.'"
        )
        self.base_context.extend([
            {"role": "user", "content": reglas},
            {"role": "assistant", "content": "Entendido completamente. Seguiré el formato."}
        ])

    async def chat(self, websocket: WebSocket):
        """Maneja la conexión WebSocket y envía saludo inicial"""
        await websocket.accept()
        # Iniciar historial con contexto base
        self.conversation_history = self.base_context.copy()
        # Saludo inicial
        greeting = "¡Hola! Soy NutriPlanner AI, tu asistente de nutrición. ¿En qué puedo ayudarte hoy?"
        # Añadir saludo al historial y enviar al cliente
        self.conversation_history.append({"role": "assistant", "content": greeting})
        await websocket.send_json({"message": f"<p>{greeting}</p>", "status": "success"})
        try:
            while True:
                data = await websocket.receive_json()
                user_message = data.get('message', '').strip()
                if not user_message:
                    await self._send_error(websocket, 'El mensaje no puede estar vacío')
                    continue
                response = await self._process_message(user_message)
                await websocket.send_json(response)
        except WebSocketDisconnect:
            print('Client disconnected')
        except Exception as e:
            print(f'Error general en chat: {e}')

    async def _process_message(self, user_message: str) -> Dict:
        """Procesa un mensaje del usuario"""
        self.conversation_history.append({"role": "user", "content": user_message})
        ai_response = await self._get_ai_response(self.conversation_history)
        self.conversation_history.append({"role": "assistant", "content": ai_response})
        max_hist = 20 + len(self.base_context)
        if len(self.conversation_history) > max_hist:
            self.conversation_history = self.base_context + self.conversation_history[-20:]
        return {"message": self._format_response(ai_response), "status": "success"}

    async def _send_error(self, websocket: WebSocket, message: str):
        await websocket.send_json({"error": message, "status": "error"})

    async def _get_ai_response(self, messages: List[Dict]) -> str:
        """Obtiene respuesta de Gemini usando el endpoint generateContent"""
        prompt = ''
        for m in messages:
            quien = 'Usuario' if m['role'] == 'user' else 'Asistente'
            prompt += f"{quien}: {m['content']}\n"
        prompt += 'Asistente:'
        payload = {"contents": [{"parts": [{"text": prompt}]}]}
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(self.endpoint, json=payload)
            resp.raise_for_status()
            data = resp.json()
        return data['candidates'][0]['output']

    def _format_response(self, text: str) -> str:
        """Formatea la respuesta con HTML estructurado"""
        plan_links = {p['nombre']: f"<a href='/accommodation/{p['id']}' class='recommendation-link'>{p['nombre']}</a>"
                      for p in self.planes_nutricionales}
        place_links = {l['nombre']: f"<a href='/recommended_place/{l['id']}' class='recommendation-link'>{l['nombre']}</a>"
                       for l in self.lugares_recomendados}
        def repl(m):
            typ, name = m.group(1), m.group(2)
            return plan_links.get(name) if typ=='plan' else place_links.get(name)
        text = re.sub(r"\[Ver (plan|lugar): (.+?)\]\([^)]*\)", repl, text)
        return ''.join(f"<p>{line}</p>" if line.strip() else '<p></p>' for line in text.split('\n'))

# --- FastAPI App ---
app = FastAPI()
bot_service = BotService() 

@app.websocket('/ws/chatbot')
async def websocket_endpoint(websocket: WebSocket):
    await bot_service.chat(websocket)

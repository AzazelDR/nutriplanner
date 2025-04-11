import os
from fastapi import WebSocket, WebSocketDisconnect
from azure.core.credentials import AzureKeyCredential
import json
import regex as re
from dotenv import load_dotenv
from typing import Dict, List
import httpx

load_dotenv()

class BotService:
    def __init__(self):
        # Configuración de Azure
        self.azure_endpoint = "https://nutriia7304260659.services.ai.azure.com"
        self.azure_api_key = "ajkJTWywdntslj4bObmOvQrMFqikDZ69vlAzuVzflrbPXjszLw6uJQQJ99BCACYeBjFXJ3w3AAAAACOGyOTq"
        
        if not all([self.azure_endpoint, self.azure_api_key]):
            raise ValueError("Azure credentials not configured in environment variables")
            
        self.api_version = "2024-05-01-preview"
        self.model_name = "Nutri-Planner-IA"
        
        # Cargar datos
        self._load_accommodations()
        self._initialize_base_context()  # Cambiado para separar contexto base de conversación

    def _load_accommodations(self):
        """Carga los datos de alojamientos"""
        self.planes_nutricionales = []
        self.lugares_recomendados = []
        
        try:
            with open("accommodations.json", "r", encoding="utf-8") as file:
                data = json.load(file)
                self.planes_nutricionales = data.get("planes_nutricionales", [])
                self.lugares_recomendados = data.get("lugares_recomendados", [])
        except Exception as e:
            print(f"Error loading accommodations: {str(e)}")

    def _initialize_base_context(self):
        """Inicializa solo el contexto base (reglas y datos) que NO debe reiniciarse"""
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
        
        if self.planes_nutricionales or self.lugares_recomendados:
            data_str = json.dumps({
                'planes': self.planes_nutricionales,
                'lugares': self.lugares_recomendados
            }, ensure_ascii=False)
            
            self.base_context.extend([
                {"role": "user", "content": f"Tienes acceso a estos datos: {data_str}"},
                {"role": "assistant", "content": "Comprendo. Tengo acceso a los datos necesarios."}
            ])
        
        # Añadir instrucciones permanentes
        self.base_context.extend([
            {
                "role": "user",
                "content": (
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
            },
            {
                "role": "assistant",
                "content": "Entendido completamente. Seguiré estrictamente el formato y reglas especificadas."
            }
        ])

    async def chat(self, websocket: WebSocket):
        """Maneja la conexión WebSocket con reinicio limpio de conversación"""
        await websocket.accept()
        
        # Iniciar con contexto base + conversación vacía
        self.conversation_history = self.base_context.copy()
        
        while True:
            try:
                data = await websocket.receive_json()
                user_message = data.get("message", "").strip()
                
                if not user_message:
                    await self._send_error(websocket, "El mensaje no puede estar vacío")
                    continue
                    
                # Procesar mensaje
                response = await self._process_message(user_message)
                await websocket.send_json(response)
                
            except WebSocketDisconnect:
                print("Client disconnected")
                break
            except json.JSONDecodeError:
                await self._send_error(websocket, "Formato de mensaje inválido")
            except Exception as e:
                print(f"Error general: {str(e)}")
                await self._send_error(websocket, "Error interno del servidor")

    async def _process_message(self, user_message: str) -> Dict:
        """Procesa un mensaje del usuario"""
        try:
            # Añadir mensaje del usuario al historial
            self.conversation_history.append({"role": "user", "content": user_message})
            
            # Obtener respuesta de Azure (envía TODO el historial)
            ai_response = await self._get_ai_response(self.conversation_history)
            
            # Añadir respuesta al historial
            self.conversation_history.append({"role": "assistant", "content": ai_response})
            
            # Limitar historial de conversación (excepto contexto base)
            if len(self.conversation_history) > 20 + len(self.base_context):
                self.conversation_history = self.base_context + self.conversation_history[-20:]
            
            return {
                "message": self._format_response(ai_response),
                "status": "success"
            }
            
        except Exception as e:
            error_msg = f"Error al procesar la solicitud: {str(e)}"
            print(f"Error: {error_msg}")
            return {
                "error": error_msg,
                "status": "error",
                "details": str(e)
            }

    async def _send_error(self, websocket: WebSocket, message: str):
        """Envía un mensaje de error"""
        await websocket.send_json({
            "error": message,
            "status": "error"
        })

    def _prepare_messages(self, user_message: str) -> List[Dict]:
        """Prepara los mensajes para Azure"""
        return [
            *self.history,
            {"role": "user", "content": user_message},
            self._get_instructions()
        ]

    def _get_instructions(self) -> Dict:
        """Instrucciones para el modelo"""
        return {
            "role": "user",
            "content": (
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
        }

    async def _get_ai_response(self, messages: List[Dict]) -> str:
        """Obtiene respuesta de Azure AI Foundry con manejo robusto de errores"""
        try:
            # Configuración de la solicitud
            url = f"{self.azure_endpoint}/models/chat/completions?api-version={self.api_version}"
            
            headers = {
                "Content-Type": "application/json",
                "api-key": self.azure_api_key  # AI Foundry puede usar api-key o Authorization
            }
            
            payload = {
                "model": self.model_name,
                "messages": messages,
                "max_tokens": 800,
                "temperature": 0.7
            }

            # Log de depuración
            print("\n=== Solicitud a Azure AI ===")
            print(f"URL: {url}")
            print(f"Headers: {headers}")
            print(f"Payload: {json.dumps(payload, indent=2, ensure_ascii=False)}")

            # Realizar la solicitud
            async with httpx.AsyncClient(timeout=30.0) as client:  # Aumenta timeout
                response = await client.post(url, json=payload, headers=headers)
                
                # Log de la respuesta
                print("\n=== Respuesta de Azure AI ===")
                print(f"Status Code: {response.status_code}")
                print(f"Response Text: {response.text}")

                response.raise_for_status()
                data = response.json()
                
                return data["choices"][0]["message"]["content"]

        except httpx.HTTPStatusError as e:
            error_details = f"HTTP Error {e.response.status_code}"
            if e.response.text:
                try:
                    error_data = e.response.json()
                    error_details += f" - {error_data.get('error', {}).get('message', str(error_data))}"
                except:
                    error_details += f" - {e.response.text}"
            raise Exception(f"Error en la API de Azure: {error_details}")

        except httpx.RequestError as e:
            raise Exception(f"Error de conexión: {str(e)}")

        except Exception as e:
            raise Exception(f"Error inesperado: {str(e)}")


    def _format_response(self, text: str) -> str:
        """Formatea la respuesta con HTML estructurado"""
        if not text:
            return ""
            
        try:
            # Crear diccionarios de enlaces
            plan_links = {p['nombre']: self._create_link(p['id'], p['nombre'], 'plan') 
                        for p in self.planes_nutricionales}
            place_links = {l['nombre']: self._create_link(l['id'], l['nombre'], 'lugar')
                        for l in self.lugares_recomendados}
            
            # Reemplazar los patrones de enlaces
            text = re.sub(
                r'\[Ver (plan|lugar): (.+?)\]\([^)]*\)', 
                lambda m: plan_links.get(m.group(2)) if m.group(1) == 'plan' else place_links.get(m.group(2)),
                text
            )
            
            # Asegurar formato consistente
            lines = text.split('\n')
            html_lines = []
            
            for line in lines:
                if line.strip() == '':
                    html_lines.append('<p></p>')
                else:
                    html_lines.append(f'<p>{line}</p>')
            
            return ''.join(html_lines)
            
        except Exception as e:
            print(f"Error al formatear respuesta: {str(e)}")
            return text

    def _create_link(self, item_id: str, name: str, item_type: str) -> str:
        """Crea enlace HTML correctamente formateado"""
        base_url = "https://explore-sv-frontend.vercel.app/"
        url_part = "accommodation" if item_type == 'plan' else "recommended_place"
        return f'<a href="{base_url}{url_part}/{item_id}" class="recommendation-link">{name}</a>'

    def _update_chat_history(self, user_message: str, ai_response: str):
        """Actualiza el historial del chat"""
        self.history.extend([
            {"role": "user", "content": user_message},
            {"role": "assistant", "content": ai_response}
        ])
        
        # Limitar el historial a los últimos 20 mensajes
        if len(self.history) > 20:
            self.history = self.history[-20:]
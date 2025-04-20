# routes/support.py
from fastapi import APIRouter, WebSocket
from services.support import SupportService

support_router = APIRouter()
support_service = SupportService("doctores.json")

@support_router.websocket("/support")
async def websocket_support(websocket: WebSocket):
    await websocket.accept()
    # Envía la lista completa de doctores y cierra
    await websocket.send_json({"data": support_service.get_all()})
    await websocket.close()
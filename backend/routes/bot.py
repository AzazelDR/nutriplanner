from fastapi import APIRouter, WebSocket
from services.bot import BotService
from dotenv import load_dotenv

load_dotenv()

bot_router = APIRouter()
bot_service = BotService()

@bot_router.websocket("/chatbot")
async def chatBot(websocket: WebSocket):
    await bot_service.chat(websocket)

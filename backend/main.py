from dotenv import load_dotenv
import os
load_dotenv()

from fastapi import FastAPI, status
from fastapi.responses import JSONResponse
from middlewares.error_handler import ErrorHandler
from routes import bot, accommodations
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = [
    "http://localhost:3000",
    "https://explore-sv-frontend.vercel.app",
    "https://exploresv-production.up.railway.app"
]

app.title = "Nutrition API - UTEC con DeepSeek V3"
app.version = "0.1.0"
app.description = "API para planes nutricionales con IA DeepSeek V3 en Azure"

# Middleware setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(ErrorHandler)

# Including routes
app.include_router(bot.bot_router)
app.include_router(accommodations.accommodations_router)

@app.get("/", tags=["Home"])
def message():
    return JSONResponse(
        content={"message": "Bienvenido a la API de Nutrición con DeepSeek V3"},
        status_code=status.HTTP_200_OK,
    )
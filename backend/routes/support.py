# routes/support.py
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from services.support import SupportService

support_router = APIRouter()
support_service = SupportService("doctores.json")  # tu nuevo JSON

@support_router.get("/support", tags=["Support"])
async def get_all_doctors():
    try:
        doctors = support_service.get_all()
        return JSONResponse(status_code=200, content=doctors)
    except Exception as e:
        return JSONResponse(status_code=500, content={"message": str(e)})
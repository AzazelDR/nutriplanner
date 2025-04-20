from fastapi import APIRouter
from fastapi.responses import JSONResponse
from services.support import SupportService

support_router = APIRouter()
support_service = SupportService("doctores.json")

@support_router.get("/support", tags=["Support"])
async def get_doctors():
    try:
        doctors = support_service.get_all()
        return JSONResponse(
            status_code=200,
            content={"message": "Doctors found", "data": doctors},
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"message": f"Internal Server Error: {e}"},
        )

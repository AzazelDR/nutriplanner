from fastapi import APIRouter
from fastapi.responses import JSONResponse
from services.accommodations import AccommodationService

accommodations_router = APIRouter()
accommodation_service = AccommodationService("accommodations.json")


@accommodations_router.get("/accommodation/{id}", tags=["Accommodations"])
async def get_accommodation(id: int):
    try:
        accommodation = accommodation_service.get_plan(id)

        # Check if the response contains an error message
        if "error" in accommodation:
            return JSONResponse(
                status_code=404,
                content={"message": accommodation["error"]},
            )

        # If no error, return the accommodation data
        return JSONResponse(
            status_code=200,
            content={"message": "Accommodation found", "data": accommodation},
        )

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"message": f"Internal Server Error: {e}"},
        )

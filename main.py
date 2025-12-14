from contextlib import asynccontextmanager
import json
from typing import List

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import uvicorn

class Hotel(BaseModel):
    id: int
    name: str
    address: str
    stars: float
    distance: float
    suites_availability: str


class HotelDetail(Hotel):
    image: str


hotels_db: List[Hotel] = []


@asynccontextmanager
async def lifespan(app: FastAPI):
    with open("hotels.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        for item in data:
            hotels_db.append(Hotel(**item))
    yield
    hotels_db.clear()


app = FastAPI(lifespan=lifespan)

app.mount("/Images", StaticFiles(directory="Images"), name="images")


@app.get("/hotels", response_model=List[Hotel])
async def get_hotels():
    """
    Returns a list of all hotels with summary information.
    """
    return hotels_db


@app.get("/hotels/{hotel_id}/details", response_model=HotelDetail)
async def get_hotel_details(hotel_id: int):
    """
    Returns the detailed information for a specific hotel.
    """
    try:
        with open(f"details/{hotel_id}.json", "r", encoding="utf-8") as f:
            hotel_details_data = json.load(f)
            return HotelDetail(**hotel_details_data)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Details for hotel with id {hotel_id} not found.")


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)

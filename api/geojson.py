import io, shutil, json
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
import config
from model.db import Rides

router = APIRouter()

some_file_path = "data/current-ride.geojson"
shutil.copy('data/default.geojson', 'data/current-ride.geojson') #ensure out current-ride.geojson is populated

@router.get("/")
async def get_current_ride_geojson():
    cur_ride = await Rides.objects.filter(active=True).get_or_none()
    
    if not cur_ride:
        return {"type": "FeatureCollection", "features": []}
    else:
        with open("data/current-ride.geojson", "r") as file:
            data = json.load(file)
            return data

@router.get("/file", )
async def get_current_ride_geojson_file():
    return FileResponse(some_file_path)


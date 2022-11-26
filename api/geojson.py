import io, shutil
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
import config
from model.db import Rides

router = APIRouter()

some_file_path = "data/current-ride.geojson"
shutil.copy('data/default.geojson', 'data/current-ride.geojson') #ensure out current-ride.geojson is populated

@router.get("/file", )
async def get_current_ride_geojson_file():
    return FileResponse(some_file_path)


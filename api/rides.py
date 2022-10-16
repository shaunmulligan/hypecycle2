from fastapi import APIRouter, HTTPException
from model.db import Rides

router = APIRouter()

@router.get("/current/", response_model=Rides)
async def get_current_ride():

    ride = await Rides.objects.filter(active=True).get_or_none()
    if not ride:
        raise HTTPException(status_code=404, detail="ride not found")
    return ride

@router.put("/current/stop", response_model=Rides)
async def stop_current_ride():
    cur_ride = await Rides.objects.filter(active=True).get_or_none()
    
    if not cur_ride:
        raise HTTPException(status_code=404, detail="ride not found")
    else:
        ride = await cur_ride.update(active=False) # TODO: add endtime stamp here
    return ride
from fastapi import APIRouter, HTTPException
from model.db import Rides, Gpsreadings
from lib.recorder.files import write_gpx_file

router = APIRouter()

@router.get("/summaries/")
async def get_rides_summaries():
    rides = await Rides.objects.all()
    summaries = []
    for ride in rides:
        if not ride.active:
            duration = (ride.end_time - ride.start_time).total_seconds()
            print(duration)
            distance = await ride.gpsreadingss.sum("distance_to_prev")
            up_hill = await ride.gpsreadingss.filter(Gpsreadings.height_to_prev > 0).sum("height_to_prev")
            avg_speed = await ride.gpsreadingss.avg("speed")
            avg_power = await ride.powerreadingss.avg("power")
            avg_hr = await ride.hrreadingss.avg("bpm")

            summary = ride.__dict__
            if not up_hill:
                up_hill = 0.0
            summary.update({"duration": duration, "distance": distance, "up_hill": up_hill, "avg_speed": avg_speed, "avg_power":avg_power, "avg_hr":avg_hr})
            print(summary)
            summaries.append(summary)
    return summaries

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
        ride = await cur_ride.update(active=False, end_time=datetime.now())

@router.post("/save/{ride_id}")
async def save_gpx(ride_id):
    return await write_gpx_file(ride_id)
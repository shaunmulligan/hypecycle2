import time
import board
import busio
import asyncio
from pa1010d import PA1010D


gps = PA1010D()

async def monitor_gps(state):
    loop = asyncio.get_running_loop()
    while True:
        result = await loop.run_in_executor(None, gps.update)
        if result:
            state.latitude = gps.latitude
            state.longitude = gps.longitude
            state.gps_altitude = gps.altitude
            state.fix_quality = gps.gps_qual
            state.location = {
                "latitude": gps.latitude,
                "longitude": gps.longitude,
            }
            state.latitude = gps.latitude
            state.longitude = gps.longitude
            state.speed = (gps.speed_over_ground*1.852000) if gps.speed_over_ground else 0.0 # Convert knots to km/h
        await asyncio.sleep(1.0)


if __name__ == "__main__":
    # Shared State
    hypecycleState = type('', (), {})()
    hypecycleState.gps_active = True
    asyncio.run(monitor_gps(hypecycleState))
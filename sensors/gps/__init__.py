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
    #         print("""
    # T: {timestamp}
    # N: {latitude}
    # E: {longitude}
    # Alt: {altitude}
    # Sats: {num_sats}
    # Qual: {gps_qual}
    # Speed: {speed_over_ground}
    # Fix Type: {mode_fix_type}
    # PDOP: {pdop}
    # VDOP: {vdop}
    # HDOP: {hdop}
    # """.format(**gps.data))
            state.latitude = gps.latitude
            state.longitude = gps.longitude
            state.gps_altitude = gps.altitude
            state.fix_quality = gps.gps_qual
            state.location = {
                "latitude": gps.latitude,
                "longitude": gps.longitude,
                "gps_time": gps.timestamp
            }
            state.speed = gps.speed_over_ground
        await asyncio.sleep(1.0)


if __name__ == "__main__":
    # Shared State
    hypecycleState = type('', (), {})()
    hypecycleState.gps_active = True
    asyncio.run(monitor_gps(hypecycleState))
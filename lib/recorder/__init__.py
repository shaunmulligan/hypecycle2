import asyncio
from model.db import Rides, Gpsreadings, Hrreadings, Powerreadings, Enviroreadings


async def monitor_recording(state, interval=1): 
    # Check if we have an active ride and if we do, write state to DB

    while True:
        active_ride = await Rides.objects.filter(active=True).get_or_none()
        if active_ride:
            print("Ride started at {}, recording data to DB".format(active_ride.start_time))
            location = Gpsreadings(ride_id=active_ride.id,latitude=state.latitude,longitude=state.longitude,speed=state.speed,altitude=state.altitude)
            hr_reading = Hrreadings(ride_id=active_ride.id, bpm=state.bpm)
            pow_reading = Powerreadings(ride_id=active_ride.id, power=state.instantaneous_power, cadence=state.cadence)
            env_reading = Enviroreadings(ride_id=active_ride.id, temp=state.temperature, altitude=state.altitude)
            await location.save()
            await hr_reading.save()
            await pow_reading.save()
            await env_reading.save()
        else:
            print("No active ride, so just chilling...")

        await asyncio.sleep(interval)
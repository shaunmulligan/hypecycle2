import asyncio
from model.db import Rides, Gpsreadings, Hrreadings, Powerreadings, Enviroreadings
from lib.recorder.files import generate_gpx

async def monitor_recording(state, interval=1): 
    # Check if we have an active ride and if we do, write state to DB

    while True:
        active_ride = await Rides.objects.filter(active=True).get_or_none()
        if active_ride:
            # print("Ride started at {}, recording data to DB".format(active_ride.start_time))
            location = Gpsreadings(ride_id=active_ride.id,latitude=state.latitude,longitude=state.longitude,speed=state.speed,altitude=state.gps_altitude)
            hr_reading = Hrreadings(ride_id=active_ride.id, bpm=state.bpm)
            pow_reading = Powerreadings(ride_id=active_ride.id, power=state.instantaneous_power, cadence=state.cadence)
            env_reading = Enviroreadings(ride_id=active_ride.id, temp=state.temperature, altitude=state.altitude)
            await location.save()
            await hr_reading.save()
            await pow_reading.save()
            await env_reading.save()
        # else:
        #     # print("No active ride, so just chilling...")

        await asyncio.sleep(interval)

async def monitor_averages(state, interval=60):
    # Calculate averages for the current ride and push them into state
    while True:
        active_ride = await Rides.objects.filter(active=True).get_or_none()
        if active_ride:
            gpx = await generate_gpx(active_ride.id) # TODO: this will probably be a bottleneck
            print("Distance: ", gpx.length_3d())
            state.distance = gpx.length_3d()
            moving_data = gpx.get_moving_data()
            if moving_data:
                print('Moving time: ', moving_data.moving_time)
                state.moving_time = moving_data.moving_time
                print('Stopped time: ', moving_data.stopped_time)
                state.stopped_time = moving_data.stopped_time
                print('Max speed: ' , moving_data.max_speed)
                state.max_speed = moving_data.max_speed
                print('Avg speed: ' , (moving_data.moving_distance / moving_data.moving_time) if moving_data.moving_time > 0 else "?")

                uphill, downhill = gpx.get_uphill_downhill()
                print('Total uphill: ', uphill)
                state.uphill = uphill
                print('Total downhill: ', downhill)
                state.downhill = downhill
        else:
            print("no active ride, so no averages to calc")

        await asyncio.sleep(interval)

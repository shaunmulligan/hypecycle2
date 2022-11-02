import asyncio
from datetime import datetime
from model.db import Rides, Gpsreadings, Hrreadings, Powerreadings, Enviroreadings
from lib.recorder.files import generate_gpx
from gpxpy import geo

import logging
logger = logging.getLogger(__name__)

async def monitor_recording(state, interval=1): 
    # Check if we have an active ride and if we do, write state to DB

    while True:
        active_ride = await Rides.objects.filter(active=True).get_or_none()
        if active_ride:
            prev_location = await Gpsreadings.objects.get_or_none() # Fetch the last location row from DB
            if not prev_location:
                distance_to_prev = 0
                height_to_prev = 0
            else:
                if state.fix_quality: # Only run the calculation if we have GPS fix, otherwise assume movement.
                    distance_to_prev = geo.distance(latitude_2=state.latitude, longitude_2=state.longitude, elevation_2=state.altitude, latitude_1=prev_location.latitude, longitude_1=prev_location.longitude, elevation_1=prev_location.altitude)
                    height_to_prev = state.altitude - prev_location.altitude
                else:
                    distance_to_prev = 0.0
                    height_to_prev = 0.0

            logger.debug("Distance to previous point: {}".format(distance_to_prev))
            logger.debug("Height from previous point: {}".format(height_to_prev))

            location = Gpsreadings(ride_id=active_ride.id,latitude=state.latitude,longitude=state.longitude,speed=state.speed,altitude=state.altitude, distance_to_prev=distance_to_prev, height_to_prev=height_to_prev)
            hr_reading = Hrreadings(ride_id=active_ride.id, bpm=state.bpm)
            pow_reading = Powerreadings(ride_id=active_ride.id, power=state.instantaneous_power, cadence=state.cadence)
            env_reading = Enviroreadings(ride_id=active_ride.id, temp=state.temperature, altitude=state.altitude)
            await location.save()
            await hr_reading.save()
            await pow_reading.save()
            await env_reading.save()
            time_delta = datetime.now() - active_ride.start_time
            state.elapsed_time = time_delta.total_seconds()

        await asyncio.sleep(interval)

async def monitor_averages(state, interval=60):
    # Calculate averages for the current ride and push them into state
    while True:
        active_ride = await Rides.objects.filter(active=True).get_or_none()
        if active_ride:
            gpx = await generate_gpx(active_ride.id) # TODO: this will probably be a bottleneck
            gps_data = await Gpsreadings.objects.filter(ride_id=active_ride.id).all()
            gps_distance_and_height = await Gpsreadings.objects.filter(ride_id=active_ride.id).sum(["distance_to_prev","height_to_prev"])
            logger.info("GPS db distance: {}".format(gps_distance_and_height["distance_to_prev"]))
            logger.info("GPS db height: {}".format(gps_distance_and_height["height_to_prev"]))
            
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

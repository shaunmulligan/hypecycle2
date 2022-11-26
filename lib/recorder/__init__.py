import asyncio, json
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
            logger.debug("Active Ride ID: {}".format(active_ride.id))
            prev_location = await active_ride.gpsreadingss.order_by(Gpsreadings.id.desc()).limit(1).get_or_none() # Fetch the last location row from DB if it exists
            if not prev_location:
                logger.debug("No previous location for this ride")
                distance_to_prev = 0.0
                height_to_prev = 0.0
            else:
                if state.fix_quality: # Only run the calculation if we have GPS fix, otherwise assume no movement.
                    distance_to_prev = geo.distance(latitude_2=state.latitude, longitude_2=state.longitude, elevation_2=state.altitude, latitude_1=prev_location.latitude, longitude_1=prev_location.longitude, elevation_1=prev_location.altitude)
                    if distance_to_prev > 50 or distance_to_prev <1: # if we have moved more than 50m in 1 second, we are moving at > 180km/h, so assume GPS issues and that we aren't moving. Also if less than 3.5km/h
                        distance_to_prev = 0.0
                    height_to_prev = state.altitude - (prev_location.altitude if prev_location.altitude else 0)
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

            def hook(obj): #This hooks in and appends latlong into our current ride geojson file
                if 'coordinates' in obj:
                    points = obj["coordinates"]
                    if obj['type'] == 'LineString':
                        points.append([state.longitude, state.latitude])
                return obj

            data = None
            with open("data/current-ride.geojson", "r") as file:
                data = json.load(file, object_hook=hook)
            with open("data/current-ride.geojson", "w") as file:
                json.dump(data, file, indent=4)

        await asyncio.sleep(interval)

async def monitor_averages(state, interval=10):
    # Calculate averages for the current ride and push them into state
    while True:
        active_ride = await Rides.objects.filter(active=True).get_or_none()
        if active_ride:
            gps_distance = await Gpsreadings.objects.filter(ride_id=active_ride.id).sum("distance_to_prev")
            gps_up_hill = await active_ride.gpsreadingss.filter(Gpsreadings.height_to_prev > 0).sum("height_to_prev")
            gps_down_hill = await active_ride.gpsreadingss.filter(Gpsreadings.height_to_prev < 0).sum("height_to_prev")
            
            max_speed = await active_ride.gpsreadingss.max("speed")
            avg_speed = await active_ride.gpsreadingss.avg("speed")
            max_altitude = await active_ride.gpsreadingss.max("altitude")
            avg_power = await active_ride.powerreadingss.avg("power")
            max_power = await active_ride.powerreadingss.max("power")
            avg_hr = await active_ride.hrreadingss.avg("bpm")
            max_hr = await active_ride.hrreadingss.max("bpm")
            avg_temp = await active_ride.enviroreadingss.avg("temp")
            max_temp = await active_ride.enviroreadingss.max("temp")
            
            # Log averages
            logger.info("Uphill = {}".format(gps_up_hill))
            logger.info("Downhill = {}".format(gps_down_hill))
            logger.info("GPS db distance: {}".format(gps_distance))
            logger.info("Speed: max = {}, avg = {}".format(max_speed, avg_speed))
            logger.info("Max Altitude = {}".format(max_altitude))
            logger.info("Heart Rate: max  = {}, avg = {}".format(max_hr, avg_hr))
            logger.info("Temperature: max = {}, avg = {}".format(max_temp, avg_temp))
            
            # Push into state
            state.distance = gps_distance
            state.max_speed = max_speed
            state.avg_speed = avg_speed
            state.uphill = gps_up_hill
            state.downhill = gps_down_hill
            state.max_altitude = max_altitude
            state.avg_power = avg_power
            state.max_power = max_power
            state.avg_hr = avg_hr
            state.max_hr = max_hr
            state.avg_temp = avg_temp
            state.max_temp = max_temp
        else:
            logger.info("no active ride, so no averages to calc")

        await asyncio.sleep(interval)

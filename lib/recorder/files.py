import asyncio
from model.db import Rides, Gpsreadings, Hrreadings, Powerreadings, Enviroreadings

import gpxpy
import gpxpy.gpx
from datetime import datetime
from xml.etree import ElementTree

def get_point(lat, lon, ele, power, temp, hr, cadence, time):
    # Create point:
    gpx_point = gpxpy.gpx.GPXTrackPoint(lat, lon, elevation=ele, time=time)
    gpx_extension_power = ElementTree.fromstring(f"""<power>{power}</power>""")
    gpx_extension_hr = ElementTree.fromstring(f"""<gpxtpx:TrackPointExtension xmlns:gpxtpx="http://www.garmin.com/xmlschemas/TrackPointExtension/v1">
        <gpxtpx:atemp>{temp}</gpxtpx:atemp>
        <gpxtpx:hr>{hr}</gpxtpx:hr>
        <gpxtpx:cad>{cadence}</gpxtpx:cad>
        </gpxtpx:TrackPointExtension>
    """)
    gpx_point.extensions.append(gpx_extension_power)
    gpx_point.extensions.append(gpx_extension_hr)
    return gpx_point

async def generate_gpx(id):
    """Generate GPX file from a ride in the DB"""
    print("Saving GPX file for ride {}".format(id))
    loc = await Gpsreadings.objects.filter(ride_id=id).all()
    hr = await Hrreadings.objects.filter(ride_id=id).all()
    power = await Powerreadings.objects.filter(ride_id=id).all()
    enviro = await Enviroreadings.objects.filter(ride_id=id).all()

    gpx = gpxpy.gpx.GPX()
    # Add TrackPointExtension namespace
    gpx.nsmap["gpxtpx"] = "http://www.garmin.com/xmlschemas/TrackPointExtension/v1"
    # Create track
    gpx_track = gpxpy.gpx.GPXTrack()
    gpx.tracks.append(gpx_track)
    # Create segment
    gpx_segment = gpxpy.gpx.GPXTrackSegment()
    gpx_track.segments.append(gpx_segment)

    for x in range(len(loc)):
        point = get_point(loc[x].latitude,loc[x].longitude, loc[x].altitude, power[x].power, enviro[x].temp, hr[x].bpm, power[x].cadence, loc[x].timestamp)
        gpx_segment.points.append(point)
    
    # Create GPX file with current datetime
    filename = "data/" + datetime.now().strftime("%Y_%m_%d-%I_%M_%S_%p") + ".gpx"
    with open(filename, "w") as f:
        f.write( gpx.to_xml())
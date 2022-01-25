#!/usr/bin/env python3
import sys
import asyncio
from icp10125 import ICP10125
import aiohttp, json
from aiohttp_requests import requests

"""QNH for calculating altitude.
This value is the atmospheric pressure reference used to calculate altitude.
The default value is 1031.0, but you *must* get a value from your local airport
or weather reports for a remotely accurate altitude!
"""
QNH = 1031.0

def calculate_altitude(pressure, qnh=1013.25):
    return 44330.0 * (1.0 - pow(pressure / qnh, (1.0 / 5.255)))

async def get_weather():
    api_key = "API_KEY_HERE"
    lat = "41.272203"
    lon = "2.154527"
    url = "https://api.openweathermap.org/data/2.5/onecall?lat=%s&lon=%s&appid=%s&units=metric&exclude=minutely,hourly,daily" % (lat, lon, api_key)
    response = await requests.get(url)
    text = await response.text()
    json = await response.json()
    print(json)
    return json

try:
    device = ICP10125()
except OSError:
    print("ERROR: No alitimeter device found!")

async def main():
    try:
        pressure, temperature = await asyncio.to_thread(device.measure)
        weather = await get_weather()
        altitude = calculate_altitude(pressure / 100, qnh=weather["current"]["pressure"])
        print(f"""Pressure: {pressure / 100:.2f}hPa
        Temperature: {temperature:.4f}c
        Altitude:    {altitude:.4f}m
        """)
    except (OSError, NameError) as e:
        print("ERROR: Couldn't read Altimeter sensor")

asyncio.run(main())
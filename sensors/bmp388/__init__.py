#!/usr/bin/env python3
import os
os.environ["BLINKA_U2IF"] = "0"
import time
import asyncio
import board
# import adafruit_bmp3xx

# I2C setup
i2c = board.I2C()  # uses board.SCL and board.SDA
bmp = adafruit_bmp3xx.BMP3XX_I2C(i2c)

bmp.pressure_oversampling = 8
bmp.temperature_oversampling = 2

async def monitor_pressure_temp(state):
    
    # change this to match the location's pressure (hPa) at sea level
    bmp.sea_level_pressure = 1017.0

    while True:
        print("\nTemperature: %0.1f C" % (bmp.temperature ))
    
        print("Pressure: %0.3f hPa" % bmp.pressure)
        print("Altitude = %0.2f meters" % bmp.altitude)
        state.temperature = bmp.temperature
        state.pressure = bmp.pressure
        state.altitude = bmp.altitude
        await asyncio.sleep(10)
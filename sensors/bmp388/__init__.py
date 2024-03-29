#!/usr/bin/env python3
import os
import time
import asyncio
import board
import adafruit_bmp3xx
import logging
logger = logging.getLogger(__name__)

loop = asyncio.get_running_loop()
# I2C setup
i2c = board.I2C()  # uses board.SCL and board.SDA
bmp = adafruit_bmp3xx.BMP3XX_I2C(i2c)

# The below are probably sync calls, TODO: wrap them
bmp.pressure_oversampling = 8
bmp.temperature_oversampling = 2

async def monitor_pressure_temp(state):

    # change this to match the location's pressure (hPa) at sea level
    sea_level_pressure = 1021.8
    logger.info("Altitude monitoring has started, sea level pressure set at {} hpa".format(sea_level_pressure))
    while True:
        pressure, temp = await loop.run_in_executor(None, bmp._read)
        pressure = pressure/100
        altitude = 44307.7 * (1 - (pressure / sea_level_pressure) ** 0.190284)
        logger.debug("\nTemperature: {} C".format(temp))
        logger.debug("Pressure: {} hPa".format(pressure))
        logger.info("Altitude = {} meters".format(altitude))
        state.temperature = temp
        state.pressure = pressure
        state.altitude = altitude
        await asyncio.sleep(10)
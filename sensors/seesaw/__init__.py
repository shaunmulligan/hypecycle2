#!/usr/bin/env python3
import time, shutil
import asyncio
from datetime import datetime
import board
from adafruit_seesaw.seesaw import Seesaw
from adafruit_seesaw import neopixel
from adafruit_seesaw.analoginput import AnalogInput
from adafruit_seesaw.digitalio import DigitalIO
import digitalio

import gpxpy
import gpxpy.gpx

import randomname

from model.db import Rides, Settings
from lib.recorder.files import write_gpx_file
import config

import logging
logger = logging.getLogger(__name__)

WHITE = (255,255,255)
OFF = (0,0,0)

i2c = board.I2C()  # uses board.SCL and board.SDA
ss = Seesaw(i2c)

ONBOARD_LED_PIN = 5
BATTERY_ADC_PIN = 2
NEOPIXEL_PIN = 19  # Can be any pin
NEOPIXEL_NUM = 8  # No more than 60 pixels!
BTN_1 = DigitalIO(ss, 1)
BTN_2 = DigitalIO(ss, 2)
BTN_3 = DigitalIO(ss, 3)
BTN_1.direction = digitalio.Direction.INPUT
BTN_1.pull = digitalio.Pull.UP
BTN_2.direction = digitalio.Direction.INPUT
BTN_2.pull = digitalio.Pull.UP
BTN_3.direction = digitalio.Direction.INPUT
BTN_3.pull = digitalio.Pull.UP

loop = asyncio.get_running_loop()

def button(id):
    return id.value

async def monitor_buttons(state):
    start_pause_last = 1
    stop_last = 1
    button_3_last = 1

    while True:
        
        start_pause = await loop.run_in_executor(None, button, BTN_1)
        stop = await loop.run_in_executor(None, button, BTN_2)
        button_3 = await loop.run_in_executor(None, button, BTN_3)

        if start_pause != start_pause_last:
            logger.info("Start/Pause Button has been {}".format("released" if start_pause else "pressed"))
            start_pause_last = start_pause
            if not start_pause:
                state.ride_paused = not state.ride_paused # Toggle the paused state
            await asyncio.sleep(1.0 / 30)
        elif stop != stop_last:
            logger.info("Stop Button has been {}".format("released" if stop else "pressed"))
            stop_last = stop
            if not stop:
                # Get current active ride if it exists
                cur_ride = await Rides.objects.filter(active=True).get_or_none()
                if cur_ride:
                    # Change ride active state to false
                    ride = await cur_ride.update(active=False, end_time=datetime.now())
                    logger.info("Stop ride requested by button press...")
                    state.elapsed_time = 0
                    state.distance = 0.0
                    # Generate and save GPX file.
                    f = await write_gpx_file(ride.id)
                    logger.info("Saved ride to file named {}".format(f))
                    #reset geojson file to default
                    shutil.copy('data/default.geojson', 'data/current-ride.geojson')
                else:
                    logger.info("No active ride to stop... so starting a new ride")
                    # Create a new ride 
                    ride_name = randomname.get_name()
                    ride = Rides(name=ride_name)
                    # TODO: we probably need to abstract "new ride" into its own thing
                    
                    await ride.save()

            await asyncio.sleep(1.0 / 30)
        elif button_3 != button_3_last:
            logger.info("Button 3 has been {}".format("released" if button_3 else "pressed"))
            button_3_last = button_3
            await asyncio.sleep(1.0 / 30)

async def monitor_battery(state):
    last_adc = 0.00
    
    while True:
        adc = await loop.run_in_executor(None, AnalogInput, ss, BATTERY_ADC_PIN)
        print(adc.value)
        adc = round(((adc.value*3.3)/1024),4)

        if adc != last_adc:
            logger.info("{:.4f}v".format(adc))
            state.battery_level = adc
            last_adc = adc

        await asyncio.sleep(60.0)

def lights(pixels, value):
    if value:
        pixels.fill(OFF)
    else:
        pixels.fill(WHITE)
    
    pixels.show()

async def lights_task(state):
    pixels = neopixel.NeoPixel(ss, NEOPIXEL_PIN, NEOPIXEL_NUM)
    pixels.brightness = 1  # Not so bright!
    out_value = 0
    while True: # Loop to keep lights_task alive
        while (await Settings.objects.filter(id=1).get_or_none()).lights_enabled:
            logger.debug("LED value is {}".format(out_value))
            await loop.run_in_executor(None, lights, pixels, out_value)
            out_value = not out_value
            await asyncio.sleep(0.5)
        await asyncio.sleep(2)


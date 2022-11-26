#!/usr/bin/env python3
import time, shutil
import asyncio
from datetime import datetime
import ioexpander as io

import gpxpy
import gpxpy.gpx

import randomname

from model.db import Rides, Settings
from lib.recorder.files import write_gpx_file
import config

import logging
logger = logging.getLogger(__name__)

BTN_1 = 14
BTN_2 = 12
BTN_3 = 10
LED_1 = 1

ioe = io.IOE(i2c_addr=0x18)

# Button Inputs
ioe.set_mode(BTN_1, io.IN_PU)
ioe.set_mode(BTN_2, io.IN_PU)
ioe.set_mode(BTN_3, io.IN_PU)
ioe.set_mode(LED_1, io.OUT)

# Analog inputs
ioe.set_adc_vref(3.3)  # Input voltage of IO Expander, this is 3.3 on Breakout Garden
ioe.set_mode(13, io.ADC)

loop = asyncio.get_running_loop()

async def monitor_buttons(state):
    start_pause_last = io.HIGH
    stop_last = io.HIGH
    button_3_last = io.HIGH

    while True:
        
        start_pause = await loop.run_in_executor(None, ioe.input, BTN_1)
        stop = await loop.run_in_executor(None, ioe.input, BTN_2)
        button_3 = await loop.run_in_executor(None, ioe.input, BTN_3)

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
        adc = await loop.run_in_executor(None, ioe.input, 13)
        adc = round(adc,4)

        if adc != last_adc:
            logger.info("{:.4f}v".format(adc))
            state.battery_level = adc
            last_adc = adc

        await asyncio.sleep(60.0)

async def lights_task(state):
    out_value = 0
    while True: # Loop to keep lights_task alive
        while (await Settings.objects.filter(id=1).get_or_none()).lights_enabled:
            logger.debug("LED value is {}".format(out_value))
            await loop.run_in_executor(None, ioe.output, LED_1, out_value)
            out_value = not out_value
            await asyncio.sleep(0.5)
        await asyncio.sleep(2)

if __name__ == "__main__":
    last_value = io.HIGH
    while True:
        value = ioe.input(BTN_1)
        if value != last_value:
            logger.info("Button has been {}".format("released" if value else "pressed"))
            last_value = value

        time.sleep(1.0 / 30)

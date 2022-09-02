#!/usr/bin/env python3
import time
import asyncio
import ioexpander as io

from model.db import Rides

BTN_1 = 14
BTN_2 = 12
BTN_3 = 10

ioe = io.IOE(i2c_addr=0x18)

# Button Inputs
ioe.set_mode(BTN_1, io.IN_PU)
ioe.set_mode(BTN_2, io.IN_PU)
ioe.set_mode(BTN_3, io.IN_PU)

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
            print("Start/Pause Button has been {}".format("released" if start_pause else "pressed"))
            start_pause_last = start_pause
            await asyncio.sleep(1.0 / 30)
        elif stop != stop_last:
            print("Stop Button has been {}".format("released" if stop else "pressed"))
            stop_last = stop
            await asyncio.sleep(1.0 / 30)
        elif button_3 != button_3_last:
            print("Button 3 has been {}".format("released" if button_3 else "pressed"))
            button_3_last = button_3
            await asyncio.sleep(1.0 / 30)

async def monitor_battery(state):
    last_adc = 0.00

    while True:
        adc = await loop.run_in_executor(None, ioe.input, 13)
        adc = round(adc,2)

        if adc != last_adc:
            print("{:.2f}v".format(adc))
            state.battery_level = adc
            last_adc = adc

        await asyncio.sleep(60)

if __name__ == "__main__":
    last_value = io.HIGH
    while True:
        value = ioe.input(BTN_1)
        if value != last_value:
            print("Button has been {}".format("released" if value else "pressed"))
            last_value = value

        time.sleep(1.0 / 30)

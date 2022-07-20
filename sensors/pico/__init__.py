print("loading pico lib")
import os
os.environ["BLINKA_U2IF"] = "1"
import asyncio
print("loading board")
import board
print("loading digitalio")
import digitalio
print("loading keypad")
import keypad
print("loading analogio")
import analogio

print("pico dep libs loaded")
from model.db import Rides
print("everything loaded for pico")

def get_voltage(raw):
    return ((raw * 2.1) / 65536) * 2

async def monitor_buttons(state):
    """Monitor 3 buttons: 
    """
    # Assume buttons are active low.
    pin_start_pause = board.GP18 
    pin_stop = board.GP17
    pin_three = board.GP16

    with keypad.Keys(
        (pin_start_pause, pin_stop, pin_three), value_when_pressed=False, pull=True
    ) as keys:
        while True:
            key_event = keys.events.get()
            if key_event and key_event.pressed:
                if key_event.key_number == 0:
                    print("Start/Pause button pressed")
                    state.ride_paused = not state.ride_paused # Toggle the paused state
                elif key_event.key_number == 1:
                    print("Stop button pressed")
                    # Get current active ride if it exists
                    cur_ride = await Rides.objects.filter(active=True).get_or_none()
                    if cur_ride:
                        # Change ride active state to false
                        ride = await cur_ride.update(active=False)
                        print("Stop ride requested by button press...")
                    else:
                        print("No active ride to stop...")
                else:
                    print("Button 3 pressed")
            # Let another task run.
            await asyncio.sleep(0)

async def monitor_battery_level(state):
    battery = analogio.AnalogIn(board.ADC0)
    while True:
        MAX_V = 4.2
        raw = battery.value
        volts = get_voltage(raw)
        level = (volts/MAX_V)*100
        print("raw = {:5d} volts = {:5.2f} level = {:5.2f}".format(raw, volts, level))
        state.battery_voltage = volts
        state.battery_level = level
        await asyncio.sleep(60)

print("pico: EOF")
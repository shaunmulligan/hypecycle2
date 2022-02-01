import os
os.environ["BLINKA_U2IF"] = "1"
import asyncio
import board
import digitalio
import keypad
import analogio
import adafruit_bme680
import busio

from model.db import Rides

battery = analogio.AnalogIn(board.ADC0)

def get_voltage(raw):
    return ((raw * 2.1) / 65536) * 2

async def monitor_buttons(state, stop_event):
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
    while True:
        MAX_V = 4.2
        raw = battery.value
        volts = get_voltage(raw)
        level = (volts/MAX_V)*100
        print("raw = {:5d} volts = {:5.2f} level = {:5.2f}".format(raw, volts, level))
        state.battery_voltage = volts
        state.battery_level = level
        await asyncio.sleep(60)

async def monitor_pressure_temp(state):
    i2c = busio.I2C(scl=board.GP15, sda=board.GP14) # uses board.SCL and board.SDA
    
    # To initialise using the default address:
    bme680 = adafruit_bme680.Adafruit_BME680_I2C(i2c, 0x76)
    
    # change this to match the location's pressure (hPa) at sea level
    bme680.sea_level_pressure = 1024.0
    
    # You will usually have to add an offset to account for the temperature of
    # the sensor. This is usually around 5 degrees but varies by use. Use a
    # separate temperature sensor to calibrate this one.
    temperature_offset = -5
    
    while True:
        print("\nTemperature: %0.1f C" % (bme680.temperature + temperature_offset))
        print("Gas: %d ohm" % bme680.gas)
        print("Humidity: %0.1f %%" % bme680.relative_humidity)
        print("Pressure: %0.3f hPa" % bme680.pressure)
        print("Altitude = %0.2f meters" % bme680.altitude)
        state.temperature = bme680.temperature
        state.pressure = bme680.pressure
        state.altitude = bme680.altitude
        await asyncio.sleep(10)

# async def main():
#     # Start blinking 0.5 sec on, 0.5 sec off.
#     interval = Interval(0.5)

#     led_task = asyncio.create_task(blink(board.GP19, interval))
#     battery_task = asyncio.create_task(monitor_battery_level())
#     interval_task = asyncio.create_task(
#         monitor_interval_buttons(board.GP18, board.GP17, board.GP16, interval)
#     )
#     enviro_task = asyncio.create_task(monitor_pressure_temp())
#     # This will run forever, because neither task ever exits.
#     await asyncio.gather(led_task, interval_task)
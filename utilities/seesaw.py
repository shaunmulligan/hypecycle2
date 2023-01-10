
import board
import asyncio
from adafruit_seesaw.seesaw import Seesaw
from adafruit_seesaw import neopixel
from adafruit_seesaw.analoginput import AnalogInput
from rainbowio import colorwheel

import logging
logger = logging.getLogger(__name__)

i2c = board.I2C()  # uses board.SCL and board.SDA
ss = Seesaw(i2c)

ONBOARD_LED_PIN = 5
BATTERY_ADC_PIN = 2
NEOPIXEL_PIN = 19  # Can be any pin
NEOPIXEL_NUM = 8  # No more than 60 pixels!

# Onboard LED pin
ss.pin_mode(ONBOARD_LED_PIN, ss.OUTPUT)

async def monitor_battery_voltage():

    while True:
        # Read the voltage of the battery connected to the ADC.
        battery_voltage = AnalogInput(ss, BATTERY_ADC_PIN)
        logger.info(f'Battery voltage: {battery_voltage.value}')

        # Sleep for 1 second before reading the voltage again.
        await asyncio.sleep(1)

RED = (255, 0, 0)
YELLOW = (255, 150, 0)
GREEN = (0, 255, 0)
CYAN = (0, 255, 255)
BLUE = (0, 0, 255)
PURPLE = (180, 0, 255)
WHITE = (255,255,255)
OFF = (0,0,0)

async def lights_task():
    pixels = neopixel.NeoPixel(ss, NEOPIXEL_PIN, NEOPIXEL_NUM)
    pixels.brightness = 1  # Not so bright!
    while True: # Loop to keep lights_task alive
        pixels.fill(OFF)
        pixels.show()
        await asyncio.sleep(1)
        pixels.fill(WHITE)
        pixels.show()
        await asyncio.sleep(1)

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(lights_task())
    loop.run_forever()
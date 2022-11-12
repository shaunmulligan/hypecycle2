import asyncio
from typing import List
from collections import deque
import backoff
from bleak import BleakClient, BleakScanner
from bleak.backends.device import BLEDevice
from bleak.exc import BleakError
from pycycling.heart_rate_service import HeartRateService
from pycycling.cycling_power_service import CyclingPowerService
from pycycling.cycling_speed_cadence_service import CyclingSpeedCadenceService

import logging
logger = logging.getLogger(__name__)

class HrSensor(object):
    """ HRM BLE sensor class """
    async def __aenter__(self):
        print('__aenter__ for HrSensor')

    async def __aexit__(self, *_):
        print('__aexit__ Clean up for HrSensor')
        self.client.disconnect()
        asyncio.sleep(5)
        
    def __init__(self, state, address):
        self.state = state
        self.address = address
        self.type = None
        self.asyncio_loop = None
        self.client = None
        self.hr_service = None

    # @backoff.on_exception(backoff.constant, (BleakError, asyncio.exceptions.TimeoutError), interval=5)
    async def start(self, sensor_active):
        self.asyncio_loop = asyncio.get_event_loop()
        logger.info("starting HR sensor monitor loop on {}".format(self.address))
        def disconnect_handler(client):
            logger.info("Heartrate Monitor disconnected!")
            self.state.hr_available = False

        async with BleakClient(self.address, loop=self.asyncio_loop, timeout=10.0, disconnected_callback=disconnect_handler) as client:
            # Set the instance client so we can clean up later.
            self.client = client
            
            def my_measurement_handler(data):   
                logger.debug("Heart Rate: {} bpm".format(data.bpm))
                self.state.bpm = data.bpm

            while not client.is_connected:
                logger.info("Attemptint to connect to HRM")
                await asyncio.sleep(1)

            logger.info("Heart Rate Monitor Connected!")
            self.state.hr_available = True

            self.hr_service = HeartRateService(client)
            self.hr_service.set_hr_measurement_handler(my_measurement_handler)

            await self.hr_service.enable_hr_measurement_notifications()
            
            while sensor_active and client.is_connected:
                await asyncio.sleep(2)

    async def stop(self):
        await self.hr_service.disable_hr_measurement_notifications()
        await self.client.disconnect()

class PowerSensor(object):
    """ Power BLE sensor class """
    async def __aenter__(self):
        print('__aenter__ for PowerSensor')

    async def __aexit__(self, *_):
        print('__aexit__ Clean up for PowerSensor')
        self.client.disconnect()
        asyncio.sleep(5)

    def __init__(self, state, address):
        self.state = state
        self.address = address
        self.type = None
        self.asyncio_loop = None
        self.client = None
        self.power_service = None
        self.previous_crank_revs = 0
        self.previous_crank_event_time = 0

    # @backoff.on_exception(backoff.constant, (BleakError, asyncio.exceptions.TimeoutError), interval=5)
    async def start(self, sensor_active):
        self.asyncio_loop = asyncio.get_event_loop()
        logger.info("starting Power sensor monitor loop on {}".format(self.address))

        def disconnect_handler(client):
            logger.info("Power Meter disconnected!")
            self.state.power_available = False
    
        async with BleakClient(self.address, loop=self.asyncio_loop, timeout=5.0) as client:
            # Set the instance client so we can clean up later.
            self.client = client
            pw3s = deque([0]*3,maxlen=3) # array to record last 3 seconds of power
            pw10s = deque([0]*10,maxlen=10) # array to record last 10 seconds of power // TODO: probably a cleaner way to do these two together

            def my_power_handler(data):
                current_crank_revs = data.cumulative_crank_revs
                current_crank_event_time = data.last_crank_event_time

                logger.debug("Instantaneous Power: {} Watts".format(data.instantaneous_power))

                time_diff = (current_crank_event_time - self.previous_crank_event_time)*(1/1024)
                if time_diff != 0:
                    rps = (current_crank_revs - self.previous_crank_revs)/time_diff
                    cadence = rps*60
                else:
                    cadence = 0
                self.previous_crank_event_time = current_crank_event_time
                self.previous_crank_revs = current_crank_revs

                logger.debug("cadence: {}".format(cadence))
                pw10s.appendleft(data.instantaneous_power)
                pw3s.appendleft(data.instantaneous_power)
                self.state.power10s = sum(pw10s)/10
                self.state.power3s = sum(pw3s)/3
                self.state.instantaneous_power = data.instantaneous_power
                self.state.cadence = cadence

            while not client.is_connected:
                logger.info("Attempting to connect to Powermeter")
                await asyncio.sleep(1)
            # Setup Power
            self.state.power_available = True
            logger.info("Powermeter connected!")
            self.power_service = CyclingPowerService(client)
            self.power_service.set_cycling_power_measurement_handler(my_power_handler)
            await self.power_service.enable_cycling_power_measurement_notifications()

            while sensor_active and client.is_connected:
                logger.debug("Reading Power and Cadence")
                await asyncio.sleep(10)

    async def stop(self):
        await self.power_service.disable_cycling_power_measurement_notifications()
        await self.client.disconnect()

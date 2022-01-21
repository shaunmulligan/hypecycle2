import asyncio
import random
from bleak import BleakClient
from pycycling.heart_rate_service import HeartRateService

class HrSensor(object):
    """ HRM BLE sensor class """
    def __init__(self, state, address):
        self.state = state
        self.address = address
        self.type = None
        self.asyncio_loop = None
        self.client = None
        self.hr_service = None

    async def start(self, sensor_active):
        self.asyncio_loop = asyncio.get_event_loop()
        print("starting HR sensor monitor loop on ", self.address)
    
        async with BleakClient(self.address, loop=self.asyncio_loop, timeout=20.0) as self.client:
            
            def my_measurement_handler(data):   
                # print("Heart Rate: ",data.bpm)
                self.state.bpm = data.bpm

            self.hr_service = HeartRateService(self.client)
            self.hr_service.set_hr_measurement_handler(my_measurement_handler)

            await self.hr_service.enable_hr_measurement_notifications()
            while sensor_active:
                # print("Reading HRM")
                await asyncio.sleep(10)

    async def stop(self):
        await self.hr_service.disable_hr_measurement_notifications()
        self.client.disconnect()

class PowerSensor(object):
    """ Power BLE sensor class """
    # Todo: 
    pass
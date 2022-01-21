import asyncio
import random
from bleak import BleakClient
from pycycling.heart_rate_service import HeartRateService
from pycycling.cycling_power_service import CyclingPowerService

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
    def __init__(self, state, address):
        self.state = state
        self.address = address
        self.type = None
        self.asyncio_loop = None
        self.client = None
        self.power_service = None

    async def start(self, sensor_active):
        self.asyncio_loop = asyncio.get_event_loop()
        print("starting Power sensor monitor loop on ", self.address)
    
        async with BleakClient(self.address, loop=self.asyncio_loop, timeout=20.0) as self.client:
            
            def my_measurement_handler(data):   
                print("Instantaneous Power: ", data.instantaneous_power)
                self.state.instantaneous_power = data.instantaneous_power

            await self.client.is_connected()
            self.power_service = CyclingPowerService(self.client)
            self.power_service.set_cycling_power_measurement_handler(my_measurement_handler)
            await self.power_service.enable_cycling_power_measurement_notifications()
            while sensor_active:
                # print("Reading Power")
                await asyncio.sleep(10)

    async def stop(self):
        await self.power_service.disable_cycling_power_measurement_notifications()
        self.client.disconnect()

# Tacx Neo 2T output
#CyclingPowerMeasurement(instantaneous_power=0, accumulated_energy=None, pedal_power_balance=None, accumulated_torque=None, cumulative_wheel_revs=165, last_wheel_event_time=0, cumulative_crank_revs=0, last_crank_event_time=0, maximum_force_magnitude=None, minimum_force_magnitude=None, maximum_torque_magnitude=None, minimum_torque_magnitude=None, top_dead_spot_angle=None, bottom_dead_spot_angle=None)
# 4iii powermeter output
#CyclingPowerMeasurement(instantaneous_power=10, accumulated_energy=None, pedal_power_balance=None, accumulated_torque=66, cumulative_wheel_revs=None, last_wheel_event_time=None, cumulative_crank_revs=7, last_crank_event_time=11248, maximum_force_magnitude=None, minimum_force_magnitude=None, maximum_torque_magnitude=None, minimum_torque_magnitude=None, top_dead_spot_angle=None, bottom_dead_spot_angle=None)
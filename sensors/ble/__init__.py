import asyncio
from typing import List
import backoff
from bleak import BleakClient, BleakScanner
from bleak.backends.device import BLEDevice
from bleak.exc import BleakError
from pycycling.heart_rate_service import HeartRateService
from pycycling.cycling_power_service import CyclingPowerService
from pycycling.cycling_speed_cadence_service import CyclingSpeedCadenceService

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
        print("starting HR sensor monitor loop on ", self.address)
        def disconnect_handler(client):
            print("Heartrate Monitor disconnected")
            self.state.hr_available = False

        async with BleakClient(self.address, loop=self.asyncio_loop, timeout=10.0, disconnected_callback=disconnect_handler) as client:
            # Set the instance client so we can clean up later.
            self.client = client
            
            def my_measurement_handler(data):   
                print("Heart Rate: ",data.bpm)
                self.state.bpm = data.bpm

            while not client.is_connected:
                print("trying to connect to HRM")
                await asyncio.sleep(1)
            print("Heart Rate Monitor Connected")
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
        print("starting Power sensor monitor loop on ", self.address)
        def disconnect_handler(client):
            print("Power Meter disconnected")
            self.state.power_available = False
    
        async with BleakClient(self.address, loop=self.asyncio_loop, timeout=5.0) as client:
            # Set the instance client so we can clean up later.
            self.client = client

            def my_power_handler(data):
                current_crank_revs = data.cumulative_crank_revs
                current_crank_event_time = data.last_crank_event_time
                print("Instantaneous Power: ", data.instantaneous_power)
                # print("cumulative_crank_revs: ", data.cumulative_crank_revs)
                # print("last_crank_event_time: ", data.last_crank_event_time)
                time_diff = (current_crank_event_time - self.previous_crank_event_time)*(1/1024)
                if time_diff != 0:
                    rps = (current_crank_revs - self.previous_crank_revs)/time_diff
                    cadence = rps*60
                else:
                    cadence = 0
                self.previous_crank_event_time = current_crank_event_time
                self.previous_crank_revs = current_crank_revs

                print("cadence: ", cadence)
                self.state.instantaneous_power = data.instantaneous_power
                self.state.cadence = cadence

            while not client.is_connected:
                print("trying to connect to powermeter")
                await asyncio.sleep(1)
            # Setup Power
            self.state.power_available = True
            print("Powermeter connected!")
            self.power_service = CyclingPowerService(client)
            self.power_service.set_cycling_power_measurement_handler(my_power_handler)
            await self.power_service.enable_cycling_power_measurement_notifications()

            while sensor_active and client.is_connected:
                # print("Reading Power and Cadence")
                await asyncio.sleep(10)

    async def stop(self):
        await self.power_service.disable_cycling_power_measurement_notifications()
        await self.client.disconnect()

class SensorScanner(object):
    """ BLE sensor scanner class """
    # def __init__(self):
    #     self.addresses = []

    async def scan_for_devices(self, addresses: List[str]) -> List[BLEDevice]:
        addresses = [a.lower() for a in addresses]
        undetected_devices = []
        s = BleakScanner()
        print("Detecting devices...")
        devices = [await s.find_device_by_address(address, timeout=5.0) for address in addresses]
        for d in devices:
            if d:
                print(f"Detected {d}...")
        if None in devices:
            # We did not find all desired devices...
            undetected_devices = list(
                set(addresses).difference(
                    list(
                        filter(
                            lambda x: x in [d.address.lower() for d in devices if d],
                            addresses,
                        )
                    )
                )
            )
            devices = [i for i in devices if i] # Remove None from devices list
        return devices, undetected_devices

# Tacx Neo 2T output
#CyclingPowerMeasurement(instantaneous_power=0, accumulated_energy=None, pedal_power_balance=None, accumulated_torque=None, cumulative_wheel_revs=165, last_wheel_event_time=0, cumulative_crank_revs=0, last_crank_event_time=0, maximum_force_magnitude=None, minimum_force_magnitude=None, maximum_torque_magnitude=None, minimum_torque_magnitude=None, top_dead_spot_angle=None, bottom_dead_spot_angle=None)
# 4iii powermeter output
#CyclingPowerMeasurement(instantaneous_power=10, accumulated_energy=None, pedal_power_balance=None, accumulated_torque=66, cumulative_wheel_revs=None, last_wheel_event_time=None, cumulative_crank_revs=7, last_crank_event_time=11248, maximum_force_magnitude=None, minimum_force_magnitude=None, maximum_torque_magnitude=None, minimum_torque_magnitude=None, top_dead_spot_angle=None, bottom_dead_spot_angle=None)

#Cadence = (Difference in two successive Cumulative Crank Revolution values) / (Difference in two successive Last Crank Event Time values)
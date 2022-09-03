import asyncio
import sys

from bleak import BleakClient, BleakScanner
from pycycling.heart_rate_service import HeartRateService
from pycycling.cycling_power_service import CyclingPowerService
from pycycling.cycling_speed_cadence_service import CyclingSpeedCadenceService
from ble_service_uuids import service_uuids

addresses = []
ble_sensors = []

def disconnect_callback(client):
    print("Client with address {} got disconnected!".format(client.address))

def device_found(device, _):
    print(f"Found device {device.name}")

def HR_measurement_handler(data):
    print("HR: "+ str(data.bpm))

def power_measurement_handler(data):
    print("Instantaneous Power: ", data.instantaneous_power)

async def get_device_info(device):
    if device.metadata['uuids']:
        for uuid in device.metadata['uuids']:
            uuid = uuid.split('-')[0].lstrip('0').upper()
            type = next((item for item in service_uuids if item["uuid"] == uuid), None) # Check to see if we know the type of device
            if type: # If we do, add it to the list
                return {"name": device.name, "address": device.address, "sensor_type": type["name"]}

class BleSensor:
    async def __aenter__(self):
        print('__aenter__ for BleSensor')

    async def __aexit__(self, *_):
        print('__aexit__ Clean up for BleSensor')
        asyncio.sleep(5)

    async def connect(device):
        try:
            async with BleakClient(device, timeout=20.0) as client:

                client.set_disconnected_callback(disconnect_callback)
                while not client.is_connected:
                    print("Connecting to sensor...")
                    asyncio.sleep(1)
                device_info = await get_device_info(device)
                print(device_info)
                if device_info['sensor_type'] == 'Heart Rate':
                    print("Heart Rate Monitor Connected!")
                    hr_service = HeartRateService(client)
                    hr_service.set_hr_measurement_handler(HR_measurement_handler)

                    await hr_service.enable_hr_measurement_notifications()
                elif device_info['sensor_type'] == 'Cycling Power' or device_info['sensor_type'] == 'Generic Access':
                    print("Powermeter connected!")
                    power_service = CyclingPowerService(client)
                    power_service.set_cycling_power_measurement_handler(power_measurement_handler)

                    await power_service.enable_cycling_power_measurement_notifications()
                else:
                    print("Connected to unsupported BLE device type")
                while True:
                    await asyncio.sleep(1)

        except asyncio.exceptions.TimeoutError:
            print(f"Can't connect to device {device.address}. Does it run a GATT server?")

async def main():
    scanner = BleakScanner()
    scanner.register_detection_callback(device_found)
    hrm = await BleakScanner.find_device_by_address("D9:38:0B:2E:22:DD",timeout=60.0)
    power = await BleakScanner.find_device_by_address("F1:01:52:E2:90:FA",timeout=60.0)
    ble_sensors = [hrm, power]
    await asyncio.gather(
        *(BleSensor.connect(device) for device in ble_sensors)
    )


if __name__ == "__main__":

    asyncio.run(main())

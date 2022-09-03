import asyncio
import functools
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
    if device.address in addresses:
        ble_sensors.append(device)
        print(f"Found device {device.name}")
        device_info = get_device_info(device)
        print(device_info)

def HR_measurement_handler(data):
    print("HR: "+ str(data.bpm))

def power_measurement_handler(data):
    print("Instantaneous Power: ", data.instantaneous_power)

def get_device_info(device):
    if device.metadata['uuids']:
        for uuid in device.metadata['uuids']:
            uuid = uuid.split('-')[0].lstrip('0').upper()
            type = next((item for item in service_uuids if item["uuid"] == uuid), None) # Check to see if we know the type of device
            if type: # If we do, add it to the list
                return {"name": device.name, "address": device.address, "sensor_type": type["name"]}

async def connect(device):
    try:
        async with BleakClient(device, timeout=5.0) as client:

            client.set_disconnected_callback(disconnect_callback)
            while not client.is_connected:
                pass
            device_info = get_device_info(device)
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
                print("Connected to unknown BLE device type")
            while True:
                await asyncio.sleep(1)

    except asyncio.exceptions.TimeoutError:
        print(f"Can't connect to device {device.address}. Does it run a GATT server?")


async def main():
    scanner = BleakScanner()
    scanner.register_detection_callback(device_found)
    await scanner.start()
    await asyncio.sleep(5.0)
    print("Sleeping done")
    await scanner.stop()
    await asyncio.gather(
        *(connect(device) for device in ble_sensors)
    )


if __name__ == "__main__":

    if len(sys.argv) >= 2:
        addresses = sys.argv[1:]
        asyncio.run(main())
    else:
        print(
            "Please specify at least one Bluetooth address on the command line."
        )
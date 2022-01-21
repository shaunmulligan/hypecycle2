"""
BLE device discovery module
"""

import asyncio
from bleak import discover
from sensors.ble.ble_service_uuids import service_uuids

async def main():
    devices = await discover_devices()
    for d in devices:
        print(d)

async def discover_devices():
    """Discover all nearby relevant BLE devices and return them as a list"""
    raw_devices = await discover()
    devices = []
    for d in raw_devices:
        info = await get_device_info(d)
        if info:
            devices.append(info)
    return devices

async def get_device_info(device):
    if device.metadata['uuids']:
        for uuid in device.metadata['uuids']:
            uuid = uuid.split('-')[0].lstrip('0').upper()
            type = next((item for item in service_uuids if item["uuid"] == uuid), None) # Check to see if we know the type of device
            if type: # If we do, add it to the list
                return {"name": device.name, "address": device.address, "sensor_type": type["name"]}

if __name__ == "__main__":
    import os

    os.environ["PYTHONASYNCIODEBUG"] = str(1)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())


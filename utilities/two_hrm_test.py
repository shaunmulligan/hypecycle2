import asyncio
import functools
import sys

from bleak import BleakClient, BleakScanner

DEVICE_NAME_UUID = "00002a00-0000-1000-8000-00805f9b34fb"
HEART_RATE_MEASUREMENT_UUID = "00002a37-0000-1000-8000-00805f9b34fb"

addresses = []
heart_rate_sensors = []


def device_found(device, _):
    if device.address in addresses:
        heart_rate_sensors.append(device)
        print(f"Found device {device.name}")


def heart_rate_changed(
    device_name: str, handle: int, data: bytearray
):
    print(f"{device_name}: {data[1]} bpm")


async def connect(device):
    try:
        async with BleakClient(device) as client:
            device_name = (
                await client.read_gatt_char(DEVICE_NAME_UUID)
            ).decode()
            print(f"Connected to {device_name}")
            await client.start_notify(
                HEART_RATE_MEASUREMENT_UUID,
                functools.partial(heart_rate_changed, device_name),
            )
            print(f"Start notifications for {device_name}...")
            while True:
                await asyncio.sleep(1)

    except asyncio.exceptions.TimeoutError:
        print(
            f"Can't connect to device {device.address}. Does it run a GATT server?"
        )


async def main():
    scanner = BleakScanner()
    scanner.register_detection_callback(device_found)
    await scanner.start()
    await asyncio.sleep(5.0)
    await scanner.stop()
    await asyncio.gather(
        *(connect(device) for device in heart_rate_sensors)
    )


if __name__ == "__main__":

    if len(sys.argv) >= 2:
        addresses = sys.argv[1:]
        asyncio.run(main())
    else:
        print(
            "Please specify at least one Bluetooth address on the command line."
        )
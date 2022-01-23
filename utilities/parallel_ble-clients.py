import sys
import asyncio
import logging
from typing import List

from bleak import BleakClient, BleakScanner
from bleak.backends.device import BLEDevice

logger = logging.getLogger("bleak.examples.two_devices")
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
handler.setFormatter(
    logging.Formatter(fmt="%(asctime)-15s %(name)-8s %(levelname)s: %(message)s")
)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)


def callback(sender, data):
    print(sender, data)


async def run(addresses, notification_uuids):
    devices, undetected_devices = await scan_for_devices(addresses)
    print("devices not found: ", undetected_devices)
    print("devices found: ", devices)
    # tasks = asyncio.gather(
    #     *(
    #         connect_to_device(device, n_uuid)
    #         for device, n_uuid in zip(devices, notification_uuids)
    #     )
    # )
    # await tasks


async def scan_for_devices(addresses: List[str]) -> List[BLEDevice]:
    addresses = [a.lower() for a in addresses]
    s = BleakScanner()
    logger.debug("Detecting devices...")
    devices = [await s.find_device_by_address(address, timeout=5.0) for address in addresses]
    for d in devices:
        if d:
            logger.debug(f"Detected {d}...")
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


async def connect_to_device(address: BLEDevice, notification_uuid: str):
    logger.info(f"Starting {address} loop...")
    async with BleakClient(address, timeout=5.0) as client:
        logger.info(f"Connected to {address}...")
        try:
            await client.start_notify(notification_uuid, callback)
            for i in range(10):
                r = await client.read_gatt_char("00002A25-0000-1000-8000-00805f9b34fb")
                logger.debug(f"[{address}] Serial Number String: {r}")
                await asyncio.sleep(6.0)
            await client.stop_notify(notification_uuid)
        except Exception as e:
            logger.error(e)
    logger.info(f"Disconnected to {address}...")


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    # Send a list of addresses to connect to and corresponding array of uuids to start notifications on.
    loop.run_until_complete(
        run(
            [
                "F0:99:19:59:B4:00",
                "F1:01:52:E2:90:FA"
            ],
            [
                "c9f60023-9f9b-fba4-5847-7fd701bf59f2",
                "0000{0:x}-0000-1000-8000-00805f9b34fb".format(0xFFE1),
            ],
        )
    )
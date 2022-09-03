import asyncio
from bleak import BleakScanner

async def scan():
    async with BleakScanner() as scanner:
        await asyncio.sleep(5.0)
    for d in scanner.discovered_devices:
        print(d)

asyncio.run(scan())
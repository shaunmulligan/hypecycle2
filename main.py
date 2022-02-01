from typing import List, Optional

import databases
import sqlalchemy
import uvicorn
import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_crudrouter import OrmarCRUDRouter

from model.db import database, Rides, Blesensors, Gpsreadings, Hrreadings, Powerreadings
from api import rides
from sensors.gps import Gps
from sensors.ble import HrSensor, PowerSensor, SensorScanner
from sensors.ble.discover import discover_devices
from sensors import pico

# Globals
app = FastAPI()
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.state.database = database

# Shared State
hypecycleState = type('', (), {})()
hypecycleState.gps_active = True
hypecycleState.hr_available = False
hypecycleState.power_available = False
hypecycleState.ride_paused = False # When this is true we should
hypecycleState.is_active = False # is_active = True when we have an Current/active ride in the DB

ble_sensors_active = asyncio.Event() # single to indicate if BLE devices should be active or not

# Create our GPS instance
gps = Gps(hypecycleState)

#Todo: remove this test route
@app.get("/location")
async def get_location():
    try:
        return hypecycleState.location
    except AttributeError:
        return {
                "latitude": 0.0,
                "longitude": 0.0,
                "gps_time": None
            }

#Todo: remove this test route
@app.get("/altitude")
async def get_altitude():
    try:
        return { "gps_altitude" : float(hypecycleState.gps_altitude), "altitude": float(hypecycleState.altitude) }
    except AttributeError:
        return {
                "gps_altitude": 0.0
            }

#Todo: remove this test route
@app.get("/speed")
async def get_speed():
    return hypecycleState.speed

#Todo: remove this test route
@app.get("/bpm")
async def get_bpm():
    try:
        return hypecycleState.bpm
    except AttributeError:
        return { "bpm": 0 }

#Todo: remove this test route
@app.get("/status")
async def get_fix():
    return { "gps_fix" : gps.is_gps_quality_ok, 
            "heart_rate": hypecycleState.hr_available, 
            "power": hypecycleState.power_available, 
            "battery": hypecycleState.battery_level, 
            "is_active": hypecycleState.is_active,
            "ride_paused": hypecycleState.ride_paused }

@app.get("/discover")
async def discover_ble_devices():
    return await discover_devices()

@app.on_event("startup")
async def startup() -> None:
    database_ = app.state.database
    if not database_.is_connected:
        await database_.connect()
    # Launch our BLE and GPS monitor tasks here
    # Spawn GPS monitoring task
    gps_task = asyncio.create_task(gps.start())
    enviro_task = asyncio.create_task(pico.monitor_pressure_temp(hypecycleState))
    battery_task = asyncio.create_task(pico.monitor_battery_level(hypecycleState))
    buttons_task = asyncio.create_task(pico.monitor_buttons(hypecycleState))
   
    #Todo: get address and type from DB of blesensors
    # address = "F0:99:19:59:B4:00" # Forerunner HR
    # address = "D9:38:0B:2E:22:DD" #HRM-pro : Tacx neo = "F1:01:52:E2:90:FA"
    addresses = ["F0:99:19:59:B4:00", "F1:01:52:E2:90:FA"]
    scanner = SensorScanner()
    devices, not_found = await scanner.scan_for_devices(addresses)
    print(devices)
    print("Couldn't find: ", not_found)
    # Todo: make the below more robust, currently always have to have both sensors found
    for device in devices:
        if device.address == addresses[0]: 
            # Start heart rate monitor 
            hypecycleState.hrm = HrSensor(hypecycleState, devices[0])
            hr_task = asyncio.create_task(hypecycleState.hrm.start(ble_sensors_active))
        if len(devices) > 1 and device.address == addresses[1]:
            # Start power meter monitor
            hypecycleState.powermeter = PowerSensor(hypecycleState, devices[1])
            power_task = asyncio.create_task(hypecycleState.powermeter.start(ble_sensors_active))

@app.on_event("shutdown")
async def shutdown() -> None:
    database_ = app.state.database
    if database_.is_connected:
        await database_.disconnect()
    # Clean up all our asyncio tasks
    hypecycleState.gps_active = False # Stop GPS loop
    await gps.stop()
    # Trigger event to stop all BLE sensor loops
    ble_sensors_active.set()

    try:
        await hypecycleState.hrm.stop()
    except AttributeError as e:
        print("HRM already doesn't exist")
    for task in asyncio.all_tasks():
        print("cancelling task ", task)
        task.cancel() # cancel all tasks

# Autogenerated CRUD routes
app.include_router(OrmarCRUDRouter(schema=Rides, prefix="rides",))
app.include_router(OrmarCRUDRouter(schema=Blesensors, prefix="sensors",))
app.include_router(OrmarCRUDRouter(schema=Gpsreadings, prefix="gps",))
app.include_router(OrmarCRUDRouter(schema=Hrreadings, prefix="heart_rate",))
app.include_router(OrmarCRUDRouter(schema=Powerreadings, prefix="power",))

# Custom Routes
app.include_router(rides.router, prefix="/rides", tags=["Rides"])
if __name__ == "__main__":
    # to play with API run the script and visit http://0.0.0.0:8001/docs
    uvicorn.run(app, host="0.0.0.0", port=8001)
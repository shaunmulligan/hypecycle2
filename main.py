from typing import List, Optional
import json
import databases
import sqlalchemy
import uvicorn
import asyncio
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_crudrouter import OrmarCRUDRouter
from fastapi import WebSocket, WebSocketDisconnect
import websockets

from bleak import BleakScanner

from model.db import database, Rides, Blesensors, Gpsreadings, Hrreadings, Powerreadings, Enviroreadings
from api import rides, settings, geojson, camera
from lib.connectionmanager import ConnectionManager
from lib import recorder
from lib.state import State

from sensors.ble import HrSensor, PowerSensor
from sensors.ble.discover import discover_devices
from sensors import gps
from sensors import ioexpander 
from sensors import bmp388

import config
# Globals
# setup loggers
logging.config.fileConfig('logging.conf', disable_existing_loggers=False)
logger = logging.getLogger(__name__)
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
hypecycleState = State()

ble_sensors_active = asyncio.Event() # single to indicate if BLE devices should be active or not

# Create our websocket manager
manager = ConnectionManager()

@app.get("/location")
async def get_location():
    try:
        return hypecycleState.location
    except AttributeError:
        return {
                "latitude": 0.0,
                "longitude": 0.0,
            }

@app.get("/altitude")
async def get_altitude():
    try:
        return { "gps_altitude" : float(hypecycleState.gps_altitude or 0.0), "altitude": float(hypecycleState.altitude or 0.0) }
    except AttributeError:
        return {
                "gps_altitude": 0.0
            }

@app.get("/speed")
async def get_speed():
    return hypecycleState.speed

@app.get("/bpm")
async def get_bpm():
    try:
        return hypecycleState.bpm
    except AttributeError:
        return 0 

@app.get("/instant_power")
async def get_instant_power():
    return {"instantaneous": hypecycleState.instantaneous_power, "3s": hypecycleState.power3s, "10s": hypecycleState.power10s}

@app.get("/status")
async def get_status():
    return { "gps_fix" : hypecycleState.fix_quality, 
            "heart_rate": hypecycleState.hr_available, 
            "power": hypecycleState.power_available, 
            "battery": hypecycleState.battery_level, 
            "is_active": hypecycleState.is_active,
            "ride_paused": hypecycleState.ride_paused,
            }

@app.get("/discover")
async def discover_ble_devices():
    return await discover_devices()

@app.get("/connect")
async def connect_ble_devices():
    # Testing Devices:
    # "F0:99:19:59:B4:00" - Forerunner HR
    # "D9:38:0B:2E:22:DD" - HRM-pro 
    # "F1:01:52:E2:90:FA" - Tacx neo 2T
    # "D1:7F:6A:25:D9:D7" - Assioma Duos

    ble_sensors = await Blesensors.objects.all()
    logger.info("Paired BLE sensors {}".format(ble_sensors))

    #TODO: Handle case where we have multiple PM and HRM devices paired.
    if ble_sensors is not []:
        for sensor in ble_sensors:
            if sensor.sensor_type == "Heart Rate":
                logger.info("Trying to connect to HRM: {}".format(sensor.name))
                hrm = await BleakScanner.find_device_by_address(sensor.address,timeout=10.0)
                if hrm is not None:
                    # Start HRM
                    hypecycleState.hrm = HrSensor(hypecycleState, hrm)
                    hr_task = asyncio.create_task(hypecycleState.hrm.start(ble_sensors_active))
                else:
                    logger.info("couldn't find {} at address: {}".format(sensor.name, sensor.address))
            elif sensor.sensor_type == "Cycling Power" or sensor.sensor_type == "Generic Access":      
                logger.info("Trying to connect to PM: {}".format(sensor.name))
                power = await BleakScanner.find_device_by_address(sensor.address,timeout=5.0)
                if power is not None:
                    # Start Power
                    hypecycleState.powermeter = PowerSensor(hypecycleState, power)
                    power_task = asyncio.create_task(hypecycleState.powermeter.start(ble_sensors_active))
                else:
                    logger.info("couldn't find {} at address: {}".format(sensor.name, sensor.address))
            else:
                logger.warning("This sensor {} of type {} is not currently supported".format(sensor.name, sensor.address))
        return {"status": "HRM is {} and PM is {}".format(hypecycleState.hr_available, hypecycleState.power_available)}
    else:
        logger.info("You don't have any BLE devices paired, please pair one!")
        return {"status": "You don't have any BLE devices paired, please pair one!"}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            state = hypecycleState.toJson()
            await websocket.send_json(state)
            await asyncio.sleep(1) # Send shared state once every second
    except websockets.exceptions.ConnectionClosedError:
        logger.info("Websocket seems down, trying again...")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except asyncio.exceptions.CancelledError:
        manager.disconnect(websocket)

@app.on_event("startup")
async def startup() -> None:
    database_ = app.state.database
    if not database_.is_connected:
        await database_.connect()
    # Launch our BLE and GPS monitor tasks here
    # Spawn GPS monitoring task
    gps_task = asyncio.create_task(gps.monitor_gps(hypecycleState))
    enviro_task = asyncio.create_task(bmp388.monitor_pressure_temp(hypecycleState))
    button_task = asyncio.create_task(ioexpander.monitor_buttons(hypecycleState))
    battery_task = asyncio.create_task(ioexpander.monitor_battery(hypecycleState))
    recorder_task = asyncio.create_task(recorder.monitor_recording(hypecycleState,interval=1))
    averages_task = asyncio.create_task(recorder.monitor_averages(hypecycleState))
    lights_task = asyncio.create_task(ioexpander.lights_task(hypecycleState))

@app.on_event("shutdown")
async def shutdown() -> None:
    database_ = app.state.database
    if database_.is_connected:
        await database_.disconnect()
    # Clean up all our asyncio tasks
    hypecycleState.gps_active = False # Stop GPS loopa
    # Trigger event to stop all BLE sensor loops
    ble_sensors_active.set()

    try:
        await hypecycleState.hrm.stop()
    except AttributeError as e:
        logger.info("HRM already doesn't exist")
    for task in asyncio.all_tasks():
        logger.info("cancelling task ".format(task))
        task.cancel() # cancel all tasks

# Autogenerated CRUD routes
app.include_router(OrmarCRUDRouter(schema=Rides, prefix="rides",))
app.include_router(OrmarCRUDRouter(schema=Blesensors, prefix="sensors",))
app.include_router(OrmarCRUDRouter(schema=Gpsreadings, prefix="gps",))
app.include_router(OrmarCRUDRouter(schema=Hrreadings, prefix="heart_rate",))
app.include_router(OrmarCRUDRouter(schema=Powerreadings, prefix="power",))
app.include_router(OrmarCRUDRouter(schema=Enviroreadings, prefix="enviroment"))
# Custom Routes
app.include_router(rides.router, prefix="/rides", tags=["Rides"])
app.include_router(settings.router, prefix="/settings", tags=["Settings"])
app.include_router(geojson.router, prefix="/geojson", tags=["Geojson"])
app.include_router(camera.router, prefix="/camera", tags=["Camera"])

if __name__ == "__main__":
    # to play with API run the script and visit http://0.0.0.0:8001/docs
    uvicorn.run(app, host="0.0.0.0", port=8001)
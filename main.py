from typing import List, Optional
import json
import databases
import sqlalchemy
import uvicorn
import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_crudrouter import OrmarCRUDRouter
from fastapi import WebSocket, WebSocketDisconnect

import logging

from bleak import BleakScanner

from model.db import database, Rides, Blesensors, Gpsreadings, Hrreadings, Powerreadings, Enviroreadings
from api import rides
from lib.connectionmanager import ConnectionManager
from lib import recorder

from sensors.ble import HrSensor, PowerSensor
from sensors.ble.discover import discover_devices
from sensors import gps
from sensors import ioexpander 
from sensors import bmp388
from lib.recorder.files import generate_gpx

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
hypecycleState = type('SharedData', (), {})()
hypecycleState.gps_active = True
hypecycleState.hr_available = False
hypecycleState.power_available = False
hypecycleState.ride_paused = False # When this is true we should record data
hypecycleState.is_active = False # is_active = True when we have an Current/active ride in the DB
hypecycleState.battery_level = 100.0
hypecycleState.fix_quality = 0
hypecycleState.instantaneous_power = 0
hypecycleState.cadence = 0
hypecycleState.bpm = 0
hypecycleState.speed = 0.0
hypecycleState.max_speed = 0.0
hypecycleState.gps_altitude = 0.0
hypecycleState.altitude = 0.0
hypecycleState.temperature = 0.0
hypecycleState.location = {
                "latitude": 0.0,
                "longitude": 0.0,
                # "gps_time": None
            }
hypecycleState.latitude = 0.0
hypecycleState.longitude = 0.0
hypecycleState.distance = 0
hypecycleState.moving_time = 0
hypecycleState.stopped_time = 0
hypecycleState.uphill = 0
hypecycleState.downhill = 0

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
                # "gps_time": None
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
    try:
        return hypecycleState.instantaneous_power
    except AttributeError:
        return  0 

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
            elif sensor.sensor_type == "Cycling Power":      
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

@app.get("/save/{ride_id}")
async def save_gpx(ride_id):
    return await generate_gpx(ride_id)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            state = { "gps_fix" : hypecycleState.fix_quality, 
            "heart_rate": hypecycleState.hr_available, 
            "power": hypecycleState.power_available, 
            "battery": hypecycleState.battery_level, 
            "is_active": hypecycleState.is_active,
            "ride_paused": hypecycleState.ride_paused,
            "instantaneous_power": hypecycleState.instantaneous_power,
            "bpm": hypecycleState.bpm,
            "speed": hypecycleState.speed,
            "gps_altitude": float(hypecycleState.gps_altitude or 0.0),
            "altitude": float(hypecycleState.altitude or 0.0),
            "location": hypecycleState.location,
            "temperature": hypecycleState.temperature,
            "latitude": hypecycleState.latitude,
            "longitude": hypecycleState.longitude,
            "distance": hypecycleState.distance,
            "uphill": hypecycleState.uphill,
            "downhill": hypecycleState.downhill,
            "moving_time": hypecycleState.moving_time,
            "stopped_time": hypecycleState.stopped_time,
             }

            await websocket.send_json(state)
            await asyncio.sleep(1) # Send shared state once every second
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
if __name__ == "__main__":

    # to play with API run the script and visit http://0.0.0.0:8001/docs
    uvicorn.run(app, host="0.0.0.0", port=8001)
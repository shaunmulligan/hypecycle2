from typing import List, Optional

import databases
import sqlalchemy
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_crudrouter import OrmarCRUDRouter

from model.db import database, Rides, Blesensors, Gpsreadings, Hrreadings, Powerreadings
from api import rides

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

@app.on_event("startup")
async def startup() -> None:
    database_ = app.state.database
    if not database_.is_connected:
        await database_.connect()
    # Launch our BLE and GPS monitor tasks here

@app.on_event("shutdown")
async def shutdown() -> None:
    database_ = app.state.database
    if database_.is_connected:
        await database_.disconnect()
    # Clean up all our asyncio tasks

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
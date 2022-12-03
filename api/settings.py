from fastapi import APIRouter, HTTPException
import config
from model.db import Settings
from lib.machine import Machine

router = APIRouter()
m = Machine(255,True)

@router.get("/", response_model=Settings)
async def get_current_settings():
    settings = await Settings.objects.get_or_create() # Get or create a settings entry if it doesn't exist
    return settings

@router.post("/update", response_model=Settings)
async def update_settings(settings: Settings):
    s = await Settings.objects.get(id=1) # Always use the first settings entry
    await s.upsert(**dict(settings))
    print(s)
    m.brightness = s.lcd_brightness
    if not s.wifi_enabled:
        await m.wifiDisable()
    else:
        await m.wifiEnable()

    return s

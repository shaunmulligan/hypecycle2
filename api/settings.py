from fastapi import APIRouter, HTTPException
import config
from model.db import Settings
# from model.config import Settings

router = APIRouter()

@router.get("/", response_model=Settings)
async def get_current_settings():
    settings = await Settings.objects.get_or_create() # Get or create a settings entry if it doesn't exist
    return settings

@router.post("/update", response_model=Settings)
async def update_settings(settings: Settings):
    s = await Settings.objects.get(id=1) # Always use the first settings entry
    await s.upsert(**dict(settings))
    return s

from fastapi import APIRouter, HTTPException
import config
from model.config import Settings

router = APIRouter()

@router.get("/", response_model=Settings)
async def get_current_settings():
    return config.settings

@router.post("/update", response_model=Settings)
async def update_settings(settings: Settings):
    config.settings = settings
    # TODO: Trigger actually updating the settings here
    return config.settings

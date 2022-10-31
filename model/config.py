from typing import Optional
from pydantic import BaseModel


class Settings(BaseModel):
    wifi_enabled: bool
    bluetooth_enabled: bool
    lights_enabled: bool
    upload_enabled: bool
    lcd_brightness: int

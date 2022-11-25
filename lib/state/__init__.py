from dataclasses import dataclass, field
import json

@dataclass
class State:
    """Class for keeping track of hypecycle state."""
    gps_active: bool = True
    hr_available: bool = False
    power_available: bool = False
    ride_paused: bool = False # When this is true we should record data
    is_active: bool = False # is_active = True when we have an Current/active ride in the DB
    battery_level: float = 100.0
    fix_quality: int = 0
    instantaneous_power: float = 0.0
    power3s: float = 0.0
    power10s: float = 0.0
    cadence: float = 0.0
    bpm: int = 0
    speed: float = 0.0
    max_speed: float = 0.0
    gps_altitude: float = 0.0
    altitude: float = 0.0
    temperature: float = 0.0
    location: dict[str, float] = field(
        default_factory=lambda: {'X-latitude':0.0,'longitude': 0.0}
    )
    latitude: float = 0.0
    longitude: float = 0.0
    distance: float = 0.0
    moving_time: int = 0
    stopped_time: int = 0
    elapsed_time: int = 0
    uphill: float = 0.0
    downhill: float = 0.0
    max_speed: float = 0.0
    avg_speed: float = 0.0
    max_altitude: float = 0.0
    avg_power: float = 0.0
    max_power: float = 0.0
    avg_hr: float = 0.0
    max_hr: float = 0.0
    avg_temp: float = 0.0
    max_temp: float = 0.0

    def toJson(self) -> json:
        #TODO: regularize the names in frontend with those above so we can auto generate this object without having to translate names
        return { "gps_fix" : self.fix_quality, 
            "heart_rate": self.hr_available, 
            "power": self.power_available, 
            "battery": self.battery_level, 
            "is_active": self.is_active,
            "ride_paused": self.ride_paused,
            "instantaneous_power": self.instantaneous_power,
            "power3s": self.power3s,
            "power10s": self.power10s,
            "cadence": self.cadence,
            "bpm": self.bpm,
            "speed": self.speed,
            "max_speed": self.max_speed,
            "avg_speed": self.avg_speed,
            "gps_altitude": float(self.gps_altitude or 0.0),
            "altitude": float(self.altitude or 0.0),
            "location": self.location,
            "temperature": self.temperature,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "distance": self.distance,
            "uphill": self.uphill,
            "downhill": self.downhill,
            "elapsed_time": self.elapsed_time,
            "moving_time": self.moving_time,
            "stopped_time": self.stopped_time,
            "avg_power": self.avg_power,
            "max_power": self.max_power,
            "avg_hr": self.avg_hr,
            "max_hr": self.max_hr,
            "avg_temp": self.avg_temp,
            "max_temp": self.max_temp,
             }
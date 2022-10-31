from typing import List, Optional

import databases
import ormar
import sqlalchemy
import datetime

database = databases.Database("sqlite:///db.sqlite")
metadata = sqlalchemy.MetaData()

class BaseMeta(ormar.ModelMeta):
    database = database
    metadata = metadata

class Rides(ormar.Model):
    class Meta(BaseMeta):
        tablename = "rides"

    id: int = ormar.Integer(primary_key=True)
    name: str = ormar.String(max_length=100, nullable=True)
    start_time: datetime = ormar.DateTime(default=datetime.datetime.now, timezone=False)
    end_time: datetime = ormar.DateTime(nullable=True, timezone=False)
    active: bool = ormar.Boolean(default=True)

class Blesensors(ormar.Model):
    class Meta(BaseMeta):
        tablename = "blesensors"

    id: int = ormar.Integer(primary_key=True)
    name: str = ormar.String(max_length=100)
    address: str = ormar.String(max_length=100, unique=True)
    sensor_type: str = ormar.String(default="Generic", max_length=100)

class Gpsreadings(ormar.Model):
    class Meta(BaseMeta):
        tablename = "gpsreadings"

    id: int = ormar.Integer(primary_key=True)
    timestamp: datetime = ormar.DateTime(default=datetime.datetime.now, timezone=False)
    ride_id: Optional[Rides] = ormar.ForeignKey(Rides, nullable=True, ondelete="CASCADE")
    latitude: float = ormar.Float(default=0.0)
    longitude: float = ormar.Float(default=0.0)
    altitude: float = ormar.Float(default=0.0)
    speed: float = ormar.Float(default=0.0)

class Hrreadings(ormar.Model):
    class Meta(BaseMeta):
        tablename = "hrreadings"

    id: int = ormar.Integer(primary_key=True)
    timestamp: datetime = ormar.DateTime(default=datetime.datetime.now, timezone=False)
    ride_id: Optional[Rides] = ormar.ForeignKey(Rides, nullable=True, ondelete="CASCADE")
    bpm: int = ormar.Integer(default=0)

class Powerreadings(ormar.Model):
    class Meta(BaseMeta):
        tablename = "powerreadings"

    id: int = ormar.Integer(primary_key=True)
    timestamp: datetime = ormar.DateTime(default=datetime.datetime.now, timezone=False)
    ride_id: Optional[Rides] = ormar.ForeignKey(Rides, nullable=True, ondelete="CASCADE")
    power: int = ormar.Integer(default=0)
    cadence: int = ormar.Integer(default=0)

class Enviroreadings(ormar.Model):
    class Meta(BaseMeta):
        tablename = "enviroreadings"

    id: int = ormar.Integer(primary_key=True)
    timestamp: datetime = ormar.DateTime(default=datetime.datetime.now, timezone=False)
    ride_id: Optional[Rides] = ormar.ForeignKey(Rides, nullable=True, ondelete="CASCADE")
    temp: float = ormar.Float(default=0.0)
    altitude: float = ormar.Float(default=0.0)


def main():
    print("boot strapping DB")
    engine = sqlalchemy.create_engine("sqlite:///db.sqlite")
    # note that this has to be the same metadata that is used in ormar Models definition
    metadata.create_all(engine)


if __name__ == "__main__":
    main()
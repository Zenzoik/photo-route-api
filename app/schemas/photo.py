from pydantic import BaseModel
from pydantic_settings import SettingsConfigDict
from datetime import datetime

class PhotoOut(BaseModel):
    id: int
    filename: str
    timestamp: datetime
    lat: float
    lng: float
    owner_token: str

    model_config = SettingsConfigDict(from_attributes=True)


class RoutePoint(BaseModel):
    filename: str
    lat: float
    lng: float
    time: datetime
    owner_token: str

    model_config = SettingsConfigDict(from_attributes=True)
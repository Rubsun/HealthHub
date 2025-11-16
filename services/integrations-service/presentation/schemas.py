from datetime import datetime
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel


class WeatherLogResponse(BaseModel):
    log_id: UUID
    city: str
    temperature: float
    description: str
    humidity: Optional[int]
    wind_speed: Optional[float]
    recorded_at: datetime
    created_at: datetime

    class Config:
        from_attributes = True


class WeatherFetchRequest(BaseModel):
    city: str




from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4


class WeatherLog:
    def __init__(
        self,
        city: str,
        temperature: float,
        description: str,
        humidity: Optional[int] = None,
        wind_speed: Optional[float] = None,
        log_id: Optional[UUID] = None,
        recorded_at: Optional[datetime] = None,
        created_at: Optional[datetime] = None
    ):
        self.log_id = log_id or uuid4()
        self.city = city
        self.temperature = temperature
        self.description = description
        self.humidity = humidity
        self.wind_speed = wind_speed
        self.recorded_at = recorded_at or datetime.utcnow()
        self.created_at = created_at or datetime.utcnow()




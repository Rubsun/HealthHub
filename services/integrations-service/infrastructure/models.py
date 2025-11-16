from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import Column, String, Float, Integer, DateTime
from sqlalchemy.dialects.postgresql import UUID as PGUUID

from infrastructure.database import Base


class WeatherLogModel(Base):
    __tablename__ = "weather_logs"

    log_id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    city = Column(String, nullable=False, index=True)
    temperature = Column(Float, nullable=False)
    description = Column(String, nullable=False)
    humidity = Column(Integer, nullable=True)
    wind_speed = Column(Float, nullable=True)
    recorded_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)




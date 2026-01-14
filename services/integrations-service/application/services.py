import logging
from typing import Optional, List

from domain.entities import WeatherLog
from infrastructure.external_apis import OpenWeatherAPI
from infrastructure.repositories import SQLAlchemyWeatherLogRepository
from infrastructure.database import async_session_maker
from infrastructure.messaging import get_publisher

logger = logging.getLogger(__name__)


class WeatherService:
    """Service for weather operations."""
    
    def __init__(self):
        self.api = OpenWeatherAPI()
        self._publisher = None
    
    @property
    def publisher(self):
        if self._publisher is None:
            self._publisher = get_publisher()
        return self._publisher

    async def fetch_and_save_weather(self, city: str) -> Optional[WeatherLog]:
        """Fetch weather from API and save to database, then publish event."""
        weather_data = await self.api.get_current_weather(city)
        if not weather_data:
            return None
        
        async with async_session_maker() as session:
            repository = SQLAlchemyWeatherLogRepository(session)
            log = WeatherLog(
                city=weather_data["city"],
                temperature=weather_data["temperature"],
                description=weather_data["description"],
                humidity=weather_data.get("humidity"),
                wind_speed=weather_data.get("wind_speed")
            )
            saved_log = await repository.create(log)
        
        try:
            await self.publisher.publish_weather_updated(
                city=saved_log.city,
                temperature=saved_log.temperature,
                description=saved_log.description,
                humidity=saved_log.humidity,
                wind_speed=saved_log.wind_speed,
                recorded_at=saved_log.recorded_at
            )
        except Exception as e:
            logger.warning(f"Failed to publish weather.updated event: {e}")
        
        return saved_log

    async def get_latest_weather(self, city: str) -> Optional[WeatherLog]:
        """Get the latest weather log for a city."""
        async with async_session_maker() as session:
            repository = SQLAlchemyWeatherLogRepository(session)
            return await repository.get_latest_by_city(city)

    async def get_weather_history(self, city: str, limit: int = 10) -> List[WeatherLog]:
        """Get weather history for a city."""
        async with async_session_maker() as session:
            repository = SQLAlchemyWeatherLogRepository(session)
            return await repository.get_by_city(city, limit)

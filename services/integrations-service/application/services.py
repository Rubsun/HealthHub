from typing import Optional, List
from uuid import UUID

from domain.entities import WeatherLog
from domain.repositories import WeatherLogRepository
from infrastructure.external_apis import OpenWeatherAPI
from infrastructure.repositories import SQLAlchemyWeatherLogRepository
from infrastructure.database import async_session_maker


class WeatherService:
    def __init__(self):
        self.api = OpenWeatherAPI()

    async def fetch_and_save_weather(self, city: str) -> Optional[WeatherLog]:
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
            return await repository.create(log)

    async def get_latest_weather(self, city: str) -> Optional[WeatherLog]:
        async with async_session_maker() as session:
            repository = SQLAlchemyWeatherLogRepository(session)
            return await repository.get_latest_by_city(city)

    async def get_weather_history(self, city: str, limit: int = 10) -> List[WeatherLog]:
        async with async_session_maker() as session:
            repository = SQLAlchemyWeatherLogRepository(session)
            return await repository.get_by_city(city, limit)




import pytest
from uuid import uuid4
from datetime import datetime

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "services" / "integrations-service"))

from domain.entities import WeatherLog
from domain.repositories import WeatherLogRepository


class MockWeatherLogRepository(WeatherLogRepository):
    def __init__(self):
        self.logs = []

    async def create(self, log: WeatherLog) -> WeatherLog:
        self.logs.append(log)
        return log

    async def get_latest_by_city(self, city: str):
        city_logs = [l for l in self.logs if l.city == city]
        if city_logs:
            return sorted(city_logs, key=lambda x: x.recorded_at, reverse=True)[0]
        return None

    async def get_by_city(self, city: str, limit=10):
        city_logs = [l for l in self.logs if l.city == city]
        return sorted(city_logs, key=lambda x: x.recorded_at, reverse=True)[:limit]


@pytest.mark.asyncio
async def test_create_weather_log():
    repository = MockWeatherLogRepository()
    
    log = WeatherLog(
        city="Moscow",
        temperature=15.5,
        description="clear sky",
        humidity=60,
        wind_speed=3.2
    )
    
    created_log = await repository.create(log)
    
    assert created_log.city == "Moscow"
    assert created_log.temperature == 15.5
    assert created_log.description == "clear sky"
    assert created_log.humidity == 60
    assert created_log.wind_speed == 3.2


@pytest.mark.asyncio
async def test_get_latest_weather_by_city():
    repository = MockWeatherLogRepository()
    
    log1 = WeatherLog(city="Moscow", temperature=15.0, description="sunny")
    log2 = WeatherLog(city="Moscow", temperature=16.0, description="cloudy")
    log3 = WeatherLog(city="SPB", temperature=12.0, description="rainy")
    
    await repository.create(log1)
    await repository.create(log2)
    await repository.create(log3)
    
    latest = await repository.get_latest_by_city("Moscow")
    
    assert latest is not None
    assert latest.city == "Moscow"
    assert latest.temperature == 16.0


def test_weather_log_entity():
    log = WeatherLog(
        city="Moscow",
        temperature=15.5,
        description="clear sky",
        humidity=60,
        wind_speed=3.2
    )
    
    assert log.city == "Moscow"
    assert log.temperature == 15.5
    assert log.description == "clear sky"
    assert log.humidity == 60
    assert log.wind_speed == 3.2
    assert log.log_id is not None
    assert log.recorded_at is not None


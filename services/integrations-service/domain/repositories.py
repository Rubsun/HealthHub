from abc import ABC, abstractmethod
from typing import Optional, List
from uuid import UUID

from domain.entities import WeatherLog


class WeatherLogRepository(ABC):
    @abstractmethod
    async def create(self, log: WeatherLog) -> WeatherLog:
        pass

    @abstractmethod
    async def get_latest_by_city(self, city: str) -> Optional[WeatherLog]:
        pass

    @abstractmethod
    async def get_by_city(self, city: str, limit: int = 10) -> List[WeatherLog]:
        pass




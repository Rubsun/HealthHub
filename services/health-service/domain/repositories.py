from abc import ABC, abstractmethod
from typing import Optional, List
from uuid import UUID
from datetime import datetime

from domain.entities import HealthMetric, Activity, Recommendation, ActivityType


class HealthMetricRepository(ABC):
    @abstractmethod
    async def create(self, metric: HealthMetric) -> HealthMetric:
        pass

    @abstractmethod
    async def get_by_id(self, metric_id: UUID) -> Optional[HealthMetric]:
        pass

    @abstractmethod
    async def get_by_user_id(self, user_id: UUID, limit: int = 100) -> List[HealthMetric]:
        pass

    @abstractmethod
    async def update(self, metric: HealthMetric) -> HealthMetric:
        pass

    @abstractmethod
    async def delete(self, metric_id: UUID) -> bool:
        pass


class ActivityRepository(ABC):
    @abstractmethod
    async def create(self, activity: Activity) -> Activity:
        pass

    @abstractmethod
    async def get_by_id(self, activity_id: UUID) -> Optional[Activity]:
        pass

    @abstractmethod
    async def get_by_user_id(self, user_id: UUID, limit: int = 100) -> List[Activity]:
        pass

    @abstractmethod
    async def update(self, activity: Activity) -> Activity:
        pass

    @abstractmethod
    async def delete(self, activity_id: UUID) -> bool:
        pass


class RecommendationRepository(ABC):
    @abstractmethod
    async def create(self, recommendation: Recommendation) -> Recommendation:
        pass

    @abstractmethod
    async def get_by_user_id(self, user_id: UUID, limit: int = 10) -> List[Recommendation]:
        pass




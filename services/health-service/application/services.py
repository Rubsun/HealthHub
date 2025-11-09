from typing import Optional, List
from uuid import UUID

from domain.use_cases import (
    CreateHealthMetricUseCase,
    GetHealthMetricsUseCase,
    UpdateHealthMetricUseCase,
    CreateActivityUseCase,
    GetActivitiesUseCase,
    GenerateRecommendationUseCase
)
from domain.entities import ActivityType
from infrastructure.repositories import (
    SQLAlchemyHealthMetricRepository,
    SQLAlchemyActivityRepository,
    SQLAlchemyRecommendationRepository
)
from infrastructure.database import async_session_maker


class HealthMetricService:
    async def create_metric(
        self,
        user_id: UUID,
        steps: Optional[int] = None,
        calories: Optional[float] = None,
        heart_rate: Optional[int] = None,
        sleep_hours: Optional[float] = None
    ):
        async with async_session_maker() as session:
            repository = SQLAlchemyHealthMetricRepository(session)
            use_case = CreateHealthMetricUseCase(repository)
            return await use_case.execute(user_id, steps, calories, heart_rate, sleep_hours)

    async def get_metrics(self, user_id: UUID, limit: int = 100):
        async with async_session_maker() as session:
            repository = SQLAlchemyHealthMetricRepository(session)
            use_case = GetHealthMetricsUseCase(repository)
            return await use_case.execute(user_id, limit)

    async def update_metric(
        self,
        metric_id: UUID,
        steps: Optional[int] = None,
        calories: Optional[float] = None,
        heart_rate: Optional[int] = None,
        sleep_hours: Optional[float] = None
    ):
        async with async_session_maker() as session:
            repository = SQLAlchemyHealthMetricRepository(session)
            use_case = UpdateHealthMetricUseCase(repository)
            return await use_case.execute(metric_id, steps, calories, heart_rate, sleep_hours)


class ActivityService:
    async def create_activity(
        self,
        user_id: UUID,
        activity_type: ActivityType,
        duration_minutes: int,
        calories_burned: Optional[float] = None,
        distance_km: Optional[float] = None
    ):
        async with async_session_maker() as session:
            repository = SQLAlchemyActivityRepository(session)
            use_case = CreateActivityUseCase(repository)
            return await use_case.execute(user_id, activity_type, duration_minutes, calories_burned, distance_km)

    async def get_activities(self, user_id: UUID, limit: int = 100):
        async with async_session_maker() as session:
            repository = SQLAlchemyActivityRepository(session)
            use_case = GetActivitiesUseCase(repository)
            return await use_case.execute(user_id, limit)


class RecommendationService:
    async def generate_recommendation(self, user_id: UUID, weather_data: Optional[dict] = None):
        async with async_session_maker() as session:
            metric_repository = SQLAlchemyHealthMetricRepository(session)
            activity_repository = SQLAlchemyActivityRepository(session)
            recommendation_repository = SQLAlchemyRecommendationRepository(session)
            use_case = GenerateRecommendationUseCase(
                metric_repository,
                activity_repository,
                recommendation_repository
            )
            return await use_case.execute(user_id, weather_data)




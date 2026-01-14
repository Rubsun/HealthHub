import logging
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
from infrastructure.messaging import get_publisher

logger = logging.getLogger(__name__)


class HealthMetricService:
    """Service for health metric operations."""
    
    def __init__(self):
        self._publisher = None
    
    @property
    def publisher(self):
        if self._publisher is None:
            self._publisher = get_publisher()
        return self._publisher
    
    async def create_metric(
        self,
        user_id: UUID,
        steps: Optional[int] = None,
        calories: Optional[float] = None,
        heart_rate: Optional[int] = None,
        sleep_hours: Optional[float] = None
    ):
        """Create a health metric and publish event."""
        async with async_session_maker() as session:
            repository = SQLAlchemyHealthMetricRepository(session)
            use_case = CreateHealthMetricUseCase(repository)
            metric = await use_case.execute(user_id, steps, calories, heart_rate, sleep_hours)
        
        try:
            await self.publisher.publish_health_metric_created(
                metric_id=metric.metric_id,
                user_id=metric.user_id,
                steps=metric.steps,
                calories=metric.calories,
                heart_rate=metric.heart_rate,
                sleep_hours=metric.sleep_hours,
                recorded_at=metric.recorded_at
            )
        except Exception as e:
            logger.warning(f"Failed to publish health.metric.created event: {e}")
        
        return metric

    async def get_metrics(self, user_id: UUID, limit: int = 100):
        """Get health metrics for a user."""
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
        """Update a health metric."""
        async with async_session_maker() as session:
            repository = SQLAlchemyHealthMetricRepository(session)
            use_case = UpdateHealthMetricUseCase(repository)
            return await use_case.execute(metric_id, steps, calories, heart_rate, sleep_hours)


class ActivityService:
    """Service for activity operations."""
    
    def __init__(self):
        self._publisher = None
    
    @property
    def publisher(self):
        if self._publisher is None:
            self._publisher = get_publisher()
        return self._publisher
    
    async def create_activity(
        self,
        user_id: UUID,
        activity_type: ActivityType,
        duration_minutes: int,
        calories_burned: Optional[float] = None,
        distance_km: Optional[float] = None
    ):
        """Create an activity and publish event."""
        async with async_session_maker() as session:
            repository = SQLAlchemyActivityRepository(session)
            use_case = CreateActivityUseCase(repository)
            activity = await use_case.execute(
                user_id, activity_type, duration_minutes, 
                calories_burned, distance_km
            )
        
        try:
            await self.publisher.publish_activity_created(
                activity_id=activity.activity_id,
                user_id=activity.user_id,
                activity_type=activity.activity_type.value if hasattr(activity.activity_type, 'value') else str(activity.activity_type),
                duration_minutes=activity.duration_minutes,
                calories_burned=activity.calories_burned,
                distance_km=activity.distance_km,
                started_at=activity.started_at
            )
        except Exception as e:
            logger.warning(f"Failed to publish activity.created event: {e}")
        
        return activity

    async def get_activities(self, user_id: UUID, limit: int = 100):
        """Get activities for a user."""
        async with async_session_maker() as session:
            repository = SQLAlchemyActivityRepository(session)
            use_case = GetActivitiesUseCase(repository)
            return await use_case.execute(user_id, limit)


class RecommendationService:
    """Service for recommendation operations."""
    
    def __init__(self):
        self._publisher = None
    
    @property
    def publisher(self):
        if self._publisher is None:
            self._publisher = get_publisher()
        return self._publisher
    
    async def generate_recommendation(self, user_id: UUID, weather_data: Optional[dict] = None):
        """Generate a recommendation and publish event."""
        async with async_session_maker() as session:
            metric_repository = SQLAlchemyHealthMetricRepository(session)
            activity_repository = SQLAlchemyActivityRepository(session)
            recommendation_repository = SQLAlchemyRecommendationRepository(session)
            use_case = GenerateRecommendationUseCase(
                metric_repository,
                activity_repository,
                recommendation_repository
            )
            recommendation = await use_case.execute(user_id, weather_data)
        
        try:
            await self.publisher.publish_recommendation_generated(
                recommendation_id=recommendation.recommendation_id,
                user_id=recommendation.user_id,
                message=recommendation.message
            )
        except Exception as e:
            logger.warning(f"Failed to publish recommendation.generated event: {e}")
        
        return recommendation

from typing import Optional, List
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from domain.entities import HealthMetric, Activity, Recommendation, ActivityType
from domain.repositories import (
    HealthMetricRepository,
    ActivityRepository,
    RecommendationRepository
)
from infrastructure.models import HealthMetricModel, ActivityModel, RecommendationModel


class SQLAlchemyHealthMetricRepository(HealthMetricRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    def _to_entity(self, model: HealthMetricModel) -> HealthMetric:
        return HealthMetric(
            metric_id=model.metric_id,
            user_id=model.user_id,
            steps=model.steps,
            calories=model.calories,
            heart_rate=model.heart_rate,
            sleep_hours=model.sleep_hours,
            recorded_at=model.recorded_at,
            created_at=model.created_at
        )

    def _to_model(self, entity: HealthMetric) -> HealthMetricModel:
        return HealthMetricModel(
            metric_id=entity.metric_id,
            user_id=entity.user_id,
            steps=entity.steps,
            calories=entity.calories,
            heart_rate=entity.heart_rate,
            sleep_hours=entity.sleep_hours,
            recorded_at=entity.recorded_at,
            created_at=entity.created_at
        )

    async def create(self, metric: HealthMetric) -> HealthMetric:
        model = self._to_model(metric)
        self.session.add(model)
        await self.session.commit()
        await self.session.refresh(model)
        return self._to_entity(model)

    async def get_by_id(self, metric_id: UUID) -> Optional[HealthMetric]:
        result = await self.session.execute(
            select(HealthMetricModel).where(HealthMetricModel.metric_id == metric_id)
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def get_by_user_id(self, user_id: UUID, limit: int = 100) -> List[HealthMetric]:
        result = await self.session.execute(
            select(HealthMetricModel)
            .where(HealthMetricModel.user_id == user_id)
            .order_by(HealthMetricModel.recorded_at.desc())
            .limit(limit)
        )
        models = result.scalars().all()
        return [self._to_entity(model) for model in models]

    async def update(self, metric: HealthMetric) -> HealthMetric:
        result = await self.session.execute(
            select(HealthMetricModel).where(HealthMetricModel.metric_id == metric.metric_id)
        )
        model = result.scalar_one()
        model.steps = metric.steps
        model.calories = metric.calories
        model.heart_rate = metric.heart_rate
        model.sleep_hours = metric.sleep_hours
        model.recorded_at = metric.recorded_at
        await self.session.commit()
        await self.session.refresh(model)
        return self._to_entity(model)

    async def delete(self, metric_id: UUID) -> bool:
        result = await self.session.execute(
            select(HealthMetricModel).where(HealthMetricModel.metric_id == metric_id)
        )
        model = result.scalar_one_or_none()
        if not model:
            return False
        await self.session.delete(model)
        await self.session.commit()
        return True


class SQLAlchemyActivityRepository(ActivityRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    def _to_entity(self, model: ActivityModel) -> Activity:
        activity_type = ActivityType(model.activity_type) if isinstance(model.activity_type, str) else model.activity_type
        return Activity(
            activity_id=model.activity_id,
            user_id=model.user_id,
            activity_type=activity_type,
            duration_minutes=model.duration_minutes,
            calories_burned=model.calories_burned,
            distance_km=model.distance_km,
            started_at=model.started_at,
            created_at=model.created_at
        )

    def _to_model(self, entity: Activity) -> ActivityModel:
        activity_type_value = entity.activity_type.value if isinstance(entity.activity_type, ActivityType) else str(entity.activity_type)
        return ActivityModel(
            activity_id=entity.activity_id,
            user_id=entity.user_id,
            activity_type=activity_type_value,
            duration_minutes=entity.duration_minutes,
            calories_burned=entity.calories_burned,
            distance_km=entity.distance_km,
            started_at=entity.started_at,
            created_at=entity.created_at
        )

    async def create(self, activity: Activity) -> Activity:
        model = self._to_model(activity)
        self.session.add(model)
        await self.session.commit()
        await self.session.refresh(model)
        return self._to_entity(model)

    async def get_by_id(self, activity_id: UUID) -> Optional[Activity]:
        result = await self.session.execute(
            select(ActivityModel).where(ActivityModel.activity_id == activity_id)
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def get_by_user_id(self, user_id: UUID, limit: int = 100) -> List[Activity]:
        result = await self.session.execute(
            select(ActivityModel)
            .where(ActivityModel.user_id == user_id)
            .order_by(ActivityModel.started_at.desc())
            .limit(limit)
        )
        models = result.scalars().all()
        return [self._to_entity(model) for model in models]

    async def update(self, activity: Activity) -> Activity:
        result = await self.session.execute(
            select(ActivityModel).where(ActivityModel.activity_id == activity.activity_id)
        )
        model = result.scalar_one()
        model.duration_minutes = activity.duration_minutes
        model.calories_burned = activity.calories_burned
        model.distance_km = activity.distance_km
        await self.session.commit()
        await self.session.refresh(model)
        return self._to_entity(model)

    async def delete(self, activity_id: UUID) -> bool:
        result = await self.session.execute(
            select(ActivityModel).where(ActivityModel.activity_id == activity_id)
        )
        model = result.scalar_one_or_none()
        if not model:
            return False
        await self.session.delete(model)
        await self.session.commit()
        return True


class SQLAlchemyRecommendationRepository(RecommendationRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    def _to_entity(self, model: RecommendationModel) -> Recommendation:
        return Recommendation(
            recommendation_id=model.recommendation_id,
            user_id=model.user_id,
            message=model.message,
            created_at=model.created_at
        )

    def _to_model(self, entity: Recommendation) -> RecommendationModel:
        return RecommendationModel(
            recommendation_id=entity.recommendation_id,
            user_id=entity.user_id,
            message=entity.message,
            created_at=entity.created_at
        )

    async def create(self, recommendation: Recommendation) -> Recommendation:
        model = self._to_model(recommendation)
        self.session.add(model)
        await self.session.commit()
        await self.session.refresh(model)
        return self._to_entity(model)

    async def get_by_user_id(self, user_id: UUID, limit: int = 10) -> List[Recommendation]:
        result = await self.session.execute(
            select(RecommendationModel)
            .where(RecommendationModel.user_id == user_id)
            .order_by(RecommendationModel.created_at.desc())
            .limit(limit)
        )
        models = result.scalars().all()
        return [self._to_entity(model) for model in models]




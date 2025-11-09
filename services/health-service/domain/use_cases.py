from typing import Optional, List
from uuid import UUID
from datetime import datetime, timedelta

from domain.entities import HealthMetric, Activity, Recommendation, ActivityType
from domain.repositories import (
    HealthMetricRepository,
    ActivityRepository,
    RecommendationRepository
)


class CreateHealthMetricUseCase:
    def __init__(self, repository: HealthMetricRepository):
        self.repository = repository

    async def execute(
        self,
        user_id: UUID,
        steps: Optional[int] = None,
        calories: Optional[float] = None,
        heart_rate: Optional[int] = None,
        sleep_hours: Optional[float] = None
    ) -> HealthMetric:
        metric = HealthMetric(
            user_id=user_id,
            steps=steps,
            calories=calories,
            heart_rate=heart_rate,
            sleep_hours=sleep_hours
        )
        return await self.repository.create(metric)


class GetHealthMetricsUseCase:
    def __init__(self, repository: HealthMetricRepository):
        self.repository = repository

    async def execute(self, user_id: UUID, limit: int = 100) -> List[HealthMetric]:
        return await self.repository.get_by_user_id(user_id, limit)


class UpdateHealthMetricUseCase:
    def __init__(self, repository: HealthMetricRepository):
        self.repository = repository

    async def execute(
        self,
        metric_id: UUID,
        steps: Optional[int] = None,
        calories: Optional[float] = None,
        heart_rate: Optional[int] = None,
        sleep_hours: Optional[float] = None
    ) -> HealthMetric:
        metric = await self.repository.get_by_id(metric_id)
        if not metric:
            raise ValueError("Health metric not found")
        metric.update(steps=steps, calories=calories, heart_rate=heart_rate, sleep_hours=sleep_hours)
        return await self.repository.update(metric)


class CreateActivityUseCase:
    def __init__(self, repository: ActivityRepository):
        self.repository = repository

    async def execute(
        self,
        user_id: UUID,
        activity_type: ActivityType,
        duration_minutes: int,
        calories_burned: Optional[float] = None,
        distance_km: Optional[float] = None
    ) -> Activity:
        activity = Activity(
            user_id=user_id,
            activity_type=activity_type,
            duration_minutes=duration_minutes,
            calories_burned=calories_burned,
            distance_km=distance_km
        )
        return await self.repository.create(activity)


class GetActivitiesUseCase:
    def __init__(self, repository: ActivityRepository):
        self.repository = repository

    async def execute(self, user_id: UUID, limit: int = 100) -> List[Activity]:
        return await self.repository.get_by_user_id(user_id, limit)


class GenerateRecommendationUseCase:
    def __init__(
        self,
        metric_repository: HealthMetricRepository,
        activity_repository: ActivityRepository,
        recommendation_repository: RecommendationRepository
    ):
        self.metric_repository = metric_repository
        self.activity_repository = activity_repository
        self.recommendation_repository = recommendation_repository

    async def execute(self, user_id: UUID, weather_data: Optional[dict] = None) -> Recommendation:
        recent_metrics = await self.metric_repository.get_by_user_id(user_id, limit=7)
        recent_activities = await self.activity_repository.get_by_user_id(user_id, limit=7)

        message_parts = []

        if recent_metrics:
            avg_steps = sum(m.steps or 0 for m in recent_metrics) / len(recent_metrics)
            if avg_steps < 5000:
                message_parts.append("Ваша средняя активность низкая. Рекомендуем увеличить количество шагов до 10000 в день.")
            elif avg_steps > 15000:
                message_parts.append("Отличная активность! Вы делаете много шагов.")

            avg_sleep = sum(m.sleep_hours or 0 for m in recent_metrics if m.sleep_hours) / max(len([m for m in recent_metrics if m.sleep_hours]), 1)
            if avg_sleep < 7:
                message_parts.append("Рекомендуем спать не менее 7-8 часов для восстановления.")
            elif avg_sleep > 9:
                message_parts.append("Вы спите достаточно, но возможно стоит проверить качество сна.")

        if recent_activities:
            total_duration = sum(a.duration_minutes for a in recent_activities)
            if total_duration < 150:
                message_parts.append("Рекомендуем заниматься физической активностью не менее 150 минут в неделю.")
            else:
                message_parts.append("Отличная работа! Вы поддерживаете регулярную физическую активность.")

        if weather_data:
            temp = weather_data.get("temp")
            if temp and temp < 10:
                message_parts.append("На улице холодно. Рекомендуем занятия в помещении или теплая одежда.")
            elif temp and temp > 25:
                message_parts.append("Жаркая погода. Не забывайте пить воду во время тренировок.")

        if not message_parts:
            message_parts.append("Продолжайте вести активный образ жизни!")

        message = " ".join(message_parts)
        recommendation = Recommendation(user_id=user_id, message=message)
        return await self.recommendation_repository.create(recommendation)




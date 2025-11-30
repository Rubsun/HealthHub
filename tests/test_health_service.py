import pytest
from uuid import uuid4
from datetime import datetime

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "services" / "health-service"))

from domain.entities import HealthMetric, Activity, ActivityType, Recommendation
from domain.use_cases import (
    CreateHealthMetricUseCase,
    CreateActivityUseCase,
    GenerateRecommendationUseCase
)


class MockHealthMetricRepository:
    def __init__(self):
        self.metrics = []

    async def create(self, metric: HealthMetric) -> HealthMetric:
        self.metrics.append(metric)
        return metric

    async def get_by_user_id(self, user_id, limit=100):
        return [m for m in self.metrics if m.user_id == user_id][:limit]

    async def get_by_id(self, metric_id):
        for m in self.metrics:
            if m.metric_id == metric_id:
                return m
        return None

    async def update(self, metric: HealthMetric) -> HealthMetric:
        for i, m in enumerate(self.metrics):
            if m.metric_id == metric.metric_id:
                self.metrics[i] = metric
                return metric
        return metric

    async def delete(self, metric_id):
        self.metrics = [m for m in self.metrics if m.metric_id != metric_id]
        return True


class MockActivityRepository:
    def __init__(self):
        self.activities = []

    async def create(self, activity: Activity) -> Activity:
        self.activities.append(activity)
        return activity

    async def get_by_user_id(self, user_id, limit=100):
        return [a for a in self.activities if a.user_id == user_id][:limit]

    async def get_by_id(self, activity_id):
        for a in self.activities:
            if a.activity_id == activity_id:
                return a
        return None

    async def update(self, activity: Activity) -> Activity:
        for i, a in enumerate(self.activities):
            if a.activity_id == activity.activity_id:
                self.activities[i] = activity
                return activity
        return activity

    async def delete(self, activity_id):
        self.activities = [a for a in self.activities if a.activity_id != activity_id]
        return True


class MockRecommendationRepository:
    def __init__(self):
        self.recommendations = []

    async def create(self, recommendation: Recommendation) -> Recommendation:
        self.recommendations.append(recommendation)
        return recommendation

    async def get_by_user_id(self, user_id, limit=10):
        return [r for r in self.recommendations if r.user_id == user_id][:limit]


@pytest.mark.asyncio
async def test_create_health_metric_use_case():
    repository = MockHealthMetricRepository()
    use_case = CreateHealthMetricUseCase(repository)
    user_id = uuid4()
    
    metric = await use_case.execute(user_id, steps=10000, calories=2000.0, heart_rate=75)
    
    assert metric.user_id == user_id
    assert metric.steps == 10000
    assert metric.calories == 2000.0
    assert metric.heart_rate == 75


@pytest.mark.asyncio
async def test_create_activity_use_case():
    repository = MockActivityRepository()
    use_case = CreateActivityUseCase(repository)
    user_id = uuid4()
    
    activity = await use_case.execute(
        user_id,
        ActivityType.RUNNING,
        duration_minutes=30,
        calories_burned=300.0,
        distance_km=5.0
    )
    
    assert activity.user_id == user_id
    assert activity.activity_type == ActivityType.RUNNING
    assert activity.duration_minutes == 30
    assert activity.calories_burned == 300.0
    assert activity.distance_km == 5.0


@pytest.mark.asyncio
async def test_generate_recommendation_use_case():
    metric_repo = MockHealthMetricRepository()
    activity_repo = MockActivityRepository()
    recommendation_repo = MockRecommendationRepository()
    use_case = GenerateRecommendationUseCase(metric_repo, activity_repo, recommendation_repo)
    user_id = uuid4()
    
    metric = HealthMetric(user_id=user_id, steps=3000, sleep_hours=6.0)
    await metric_repo.create(metric)
    
    recommendation = await use_case.execute(user_id)
    
    assert recommendation.user_id == user_id
    assert len(recommendation.message) > 0


def test_health_metric_entity():
    user_id = uuid4()
    metric = HealthMetric(
        user_id=user_id,
        steps=10000,
        calories=2000.0,
        heart_rate=75,
        sleep_hours=8.0
    )
    
    assert metric.user_id == user_id
    assert metric.steps == 10000
    assert metric.metric_id is not None


def test_activity_entity():
    user_id = uuid4()
    activity = Activity(
        user_id=user_id,
        activity_type=ActivityType.RUNNING,
        duration_minutes=30
    )
    
    assert activity.user_id == user_id
    assert activity.activity_type == ActivityType.RUNNING
    assert activity.duration_minutes == 30
    assert activity.activity_id is not None


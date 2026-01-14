import pytest
from uuid import uuid4
from datetime import datetime
import importlib.util
from pathlib import Path


def load_module_from_path(module_name: str, file_path: Path):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


service_path = Path(__file__).parent.parent / "services" / "health-service"
entities_module = load_module_from_path("health_entities", service_path / "domain" / "entities.py")

HealthMetric = entities_module.HealthMetric
Activity = entities_module.Activity
ActivityType = entities_module.ActivityType
Recommendation = entities_module.Recommendation


class MockHealthMetricRepository:
    def __init__(self):
        self.metrics = []

    async def create(self, metric) -> object:
        self.metrics.append(metric)
        return metric

    async def get_by_user_id(self, user_id, limit=100):
        return [m for m in self.metrics if m.user_id == user_id][:limit]

    async def get_by_id(self, metric_id):
        for m in self.metrics:
            if m.metric_id == metric_id:
                return m
        return None

    async def update(self, metric) -> object:
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

    async def create(self, activity) -> object:
        self.activities.append(activity)
        return activity

    async def get_by_user_id(self, user_id, limit=100):
        return [a for a in self.activities if a.user_id == user_id][:limit]

    async def get_by_id(self, activity_id):
        for a in self.activities:
            if a.activity_id == activity_id:
                return a
        return None

    async def update(self, activity) -> object:
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

    async def create(self, recommendation) -> object:
        self.recommendations.append(recommendation)
        return recommendation

    async def get_by_user_id(self, user_id, limit=10):
        return [r for r in self.recommendations if r.user_id == user_id][:limit]


@pytest.mark.asyncio
async def test_create_health_metric():
    repository = MockHealthMetricRepository()
    user_id = uuid4()
    metric = HealthMetric(user_id=user_id, steps=10000, calories=2000.0, heart_rate=75)
    created = await repository.create(metric)
    assert created.user_id == user_id
    assert created.steps == 10000
    assert created.calories == 2000.0
    assert created.heart_rate == 75


@pytest.mark.asyncio
async def test_create_activity():
    repository = MockActivityRepository()
    user_id = uuid4()
    activity = Activity(
        user_id=user_id,
        activity_type=ActivityType.RUNNING,
        duration_minutes=30,
        calories_burned=300.0,
        distance_km=5.0
    )
    created = await repository.create(activity)
    assert created.user_id == user_id
    assert created.activity_type == ActivityType.RUNNING
    assert created.duration_minutes == 30
    assert created.calories_burned == 300.0
    assert created.distance_km == 5.0


@pytest.mark.asyncio
async def test_create_recommendation():
    repository = MockRecommendationRepository()
    user_id = uuid4()
    recommendation = Recommendation(user_id=user_id, message="Test recommendation")
    created = await repository.create(recommendation)
    assert created.user_id == user_id
    assert created.message == "Test recommendation"


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


def test_activity_types():
    assert ActivityType.WALKING.value == "walking"
    assert ActivityType.RUNNING.value == "running"
    assert ActivityType.CYCLING.value == "cycling"
    assert ActivityType.SWIMMING.value == "swimming"
    assert ActivityType.GYM.value == "gym"
    assert ActivityType.OTHER.value == "other"

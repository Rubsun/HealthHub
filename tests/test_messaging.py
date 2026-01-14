import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "shared"))

import json
from datetime import datetime
from unittest.mock import patch
from uuid import uuid4

import pytest
from events import (
    ActivityCreatedEvent,
    Exchanges,
    FoodCreatedEvent,
    HealthMetricCreatedEvent,
    MealLoggedEvent,
    Queues,
    RoutingKeys,
    UserCreatedEvent,
    UserDeletedEvent,
    WeatherFetchRequestEvent,
    WeatherUpdatedEvent,
)


@pytest.fixture(autouse=True)
def mock_settings():
    with patch.dict('os.environ', {
        'DATABASE_URL': 'postgresql+asyncpg://test:test@localhost:5432/test',
        'RABBITMQ_URL': 'amqp://guest:guest@localhost:5672/'
    }):
        yield


class TestUserEvents:

    def test_user_created_event_schema(self):
        user_id = uuid4()
        event = UserCreatedEvent(
            user_id=user_id,
            email="test@example.com",
            full_name="Test User"
        )

        assert event.user_id == user_id
        assert event.email == "test@example.com"
        assert event.full_name == "Test User"
        assert event.timestamp is not None

    def test_user_deleted_event_schema(self):
        user_id = uuid4()
        event = UserDeletedEvent(user_id=user_id)

        assert event.user_id == user_id


class TestHealthEvents:

    def test_health_metric_created_event_schema(self):
        metric_id = uuid4()
        user_id = uuid4()
        recorded_at = datetime.utcnow()

        event = HealthMetricCreatedEvent(
            metric_id=metric_id,
            user_id=user_id,
            steps=10000,
            calories=2000.0,
            heart_rate=75,
            sleep_hours=8.0,
            recorded_at=recorded_at
        )

        assert event.metric_id == metric_id
        assert event.user_id == user_id
        assert event.steps == 10000
        assert event.calories == 2000.0
        assert event.heart_rate == 75
        assert event.sleep_hours == 8.0
        assert event.recorded_at == recorded_at

    def test_activity_created_event_schema(self):
        activity_id = uuid4()
        user_id = uuid4()
        started_at = datetime.utcnow()

        event = ActivityCreatedEvent(
            activity_id=activity_id,
            user_id=user_id,
            activity_type="running",
            duration_minutes=30,
            calories_burned=300.0,
            distance_km=5.0,
            started_at=started_at
        )

        assert event.activity_id == activity_id
        assert event.user_id == user_id
        assert event.activity_type == "running"
        assert event.duration_minutes == 30


class TestNutritionEvents:

    def test_meal_logged_event_schema(self):
        meal_id = uuid4()
        user_id = uuid4()
        food_id = uuid4()
        consumed_at = datetime.utcnow()

        event = MealLoggedEvent(
            meal_id=meal_id,
            user_id=user_id,
            food_id=food_id,
            quantity_grams=150.0,
            consumed_at=consumed_at
        )

        assert event.meal_id == meal_id
        assert event.user_id == user_id
        assert event.food_id == food_id
        assert event.quantity_grams == 150.0

    def test_food_created_event_schema(self):
        food_id = uuid4()

        event = FoodCreatedEvent(
            food_id=food_id,
            name="Apple",
            barcode="1234567890",
            calories_per_100g=52.0
        )

        assert event.food_id == food_id
        assert event.name == "Apple"
        assert event.barcode == "1234567890"
        assert event.calories_per_100g == 52.0


class TestIntegrationEvents:

    def test_weather_fetch_request_event_schema(self):
        user_id = uuid4()

        event = WeatherFetchRequestEvent(
            city="Moscow",
            user_id=user_id
        )

        assert event.city == "Moscow"
        assert event.user_id == user_id

    def test_weather_updated_event_schema(self):
        recorded_at = datetime.utcnow()

        event = WeatherUpdatedEvent(
            city="Moscow",
            temperature=15.5,
            description="clear sky",
            humidity=60,
            wind_speed=3.2,
            recorded_at=recorded_at
        )

        assert event.city == "Moscow"
        assert event.temperature == 15.5
        assert event.description == "clear sky"
        assert event.humidity == 60
        assert event.wind_speed == 3.2


class TestExchangesAndQueues:

    def test_exchanges_defined(self):
        assert Exchanges.USERS == "users.events"
        assert Exchanges.HEALTH == "health.events"
        assert Exchanges.NUTRITION == "nutrition.events"
        assert Exchanges.INTEGRATIONS == "integrations.events"

    def test_queues_defined(self):
        assert Queues.HEALTH_USER_CREATED == "health.user.created"
        assert Queues.HEALTH_USER_DELETED == "health.user.deleted"
        assert Queues.NUTRITION_USER_CREATED == "nutrition.user.created"
        assert Queues.INTEGRATIONS_WEATHER_FETCH == "integrations.weather.fetch"

    def test_routing_keys_defined(self):
        assert RoutingKeys.USER_CREATED == "user.created"
        assert RoutingKeys.USER_DELETED == "user.deleted"
        assert RoutingKeys.ACTIVITY_CREATED == "activity.created"
        assert RoutingKeys.WEATHER_FETCH == "weather.fetch"


class TestEventSerialization:

    def test_event_json_serialization(self):
        user_id = uuid4()
        event = UserCreatedEvent(
            user_id=user_id,
            email="test@example.com",
            full_name="Test User"
        )

        json_str = event.model_dump_json()
        assert json_str is not None

        data = json.loads(json_str)
        assert data["email"] == "test@example.com"
        assert data["full_name"] == "Test User"

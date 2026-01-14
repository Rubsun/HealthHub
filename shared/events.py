from datetime import datetime
from typing import Optional
from uuid import UUID
from enum import Enum

from pydantic import BaseModel, Field


class Exchanges:
    """Exchange names for RabbitMQ."""
    USERS = "users.events"
    HEALTH = "health.events"
    NUTRITION = "nutrition.events"
    INTEGRATIONS = "integrations.events"


class Queues:
    """Queue names for RabbitMQ consumers."""
    # Health service queues
    HEALTH_USER_CREATED = "health.user.created"
    HEALTH_USER_DELETED = "health.user.deleted"
    HEALTH_WEATHER_UPDATED = "health.weather.updated"
    
    # Nutrition service queues
    NUTRITION_USER_CREATED = "nutrition.user.created"
    NUTRITION_USER_DELETED = "nutrition.user.deleted"
    
    # Integrations service queues
    INTEGRATIONS_WEATHER_FETCH = "integrations.weather.fetch"
    INTEGRATIONS_ACTIVITY_CREATED = "integrations.activity.created"
    
    # Recommendations queue
    RECOMMENDATIONS_GENERATE = "recommendations.generate"


class RoutingKeys:
    """Routing keys for message routing."""
    USER_CREATED = "user.created"
    USER_UPDATED = "user.updated"
    USER_DELETED = "user.deleted"
    
    HEALTH_METRIC_CREATED = "health.metric.created"
    ACTIVITY_CREATED = "activity.created"
    RECOMMENDATION_GENERATED = "recommendation.generated"
    
    MEAL_LOGGED = "meal.logged"
    
    WEATHER_FETCH = "weather.fetch"
    WEATHER_UPDATED = "weather.updated"


class BaseEvent(BaseModel):
    """Base class for all events."""
    event_id: str = Field(default_factory=lambda: str(UUID(int=0)))
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v)
        }


class UserCreatedEvent(BaseEvent):
    """Event published when a new user is created."""
    user_id: UUID
    email: str
    full_name: Optional[str] = None


class UserUpdatedEvent(BaseEvent):
    """Event published when a user is updated."""
    user_id: UUID
    full_name: Optional[str] = None


class UserDeletedEvent(BaseEvent):
    """Event published when a user is deleted."""
    user_id: UUID


class HealthMetricCreatedEvent(BaseEvent):
    """Event published when a health metric is recorded."""
    metric_id: UUID
    user_id: UUID
    steps: Optional[int] = None
    calories: Optional[float] = None
    heart_rate: Optional[int] = None
    sleep_hours: Optional[float] = None
    recorded_at: datetime


class ActivityCreatedEvent(BaseEvent):
    """Event published when an activity is logged."""
    activity_id: UUID
    user_id: UUID
    activity_type: str
    duration_minutes: int
    calories_burned: Optional[float] = None
    distance_km: Optional[float] = None
    started_at: datetime


class RecommendationRequestEvent(BaseEvent):
    """Event to request recommendation generation."""
    user_id: UUID
    include_weather: bool = True
    city: Optional[str] = None


class RecommendationGeneratedEvent(BaseEvent):
    """Event published when a recommendation is generated."""
    recommendation_id: UUID
    user_id: UUID
    message: str


class MealLoggedEvent(BaseEvent):
    """Event published when a meal is logged."""
    meal_id: UUID
    user_id: UUID
    food_id: UUID
    quantity_grams: float
    consumed_at: datetime


class FoodCreatedEvent(BaseEvent):
    """Event published when a new food item is created."""
    food_id: UUID
    name: str
    barcode: Optional[str] = None
    calories_per_100g: Optional[float] = None


class WeatherFetchRequestEvent(BaseEvent):
    """Event to request weather data fetch."""
    city: str
    user_id: Optional[UUID] = None


class WeatherUpdatedEvent(BaseEvent):
    """Event published when weather data is updated."""
    city: str
    temperature: float
    description: str
    humidity: Optional[int] = None
    wind_speed: Optional[float] = None
    recorded_at: datetime


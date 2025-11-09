from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4
from enum import Enum


class ActivityType(str, Enum):
    WALKING = "walking"
    RUNNING = "running"
    CYCLING = "cycling"
    SWIMMING = "swimming"
    GYM = "gym"
    OTHER = "other"


class HealthMetric:
    def __init__(
        self,
        user_id: UUID,
        steps: Optional[int] = None,
        calories: Optional[float] = None,
        heart_rate: Optional[int] = None,
        sleep_hours: Optional[float] = None,
        metric_id: Optional[UUID] = None,
        recorded_at: Optional[datetime] = None,
        created_at: Optional[datetime] = None
    ):
        self.metric_id = metric_id or uuid4()
        self.user_id = user_id
        self.steps = steps
        self.calories = calories
        self.heart_rate = heart_rate
        self.sleep_hours = sleep_hours
        self.recorded_at = recorded_at or datetime.utcnow()
        self.created_at = created_at or datetime.utcnow()

    def update(
        self,
        steps: Optional[int] = None,
        calories: Optional[float] = None,
        heart_rate: Optional[int] = None,
        sleep_hours: Optional[float] = None
    ):
        if steps is not None:
            self.steps = steps
        if calories is not None:
            self.calories = calories
        if heart_rate is not None:
            self.heart_rate = heart_rate
        if sleep_hours is not None:
            self.sleep_hours = sleep_hours
        self.recorded_at = datetime.utcnow()


class Activity:
    def __init__(
        self,
        user_id: UUID,
        activity_type: ActivityType,
        duration_minutes: int,
        calories_burned: Optional[float] = None,
        distance_km: Optional[float] = None,
        activity_id: Optional[UUID] = None,
        started_at: Optional[datetime] = None,
        created_at: Optional[datetime] = None
    ):
        self.activity_id = activity_id or uuid4()
        self.user_id = user_id
        self.activity_type = activity_type
        self.duration_minutes = duration_minutes
        self.calories_burned = calories_burned
        self.distance_km = distance_km
        self.started_at = started_at or datetime.utcnow()
        self.created_at = created_at or datetime.utcnow()

    def update(
        self,
        duration_minutes: Optional[int] = None,
        calories_burned: Optional[float] = None,
        distance_km: Optional[float] = None
    ):
        if duration_minutes is not None:
            self.duration_minutes = duration_minutes
        if calories_burned is not None:
            self.calories_burned = calories_burned
        if distance_km is not None:
            self.distance_km = distance_km


class Recommendation:
    def __init__(
        self,
        user_id: UUID,
        message: str,
        recommendation_id: Optional[UUID] = None,
        created_at: Optional[datetime] = None
    ):
        self.recommendation_id = recommendation_id or uuid4()
        self.user_id = user_id
        self.message = message
        self.created_at = created_at or datetime.utcnow()




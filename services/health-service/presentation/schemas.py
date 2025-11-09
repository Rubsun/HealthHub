from datetime import datetime
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel

from domain.entities import ActivityType


class HealthMetricCreate(BaseModel):
    steps: Optional[int] = None
    calories: Optional[float] = None
    heart_rate: Optional[int] = None
    sleep_hours: Optional[float] = None


class HealthMetricUpdate(BaseModel):
    steps: Optional[int] = None
    calories: Optional[float] = None
    heart_rate: Optional[int] = None
    sleep_hours: Optional[float] = None


class HealthMetricResponse(BaseModel):
    metric_id: UUID
    user_id: UUID
    steps: Optional[int]
    calories: Optional[float]
    heart_rate: Optional[int]
    sleep_hours: Optional[float]
    recorded_at: datetime
    created_at: datetime

    class Config:
        from_attributes = True


class ActivityCreate(BaseModel):
    activity_type: ActivityType
    duration_minutes: int
    calories_burned: Optional[float] = None
    distance_km: Optional[float] = None


class ActivityUpdate(BaseModel):
    duration_minutes: Optional[int] = None
    calories_burned: Optional[float] = None
    distance_km: Optional[float] = None


class ActivityResponse(BaseModel):
    activity_id: UUID
    user_id: UUID
    activity_type: ActivityType
    duration_minutes: int
    calories_burned: Optional[float]
    distance_km: Optional[float]
    started_at: datetime
    created_at: datetime

    class Config:
        from_attributes = True


class RecommendationResponse(BaseModel):
    recommendation_id: UUID
    user_id: UUID
    message: str
    created_at: datetime

    class Config:
        from_attributes = True




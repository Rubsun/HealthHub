from datetime import datetime
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None


class UserResponse(BaseModel):
    user_id: UUID
    email: str
    full_name: Optional[str]
    created_at: datetime
    updated_at: datetime


class UserUpdate(BaseModel):
    full_name: Optional[str] = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class HealthMetricCreate(BaseModel):
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


class ActivityCreate(BaseModel):
    activity_type: str
    duration_minutes: int
    calories_burned: Optional[float] = None
    distance_km: Optional[float] = None


class ActivityResponse(BaseModel):
    activity_id: UUID
    user_id: UUID
    activity_type: str
    duration_minutes: int
    calories_burned: Optional[float]
    distance_km: Optional[float]
    started_at: datetime
    created_at: datetime


class RecommendationResponse(BaseModel):
    recommendation_id: UUID
    user_id: UUID
    message: str
    created_at: datetime


class FoodCreate(BaseModel):
    name: str
    barcode: Optional[str] = None
    calories_per_100g: Optional[float] = None
    proteins: Optional[float] = None
    carbs: Optional[float] = None
    fats: Optional[float] = None


class FoodResponse(BaseModel):
    food_id: UUID
    name: str
    barcode: Optional[str]
    calories_per_100g: Optional[float]
    proteins: Optional[float]
    carbs: Optional[float]
    fats: Optional[float]
    created_at: datetime


class MealCreate(BaseModel):
    food_id: UUID
    quantity_grams: float


class MealResponse(BaseModel):
    meal_id: UUID
    user_id: UUID
    food_id: UUID
    quantity_grams: float
    consumed_at: datetime
    created_at: datetime


class WeatherFetchRequest(BaseModel):
    city: str


class WeatherLogResponse(BaseModel):
    log_id: UUID
    city: str
    temperature: float
    description: str
    humidity: Optional[int]
    wind_speed: Optional[float]
    recorded_at: datetime
    created_at: datetime




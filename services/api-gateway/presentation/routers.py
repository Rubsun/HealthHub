import logging
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, HTTPException, Depends, Header
from fastapi.security import HTTPBearer
from faststream.rabbit import RabbitBroker

from infrastructure.settings import settings
from infrastructure.http_client import HTTPClient
from infrastructure.auth import create_access_token
from presentation.schemas import (
    UserCreate,
    UserResponse,
    UserUpdate,
    LoginRequest,
    TokenResponse,
    HealthMetricCreate,
    HealthMetricResponse,
    ActivityCreate,
    ActivityResponse,
    RecommendationResponse,
    FoodCreate,
    FoodResponse,
    MealCreate,
    MealResponse,
    WeatherFetchRequest,
    WeatherLogResponse
)
from presentation.dependencies import get_current_user_id

logger = logging.getLogger(__name__)

auth_router = APIRouter()
users_router = APIRouter()
health_router = APIRouter()
nutrition_router = APIRouter()
integrations_router = APIRouter()

users_client = HTTPClient(settings.users_service_url)
health_client = HTTPClient(settings.health_service_url)
nutrition_client = HTTPClient(settings.nutrition_service_url)
integrations_client = HTTPClient(settings.integrations_service_url)

_broker_instance = None

def get_broker():
    global _broker_instance
    if _broker_instance is None:
        _broker_instance = RabbitBroker(settings.rabbitmq_url)
    return _broker_instance


@auth_router.post("/register", response_model=UserResponse, status_code=201)
async def register(user_data: UserCreate):
    user_data_dict = user_data.model_dump()
    result = await users_client.post("/api/v1/users/", data=user_data_dict)
    if not result:
        raise HTTPException(status_code=500, detail="Failed to create user")
    return UserResponse(**result)


@auth_router.post("/login", response_model=TokenResponse)
async def login(credentials: LoginRequest):
    user_data = await users_client.get(f"/api/v1/users/email/{credentials.email}")
    if not user_data:
        logger.warning(f"User not found: {credentials.email}")
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    password_check = await users_client.post(
        "/api/v1/users/verify-password",
        data={"email": credentials.email, "password": credentials.password}
    )
    logger.info(f"Password check result: {password_check}")
    if not password_check:
        logger.warning(f"Password check returned None for {credentials.email}")
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    is_valid = password_check.get("valid", False)
    if not is_valid:
        logger.warning(f"Password validation failed for {credentials.email}")
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    access_token = create_access_token(data={"sub": str(user_data["user_id"])})
    return TokenResponse(access_token=access_token)


@users_router.post("/", response_model=UserResponse, status_code=201)
async def create_user(user_data: UserCreate, user_id: UUID = Depends(get_current_user_id)):
    user_data_dict = user_data.model_dump()
    result = await users_client.post("/api/v1/users/", data=user_data_dict)
    if not result:
        raise HTTPException(status_code=500, detail="Failed to create user")
    return UserResponse(**result)


@users_router.get("/me", response_model=UserResponse)
async def get_current_user(user_id: UUID = Depends(get_current_user_id)):
    result = await users_client.get(f"/api/v1/users/{user_id}")
    if not result:
        raise HTTPException(status_code=404, detail="User not found")
    return UserResponse(**result)


@users_router.put("/me", response_model=UserResponse)
async def update_current_user(
    user_data: UserUpdate,
    user_id: UUID = Depends(get_current_user_id)
):
    result = await users_client.put(f"/api/v1/users/{user_id}", data=user_data.model_dump())
    if not result:
        raise HTTPException(status_code=404, detail="User not found")
    return UserResponse(**result)


@health_router.post("/metrics", response_model=HealthMetricResponse, status_code=201)
async def create_health_metric(
    metric_data: HealthMetricCreate,
    user_id: UUID = Depends(get_current_user_id)
):
    headers = {"X-User-Id": str(user_id)}
    result = await health_client.post(
        "/api/v1/health-metrics/",
        data=metric_data.model_dump(),
        headers=headers
    )
    if not result:
        raise HTTPException(status_code=500, detail="Failed to create health metric")
    return HealthMetricResponse(**result)


@health_router.get("/metrics", response_model=List[HealthMetricResponse])
async def get_health_metrics(
    limit: int = 100,
    user_id: UUID = Depends(get_current_user_id)
):
    headers = {"X-User-Id": str(user_id)}
    result = await health_client.get(f"/api/v1/health-metrics/?limit={limit}", headers=headers)
    if not result:
        return []
    return [HealthMetricResponse(**item) for item in result]


@health_router.post("/activities", response_model=ActivityResponse, status_code=201)
async def create_activity(
    activity_data: ActivityCreate,
    user_id: UUID = Depends(get_current_user_id)
):
    headers = {"X-User-Id": str(user_id)}
    data = activity_data.model_dump()
    if "activity_type" in data and isinstance(data["activity_type"], str):
        data["activity_type"] = data["activity_type"].lower()
    result = await health_client.post(
        "/api/v1/activities/",
        data=data,
        headers=headers
    )
    if not result:
        raise HTTPException(status_code=500, detail="Failed to create activity")
    return ActivityResponse(**result)


@health_router.get("/activities", response_model=List[ActivityResponse])
async def get_activities(
    limit: int = 100,
    user_id: UUID = Depends(get_current_user_id)
):
    headers = {"X-User-Id": str(user_id)}
    result = await health_client.get(f"/api/v1/activities/?limit={limit}", headers=headers)
    if not result:
        return []
    return [ActivityResponse(**item) for item in result]


@health_router.post("/recommendations", response_model=RecommendationResponse, status_code=201)
async def generate_recommendation(user_id: UUID = Depends(get_current_user_id)):
    headers = {"X-User-Id": str(user_id)}
    result = await health_client.post("/api/v1/recommendations/", headers=headers)
    if not result:
        raise HTTPException(status_code=500, detail="Failed to generate recommendation")
    return RecommendationResponse(**result)


@nutrition_router.post("/foods", response_model=FoodResponse, status_code=201)
async def create_food(food_data: FoodCreate):
    result = await nutrition_client.post("/api/v1/foods/", data=food_data.model_dump())
    if not result:
        raise HTTPException(status_code=500, detail="Failed to create food")
    return FoodResponse(**result)


@nutrition_router.get("/foods/search", response_model=List[FoodResponse])
async def search_foods(query: str, limit: int = 20):
    result = await nutrition_client.get(f"/api/v1/foods/search?query={query}&limit={limit}")
    if not result:
        return []
    return [FoodResponse(**item) for item in result]


@nutrition_router.get("/foods/barcode/{barcode}", response_model=FoodResponse)
async def get_food_by_barcode(barcode: str):
    result = await nutrition_client.get(f"/api/v1/foods/barcode/{barcode}")
    if not result:
        raise HTTPException(status_code=404, detail="Food not found")
    return FoodResponse(**result)


@nutrition_router.post("/meals", response_model=MealResponse, status_code=201)
async def create_meal(meal_data: MealCreate, user_id: UUID = Depends(get_current_user_id)):
    headers = {"X-User-Id": str(user_id)}
    result = await nutrition_client.post(
        "/api/v1/meals/",
        data=meal_data.model_dump(),
        headers=headers
    )
    if not result:
        raise HTTPException(status_code=500, detail="Failed to create meal")
    return MealResponse(**result)


@nutrition_router.get("/meals", response_model=List[MealResponse])
async def get_meals(limit: int = 100, user_id: UUID = Depends(get_current_user_id)):
    headers = {"X-User-Id": str(user_id)}
    result = await nutrition_client.get(f"/api/v1/meals/?limit={limit}", headers=headers)
    if not result:
        return []
    return [MealResponse(**item) for item in result]


@integrations_router.post("/weather/fetch", response_model=WeatherLogResponse, status_code=201)
async def fetch_weather(request: WeatherFetchRequest):
    result = await integrations_client.post(
        "/api/v1/weather/fetch",
        data=request.model_dump()
    )
    if not result:
        raise HTTPException(status_code=500, detail="Failed to fetch weather")
    
    try:
        broker = get_broker()
        await broker.connect()
        await broker.publish(request.city, "weather.fetch")
        await broker.close()
    except Exception as e:
        logger.warning(f"Failed to publish weather fetch message: {e}")
    
    return WeatherLogResponse(**result)


@integrations_router.get("/weather/{city}/latest", response_model=WeatherLogResponse)
async def get_latest_weather(city: str):
    result = await integrations_client.get(f"/api/v1/weather/{city}/latest")
    if not result:
        raise HTTPException(status_code=404, detail="Weather data not found")
    return WeatherLogResponse(**result)


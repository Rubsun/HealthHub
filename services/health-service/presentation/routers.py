import logging
from typing import List
from uuid import UUID

from fastapi import APIRouter, HTTPException, Depends, Header
from fastapi.security import HTTPBearer

from application.services import HealthMetricService, ActivityService, RecommendationService
from presentation.schemas import (
    HealthMetricCreate,
    HealthMetricUpdate,
    HealthMetricResponse,
    ActivityCreate,
    ActivityUpdate,
    ActivityResponse,
    RecommendationResponse
)
from domain.entities import ActivityType

logger = logging.getLogger(__name__)

router_health = APIRouter()
router_activities = APIRouter()
router_recommendations = APIRouter()

health_metrics_router = router_health
activities_router = router_activities
recommendations_router = router_recommendations

health_metric_service = HealthMetricService()
activity_service = ActivityService()
recommendation_service = RecommendationService()


def get_user_id_from_header(x_user_id: str = Header(...)) -> UUID:
    try:
        return UUID(x_user_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid user_id header")


@router_health.post("/", response_model=HealthMetricResponse, status_code=201)
async def create_health_metric(
    metric_data: HealthMetricCreate,
    user_id: UUID = Depends(get_user_id_from_header),
    service: HealthMetricService = Depends(lambda: health_metric_service)
):
    try:
        metric = await service.create_metric(
            user_id=user_id,
            steps=metric_data.steps,
            calories=metric_data.calories,
            heart_rate=metric_data.heart_rate,
            sleep_hours=metric_data.sleep_hours
        )
        return HealthMetricResponse(
            metric_id=metric.metric_id,
            user_id=metric.user_id,
            steps=metric.steps,
            calories=metric.calories,
            heart_rate=metric.heart_rate,
            sleep_hours=metric.sleep_hours,
            recorded_at=metric.recorded_at,
            created_at=metric.created_at
        )
    except Exception as e:
        logger.error(f"Error creating health metric: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router_health.get("/", response_model=List[HealthMetricResponse])
async def get_health_metrics(
    user_id: UUID = Depends(get_user_id_from_header),
    limit: int = 100,
    service: HealthMetricService = Depends(lambda: health_metric_service)
):
    metrics = await service.get_metrics(user_id, limit)
    return [
        HealthMetricResponse(
            metric_id=m.metric_id,
            user_id=m.user_id,
            steps=m.steps,
            calories=m.calories,
            heart_rate=m.heart_rate,
            sleep_hours=m.sleep_hours,
            recorded_at=m.recorded_at,
            created_at=m.created_at
        )
        for m in metrics
    ]


@router_health.put("/{metric_id}", response_model=HealthMetricResponse)
async def update_health_metric(
    metric_id: UUID,
    metric_data: HealthMetricUpdate,
    user_id: UUID = Depends(get_user_id_from_header),
    service: HealthMetricService = Depends(lambda: health_metric_service)
):
    try:
        metric = await service.update_metric(
            metric_id=metric_id,
            steps=metric_data.steps,
            calories=metric_data.calories,
            heart_rate=metric_data.heart_rate,
            sleep_hours=metric_data.sleep_hours
        )
        if metric.user_id != user_id:
            raise HTTPException(status_code=403, detail="Access denied")
        return HealthMetricResponse(
            metric_id=metric.metric_id,
            user_id=metric.user_id,
            steps=metric.steps,
            calories=metric.calories,
            heart_rate=metric.heart_rate,
            sleep_hours=metric.sleep_hours,
            recorded_at=metric.recorded_at,
            created_at=metric.created_at
        )
    except ValueError as e:
        logger.error(f"Error updating health metric: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error updating health metric: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router_activities.post("/", response_model=ActivityResponse, status_code=201)
async def create_activity(
    activity_data: ActivityCreate,
    user_id: UUID = Depends(get_user_id_from_header),
    service: ActivityService = Depends(lambda: activity_service)
):
    try:
        if isinstance(activity_data.activity_type, str):
            activity_type_str = activity_data.activity_type.lower()
            try:
                activity_type = ActivityType(activity_type_str)
            except ValueError:
                logger.error(f"Invalid activity type: {activity_data.activity_type}")
                raise HTTPException(status_code=400, detail=f"Invalid activity type: {activity_data.activity_type}")
        else:
            activity_type = activity_data.activity_type
        
        activity = await service.create_activity(
            user_id=user_id,
            activity_type=activity_type,
            duration_minutes=activity_data.duration_minutes,
            calories_burned=activity_data.calories_burned,
            distance_km=activity_data.distance_km
        )
        return ActivityResponse(
            activity_id=activity.activity_id,
            user_id=activity.user_id,
            activity_type=activity.activity_type,
            duration_minutes=activity.duration_minutes,
            calories_burned=activity.calories_burned,
            distance_km=activity.distance_km,
            started_at=activity.started_at,
            created_at=activity.created_at
        )
    except Exception as e:
        logger.error(f"Error creating activity: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router_activities.get("/", response_model=List[ActivityResponse])
async def get_activities(
    user_id: UUID = Depends(get_user_id_from_header),
    limit: int = 100,
    service: ActivityService = Depends(lambda: activity_service)
):
    activities = await service.get_activities(user_id, limit)
    return [
        ActivityResponse(
            activity_id=a.activity_id,
            user_id=a.user_id,
            activity_type=a.activity_type,
            duration_minutes=a.duration_minutes,
            calories_burned=a.calories_burned,
            distance_km=a.distance_km,
            started_at=a.started_at,
            created_at=a.created_at
        )
        for a in activities
    ]


@router_recommendations.post("/", response_model=RecommendationResponse, status_code=201)
async def generate_recommendation(
    user_id: UUID = Depends(get_user_id_from_header),
    service: RecommendationService = Depends(lambda: recommendation_service)
):
    try:
        recommendation = await service.generate_recommendation(user_id)
        return RecommendationResponse(
            recommendation_id=recommendation.recommendation_id,
            user_id=recommendation.user_id,
            message=recommendation.message,
            created_at=recommendation.created_at
        )
    except Exception as e:
        logger.error(f"Error generating recommendation: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router_recommendations.get("/", response_model=List[RecommendationResponse])
async def get_recommendations(
    user_id: UUID = Depends(get_user_id_from_header),
    limit: int = 10
):
    from infrastructure.repositories import SQLAlchemyRecommendationRepository
    from infrastructure.database import async_session_maker
    async with async_session_maker() as session:
        repository = SQLAlchemyRecommendationRepository(session)
        recommendations = await repository.get_by_user_id(user_id, limit)
        return [
            RecommendationResponse(
                recommendation_id=r.recommendation_id,
                user_id=r.user_id,
                message=r.message,
                created_at=r.created_at
            )
            for r in recommendations
        ]


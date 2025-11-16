import logging
from typing import List
from uuid import UUID

from fastapi import APIRouter, HTTPException, Depends
from faststream import FastStream
from faststream.rabbit import RabbitBroker

from application.services import WeatherService
from presentation.schemas import WeatherLogResponse, WeatherFetchRequest
from infrastructure.settings import settings

logger = logging.getLogger(__name__)

weather_router = APIRouter()
weather_service = WeatherService()

broker = RabbitBroker(settings.rabbitmq_url)


@weather_router.post("/fetch", response_model=WeatherLogResponse, status_code=201)
async def fetch_weather(request: WeatherFetchRequest):
    try:
        weather_log = await weather_service.fetch_and_save_weather(request.city)
        if not weather_log:
            raise HTTPException(status_code=500, detail="Failed to fetch weather data")
        return WeatherLogResponse(
            log_id=weather_log.log_id,
            city=weather_log.city,
            temperature=weather_log.temperature,
            description=weather_log.description,
            humidity=weather_log.humidity,
            wind_speed=weather_log.wind_speed,
            recorded_at=weather_log.recorded_at,
            created_at=weather_log.created_at
        )
    except Exception as e:
        logger.error(f"Error fetching weather: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@weather_router.get("/{city}/latest", response_model=WeatherLogResponse)
async def get_latest_weather(city: str):
    weather_log = await weather_service.get_latest_weather(city)
    if not weather_log:
        raise HTTPException(status_code=404, detail="Weather data not found")
    return WeatherLogResponse(
        log_id=weather_log.log_id,
        city=weather_log.city,
        temperature=weather_log.temperature,
        description=weather_log.description,
        humidity=weather_log.humidity,
        wind_speed=weather_log.wind_speed,
        recorded_at=weather_log.recorded_at,
        created_at=weather_log.created_at
    )


@weather_router.get("/{city}/history", response_model=List[WeatherLogResponse])
async def get_weather_history(city: str, limit: int = 10):
    logs = await weather_service.get_weather_history(city, limit)
    return [
        WeatherLogResponse(
            log_id=log.log_id,
            city=log.city,
            temperature=log.temperature,
            description=log.description,
            humidity=log.humidity,
            wind_speed=log.wind_speed,
            recorded_at=log.recorded_at,
            created_at=log.created_at
        )
        for log in logs
    ]




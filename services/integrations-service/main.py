import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from infrastructure.database import engine
from infrastructure.messaging import get_publisher, shutdown_publisher
from presentation.routers import weather_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Integrations service starting...")
    publisher = get_publisher()
    try:
        await publisher.connect()
        logger.info("Connected to RabbitMQ")
    except Exception as e:
        logger.warning(f"Failed to connect to RabbitMQ on startup: {e}")
    
    logger.info("Integrations service started")
    
    yield
    
    logger.info("Integrations service shutting down...")
    await shutdown_publisher()
    await engine.dispose()
    logger.info("Integrations service stopped")


app = FastAPI(
    title="Integrations Service",
    description="External API integrations service for HealthHub (OpenWeather)",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(weather_router, prefix="/api/v1/weather", tags=["weather"])


@app.get("/health")
async def health():
    return {"status": "ok", "service": "integrations-service"}

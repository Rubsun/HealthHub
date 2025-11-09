import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from infrastructure.database import engine
from presentation.routers import health_metrics_router, activities_router, recommendations_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Health service started")
    yield
    await engine.dispose()
    logger.info("Health service stopped")


app = FastAPI(
    title="Health Service",
    description="Health metrics and activities service",
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

app.include_router(health_metrics_router, prefix="/api/v1/health-metrics", tags=["health-metrics"])
app.include_router(activities_router, prefix="/api/v1/activities", tags=["activities"])
app.include_router(recommendations_router, prefix="/api/v1/recommendations", tags=["recommendations"])


@app.get("/health")
async def health():
    return {"status": "ok", "service": "health-service"}


@app.on_event("shutdown")
async def shutdown():
    await engine.dispose()
    logger.info("Database connections closed")


import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from infrastructure.settings import settings
from presentation.routers import (
    auth_router,
    users_router,
    health_router,
    nutrition_router,
    integrations_router
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("API Gateway started")
    yield
    logger.info("API Gateway stopped")


app = FastAPI(
    title="HealthHub API Gateway",
    description="API Gateway for HealthHub microservices",
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

app.include_router(auth_router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(users_router, prefix="/api/v1/users", tags=["users"])
app.include_router(health_router, prefix="/api/v1/health", tags=["health"])
app.include_router(nutrition_router, prefix="/api/v1/nutrition", tags=["nutrition"])
app.include_router(integrations_router, prefix="/api/v1/integrations", tags=["integrations"])


@app.get("/health")
async def health():
    return {"status": "ok", "service": "api-gateway"}


@app.get("/")
async def root():
    return {"message": "HealthHub API Gateway", "docs": "/docs"}




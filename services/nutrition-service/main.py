import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from infrastructure.database import engine
from presentation.routers import foods_router, meals_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Nutrition service started")
    yield
    await engine.dispose()
    logger.info("Nutrition service stopped")


app = FastAPI(
    title="Nutrition Service",
    description="Nutrition and food products service",
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

app.include_router(foods_router, prefix="/api/v1/foods", tags=["foods"])
app.include_router(meals_router, prefix="/api/v1/meals", tags=["meals"])


@app.get("/health")
async def health():
    return {"status": "ok", "service": "nutrition-service"}


@app.on_event("shutdown")
async def shutdown():
    await engine.dispose()
    logger.info("Database connections closed")


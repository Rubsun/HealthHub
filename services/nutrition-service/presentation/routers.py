import logging
from typing import List
from uuid import UUID

from fastapi import APIRouter, HTTPException, Depends, Header, Query

from application.services import FoodService, MealService
from presentation.schemas import FoodCreate, FoodResponse, MealCreate, MealResponse

logger = logging.getLogger(__name__)

foods_router = APIRouter()
meals_router = APIRouter()

food_service = FoodService()
meal_service = MealService()


def get_user_id_from_header(x_user_id: str = Header(...)) -> UUID:
    try:
        return UUID(x_user_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid user_id header")


@foods_router.post("/", response_model=FoodResponse, status_code=201)
async def create_food(
    food_data: FoodCreate,
    service: FoodService = Depends(lambda: food_service)
):
    try:
        food = await service.create_food(
            name=food_data.name,
            barcode=food_data.barcode,
            calories_per_100g=food_data.calories_per_100g,
            proteins=food_data.proteins,
            carbs=food_data.carbs,
            fats=food_data.fats
        )
        return FoodResponse(
            food_id=food.food_id,
            name=food.name,
            barcode=food.barcode,
            calories_per_100g=food.calories_per_100g,
            proteins=food.proteins,
            carbs=food.carbs,
            fats=food.fats,
            created_at=food.created_at
        )
    except Exception as e:
        logger.error(f"Error creating food: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@foods_router.get("/barcode/{barcode}", response_model=FoodResponse)
async def get_food_by_barcode(
    barcode: str,
    service: FoodService = Depends(lambda: food_service)
):
    food = await service.get_food_by_barcode(barcode)
    if not food:
        raise HTTPException(status_code=404, detail="Food not found")
    return FoodResponse(
        food_id=food.food_id,
        name=food.name,
        barcode=food.barcode,
        calories_per_100g=food.calories_per_100g,
        proteins=food.proteins,
        carbs=food.carbs,
        fats=food.fats,
        created_at=food.created_at
    )


@foods_router.get("/search", response_model=List[FoodResponse])
async def search_foods(
    query: str = Query(..., min_length=1),
    limit: int = Query(20, ge=1, le=100),
    service: FoodService = Depends(lambda: food_service)
):
    foods = await service.search_food(query, limit)
    return [
        FoodResponse(
            food_id=f.food_id,
            name=f.name,
            barcode=f.barcode,
            calories_per_100g=f.calories_per_100g,
            proteins=f.proteins,
            carbs=f.carbs,
            fats=f.fats,
            created_at=f.created_at
        )
        for f in foods
    ]


@meals_router.post("/", response_model=MealResponse, status_code=201)
async def create_meal(
    meal_data: MealCreate,
    user_id: UUID = Depends(get_user_id_from_header),
    service: MealService = Depends(lambda: meal_service)
):
    try:
        meal = await service.create_meal(user_id, meal_data.food_id, meal_data.quantity_grams)
        return MealResponse(
            meal_id=meal.meal_id,
            user_id=meal.user_id,
            food_id=meal.food_id,
            quantity_grams=meal.quantity_grams,
            consumed_at=meal.consumed_at,
            created_at=meal.created_at
        )
    except ValueError as e:
        logger.error(f"Error creating meal: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error creating meal: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@meals_router.get("/", response_model=List[MealResponse])
async def get_meals(
    user_id: UUID = Depends(get_user_id_from_header),
    limit: int = Query(100, ge=1, le=1000),
    service: MealService = Depends(lambda: meal_service)
):
    meals = await service.get_meals(user_id, limit)
    return [
        MealResponse(
            meal_id=m.meal_id,
            user_id=m.user_id,
            food_id=m.food_id,
            quantity_grams=m.quantity_grams,
            consumed_at=m.consumed_at,
            created_at=m.created_at
        )
        for m in meals
    ]




from typing import Optional, List
from uuid import UUID

from domain.use_cases import (
    CreateFoodUseCase,
    GetFoodByBarcodeUseCase,
    SearchFoodUseCase,
    CreateMealUseCase,
    GetMealsUseCase
)
from infrastructure.repositories import SQLAlchemyFoodRepository, SQLAlchemyMealRepository
from infrastructure.external_apis import OpenFoodFactsAPI
from infrastructure.database import async_session_maker


class FoodService:
    def __init__(self):
        self.api = OpenFoodFactsAPI()

    async def create_food(
        self,
        name: str,
        barcode: Optional[str] = None,
        calories_per_100g: Optional[float] = None,
        proteins: Optional[float] = None,
        carbs: Optional[float] = None,
        fats: Optional[float] = None
    ):
        async with async_session_maker() as session:
            repository = SQLAlchemyFoodRepository(session)
            use_case = CreateFoodUseCase(repository)
            return await use_case.execute(name, barcode, calories_per_100g, proteins, carbs, fats)

    async def get_food_by_barcode(self, barcode: str):
        async with async_session_maker() as session:
            repository = SQLAlchemyFoodRepository(session)
            use_case = GetFoodByBarcodeUseCase(repository, self.api)
            return await use_case.execute(barcode)

    async def search_food(self, query: str, limit: int = 20):
        async with async_session_maker() as session:
            repository = SQLAlchemyFoodRepository(session)
            use_case = SearchFoodUseCase(repository, self.api)
            return await use_case.execute(query, limit)


class MealService:
    async def create_meal(self, user_id: UUID, food_id: UUID, quantity_grams: float):
        async with async_session_maker() as session:
            meal_repository = SQLAlchemyMealRepository(session)
            food_repository = SQLAlchemyFoodRepository(session)
            use_case = CreateMealUseCase(meal_repository, food_repository)
            return await use_case.execute(user_id, food_id, quantity_grams)

    async def get_meals(self, user_id: UUID, limit: int = 100):
        async with async_session_maker() as session:
            repository = SQLAlchemyMealRepository(session)
            use_case = GetMealsUseCase(repository)
            return await use_case.execute(user_id, limit)




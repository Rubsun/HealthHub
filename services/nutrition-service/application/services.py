import logging
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
from infrastructure.messaging import get_publisher

logger = logging.getLogger(__name__)


class FoodService:
    """Service for food operations."""
    
    def __init__(self):
        self.api = OpenFoodFactsAPI()
        self._publisher = None
    
    @property
    def publisher(self):
        if self._publisher is None:
            self._publisher = get_publisher()
        return self._publisher
    
    async def create_food(
        self,
        name: str,
        barcode: Optional[str] = None,
        calories_per_100g: Optional[float] = None,
        proteins: Optional[float] = None,
        carbs: Optional[float] = None,
        fats: Optional[float] = None
    ):
        """Create a food item and publish event."""
        async with async_session_maker() as session:
            repository = SQLAlchemyFoodRepository(session)
            use_case = CreateFoodUseCase(repository)
            food = await use_case.execute(name, barcode, calories_per_100g, proteins, carbs, fats)
        
        try:
            await self.publisher.publish_food_created(
                food_id=food.food_id,
                name=food.name,
                barcode=food.barcode,
                calories_per_100g=food.calories_per_100g
            )
        except Exception as e:
            logger.warning(f"Failed to publish food.created event: {e}")
        
        return food

    async def get_food_by_barcode(self, barcode: str):
        """Get food by barcode, fetching from OpenFoodFacts if not in database."""
        async with async_session_maker() as session:
            repository = SQLAlchemyFoodRepository(session)
            use_case = GetFoodByBarcodeUseCase(repository, self.api)
            return await use_case.execute(barcode)

    async def search_food(self, query: str, limit: int = 20):
        """Search for food by name."""
        async with async_session_maker() as session:
            repository = SQLAlchemyFoodRepository(session)
            use_case = SearchFoodUseCase(repository, self.api)
            return await use_case.execute(query, limit)


class MealService:
    """Service for meal operations."""
    
    def __init__(self):
        self._publisher = None
    
    @property
    def publisher(self):
        if self._publisher is None:
            self._publisher = get_publisher()
        return self._publisher
    
    async def create_meal(self, user_id: UUID, food_id: UUID, quantity_grams: float):
        """Create a meal and publish event."""
        async with async_session_maker() as session:
            meal_repository = SQLAlchemyMealRepository(session)
            food_repository = SQLAlchemyFoodRepository(session)
            use_case = CreateMealUseCase(meal_repository, food_repository)
            meal = await use_case.execute(user_id, food_id, quantity_grams)
        
        try:
            await self.publisher.publish_meal_logged(
                meal_id=meal.meal_id,
                user_id=meal.user_id,
                food_id=meal.food_id,
                quantity_grams=meal.quantity_grams,
                consumed_at=meal.consumed_at
            )
        except Exception as e:
            logger.warning(f"Failed to publish meal.logged event: {e}")
        
        return meal

    async def get_meals(self, user_id: UUID, limit: int = 100):
        """Get meals for a user."""
        async with async_session_maker() as session:
            repository = SQLAlchemyMealRepository(session)
            use_case = GetMealsUseCase(repository)
            return await use_case.execute(user_id, limit)

from typing import Optional, List
from uuid import UUID

from domain.entities import Food, Meal
from domain.repositories import FoodRepository, MealRepository
from infrastructure.external_apis import OpenFoodFactsAPI


class CreateFoodUseCase:
    def __init__(self, repository: FoodRepository):
        self.repository = repository

    async def execute(
        self,
        name: str,
        barcode: Optional[str] = None,
        calories_per_100g: Optional[float] = None,
        proteins: Optional[float] = None,
        carbs: Optional[float] = None,
        fats: Optional[float] = None
    ) -> Food:
        food = Food(
            name=name,
            barcode=barcode,
            calories_per_100g=calories_per_100g,
            proteins=proteins,
            carbs=carbs,
            fats=fats
        )
        return await self.repository.create(food)


class GetFoodByBarcodeUseCase:
    def __init__(self, repository: FoodRepository, api: OpenFoodFactsAPI):
        self.repository = repository
        self.api = api

    async def execute(self, barcode: str) -> Optional[Food]:
        food = await self.repository.get_by_barcode(barcode)
        if food:
            return food
        
        product_data = await self.api.get_product_by_barcode(barcode)
        if product_data:
            food = Food(
                name=product_data["name"],
                barcode=barcode,
                calories_per_100g=product_data.get("calories_per_100g"),
                proteins=product_data.get("proteins"),
                carbs=product_data.get("carbs"),
                fats=product_data.get("fats")
            )
            return await self.repository.create(food)
        return None


class SearchFoodUseCase:
    def __init__(self, repository: FoodRepository, api: OpenFoodFactsAPI):
        self.repository = repository
        self.api = api

    async def execute(self, query: str, limit: int = 20) -> List[Food]:
        db_foods = await self.repository.search_by_name(query, limit)
        if len(db_foods) >= limit:
            return db_foods
        
        api_products = await self.api.search_product(query, limit)
        foods = []
        for product_data in api_products:
            if product_data["barcode"]:
                existing = await self.repository.get_by_barcode(product_data["barcode"])
                if existing:
                    foods.append(existing)
                    continue
            
            food = Food(
                name=product_data["name"],
                barcode=product_data.get("barcode"),
                calories_per_100g=product_data.get("calories_per_100g"),
                proteins=product_data.get("proteins"),
                carbs=product_data.get("carbs"),
                fats=product_data.get("fats")
            )
            created_food = await self.repository.create(food)
            foods.append(created_food)
        
        return db_foods + foods[:limit - len(db_foods)]


class CreateMealUseCase:
    def __init__(self, repository: MealRepository, food_repository: FoodRepository):
        self.repository = repository
        self.food_repository = food_repository

    async def execute(
        self,
        user_id: UUID,
        food_id: UUID,
        quantity_grams: float
    ) -> Meal:
        food = await self.food_repository.get_by_id(food_id)
        if not food:
            raise ValueError("Food not found")
        
        meal = Meal(
            user_id=user_id,
            food_id=food_id,
            quantity_grams=quantity_grams
        )
        return await self.repository.create(meal)


class GetMealsUseCase:
    def __init__(self, repository: MealRepository):
        self.repository = repository

    async def execute(self, user_id: UUID, limit: int = 100) -> List[Meal]:
        return await self.repository.get_by_user_id(user_id, limit)




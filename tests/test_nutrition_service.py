import pytest
from uuid import uuid4
from datetime import datetime

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "services" / "nutrition-service"))

from domain.entities import Food, Meal
from domain.use_cases import CreateFoodUseCase, CreateMealUseCase


class MockFoodRepository:
    def __init__(self):
        self.foods = {}

    async def create(self, food: Food) -> Food:
        self.foods[food.food_id] = food
        return food

    async def get_by_id(self, food_id):
        return self.foods.get(food_id)

    async def get_by_barcode(self, barcode: str):
        for food in self.foods.values():
            if food.barcode == barcode:
                return food
        return None

    async def search_by_name(self, name: str, limit=20):
        results = []
        for food in self.foods.values():
            if name.lower() in food.name.lower():
                results.append(food)
        return results[:limit]

    async def update(self, food: Food) -> Food:
        self.foods[food.food_id] = food
        return food


class MockMealRepository:
    def __init__(self):
        self.meals = {}

    async def create(self, meal: Meal) -> Meal:
        self.meals[meal.meal_id] = meal
        return meal

    async def get_by_id(self, meal_id):
        return self.meals.get(meal_id)

    async def get_by_user_id(self, user_id, limit=100):
        results = []
        for meal in self.meals.values():
            if meal.user_id == user_id:
                results.append(meal)
        return results[:limit]

    async def update(self, meal: Meal) -> Meal:
        self.meals[meal.meal_id] = meal
        return meal

    async def delete(self, meal_id):
        if meal_id in self.meals:
            del self.meals[meal_id]
            return True
        return False


@pytest.mark.asyncio
async def test_create_food_use_case():
    repository = MockFoodRepository()
    use_case = CreateFoodUseCase(repository)
    
    food = await use_case.execute(
        name="Apple",
        barcode="1234567890",
        calories_per_100g=52.0,
        proteins=0.3,
        carbs=14.0,
        fats=0.2
    )
    
    assert food.name == "Apple"
    assert food.barcode == "1234567890"
    assert food.calories_per_100g == 52.0
    assert food.proteins == 0.3
    assert food.carbs == 14.0
    assert food.fats == 0.2


@pytest.mark.asyncio
async def test_create_meal_use_case():
    food_repo = MockFoodRepository()
    meal_repo = MockMealRepository()
    
    food_use_case = CreateFoodUseCase(food_repo)
    meal_use_case = CreateMealUseCase(meal_repo, food_repo)
    
    user_id = uuid4()
    food = await food_use_case.execute(name="Apple", calories_per_100g=52.0)
    
    meal = await meal_use_case.execute(user_id, food.food_id, quantity_grams=150.0)
    
    assert meal.user_id == user_id
    assert meal.food_id == food.food_id
    assert meal.quantity_grams == 150.0


@pytest.mark.asyncio
async def test_create_meal_food_not_found():
    food_repo = MockFoodRepository()
    meal_repo = MockMealRepository()
    
    use_case = CreateMealUseCase(meal_repo, food_repo)
    user_id = uuid4()
    food_id = uuid4()
    
    with pytest.raises(ValueError, match="Food not found"):
        await use_case.execute(user_id, food_id, quantity_grams=150.0)


def test_food_entity():
    food = Food(
        name="Apple",
        barcode="1234567890",
        calories_per_100g=52.0
    )
    
    assert food.name == "Apple"
    assert food.barcode == "1234567890"
    assert food.calories_per_100g == 52.0
    assert food.food_id is not None


def test_meal_entity():
    user_id = uuid4()
    food_id = uuid4()
    
    meal = Meal(
        user_id=user_id,
        food_id=food_id,
        quantity_grams=150.0
    )
    
    assert meal.user_id == user_id
    assert meal.food_id == food_id
    assert meal.quantity_grams == 150.0
    assert meal.meal_id is not None


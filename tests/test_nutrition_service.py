import pytest
from uuid import uuid4
from datetime import datetime
import importlib.util
from pathlib import Path


def load_module_from_path(module_name: str, file_path: Path):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


service_path = Path(__file__).parent.parent / "services" / "nutrition-service"
entities_module = load_module_from_path("nutrition_entities", service_path / "domain" / "entities.py")

Food = entities_module.Food
Meal = entities_module.Meal


class MockFoodRepository:
    def __init__(self):
        self.foods = {}

    async def create(self, food) -> object:
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

    async def update(self, food) -> object:
        self.foods[food.food_id] = food
        return food


class MockMealRepository:
    def __init__(self):
        self.meals = {}

    async def create(self, meal) -> object:
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

    async def update(self, meal) -> object:
        self.meals[meal.meal_id] = meal
        return meal

    async def delete(self, meal_id):
        if meal_id in self.meals:
            del self.meals[meal_id]
            return True
        return False


@pytest.mark.asyncio
async def test_create_food():
    repository = MockFoodRepository()
    food = Food(
        name="Apple",
        barcode="1234567890",
        calories_per_100g=52.0,
        proteins=0.3,
        carbs=14.0,
        fats=0.2
    )
    created = await repository.create(food)
    assert created.name == "Apple"
    assert created.barcode == "1234567890"
    assert created.calories_per_100g == 52.0
    assert created.proteins == 0.3
    assert created.carbs == 14.0
    assert created.fats == 0.2


@pytest.mark.asyncio
async def test_create_meal():
    food_repo = MockFoodRepository()
    meal_repo = MockMealRepository()
    user_id = uuid4()
    food = Food(name="Apple", calories_per_100g=52.0)
    await food_repo.create(food)
    meal = Meal(user_id=user_id, food_id=food.food_id, quantity_grams=150.0)
    created = await meal_repo.create(meal)
    assert created.user_id == user_id
    assert created.food_id == food.food_id
    assert created.quantity_grams == 150.0


@pytest.mark.asyncio
async def test_get_food_by_barcode():
    repository = MockFoodRepository()
    food = Food(name="Apple", barcode="1234567890", calories_per_100g=52.0)
    await repository.create(food)
    found = await repository.get_by_barcode("1234567890")
    assert found is not None
    assert found.name == "Apple"
    not_found = await repository.get_by_barcode("9999999999")
    assert not_found is None


@pytest.mark.asyncio
async def test_search_food_by_name():
    repository = MockFoodRepository()
    await repository.create(Food(name="Apple", calories_per_100g=52.0))
    await repository.create(Food(name="Apple Juice", calories_per_100g=46.0))
    await repository.create(Food(name="Banana", calories_per_100g=89.0))
    results = await repository.search_by_name("apple")
    assert len(results) == 2


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

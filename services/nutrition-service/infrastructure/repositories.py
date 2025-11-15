from typing import Optional, List
from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from domain.entities import Food, Meal
from domain.repositories import FoodRepository, MealRepository
from infrastructure.models import FoodModel, MealModel


class SQLAlchemyFoodRepository(FoodRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    def _to_entity(self, model: FoodModel) -> Food:
        return Food(
            food_id=model.food_id,
            name=model.name,
            barcode=model.barcode,
            calories_per_100g=model.calories_per_100g,
            proteins=model.proteins,
            carbs=model.carbs,
            fats=model.fats,
            created_at=model.created_at
        )

    def _to_model(self, entity: Food) -> FoodModel:
        return FoodModel(
            food_id=entity.food_id,
            name=entity.name,
            barcode=entity.barcode,
            calories_per_100g=entity.calories_per_100g,
            proteins=entity.proteins,
            carbs=entity.carbs,
            fats=entity.fats,
            created_at=entity.created_at
        )

    async def create(self, food: Food) -> Food:
        model = self._to_model(food)
        self.session.add(model)
        await self.session.commit()
        await self.session.refresh(model)
        return self._to_entity(model)

    async def get_by_id(self, food_id: UUID) -> Optional[Food]:
        result = await self.session.execute(
            select(FoodModel).where(FoodModel.food_id == food_id)
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def get_by_barcode(self, barcode: str) -> Optional[Food]:
        result = await self.session.execute(
            select(FoodModel).where(FoodModel.barcode == barcode)
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def search_by_name(self, name: str, limit: int = 20) -> List[Food]:
        result = await self.session.execute(
            select(FoodModel)
            .where(FoodModel.name.ilike(f"%{name}%"))
            .limit(limit)
        )
        models = result.scalars().all()
        return [self._to_entity(model) for model in models]

    async def update(self, food: Food) -> Food:
        result = await self.session.execute(
            select(FoodModel).where(FoodModel.food_id == food.food_id)
        )
        model = result.scalar_one()
        model.calories_per_100g = food.calories_per_100g
        model.proteins = food.proteins
        model.carbs = food.carbs
        model.fats = food.fats
        await self.session.commit()
        await self.session.refresh(model)
        return self._to_entity(model)


class SQLAlchemyMealRepository(MealRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    def _to_entity(self, model: MealModel) -> Meal:
        return Meal(
            meal_id=model.meal_id,
            user_id=model.user_id,
            food_id=model.food_id,
            quantity_grams=model.quantity_grams,
            consumed_at=model.consumed_at,
            created_at=model.created_at
        )

    def _to_model(self, entity: Meal) -> MealModel:
        return MealModel(
            meal_id=entity.meal_id,
            user_id=entity.user_id,
            food_id=entity.food_id,
            quantity_grams=entity.quantity_grams,
            consumed_at=entity.consumed_at,
            created_at=entity.created_at
        )

    async def create(self, meal: Meal) -> Meal:
        model = self._to_model(meal)
        self.session.add(model)
        await self.session.commit()
        await self.session.refresh(model)
        return self._to_entity(model)

    async def get_by_id(self, meal_id: UUID) -> Optional[Meal]:
        result = await self.session.execute(
            select(MealModel).where(MealModel.meal_id == meal_id)
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def get_by_user_id(self, user_id: UUID, limit: int = 100) -> List[Meal]:
        result = await self.session.execute(
            select(MealModel)
            .where(MealModel.user_id == user_id)
            .order_by(MealModel.consumed_at.desc())
            .limit(limit)
        )
        models = result.scalars().all()
        return [self._to_entity(model) for model in models]

    async def update(self, meal: Meal) -> Meal:
        result = await self.session.execute(
            select(MealModel).where(MealModel.meal_id == meal.meal_id)
        )
        model = result.scalar_one()
        model.quantity_grams = meal.quantity_grams
        await self.session.commit()
        await self.session.refresh(model)
        return self._to_entity(model)

    async def delete(self, meal_id: UUID) -> bool:
        result = await self.session.execute(
            select(MealModel).where(MealModel.meal_id == meal_id)
        )
        model = result.scalar_one_or_none()
        if not model:
            return False
        await self.session.delete(model)
        await self.session.commit()
        return True




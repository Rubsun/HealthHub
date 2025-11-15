from abc import ABC, abstractmethod
from typing import Optional, List
from uuid import UUID

from domain.entities import Food, Meal


class FoodRepository(ABC):
    @abstractmethod
    async def create(self, food: Food) -> Food:
        pass

    @abstractmethod
    async def get_by_id(self, food_id: UUID) -> Optional[Food]:
        pass

    @abstractmethod
    async def get_by_barcode(self, barcode: str) -> Optional[Food]:
        pass

    @abstractmethod
    async def search_by_name(self, name: str, limit: int = 20) -> List[Food]:
        pass

    @abstractmethod
    async def update(self, food: Food) -> Food:
        pass


class MealRepository(ABC):
    @abstractmethod
    async def create(self, meal: Meal) -> Meal:
        pass

    @abstractmethod
    async def get_by_id(self, meal_id: UUID) -> Optional[Meal]:
        pass

    @abstractmethod
    async def get_by_user_id(self, user_id: UUID, limit: int = 100) -> List[Meal]:
        pass

    @abstractmethod
    async def update(self, meal: Meal) -> Meal:
        pass

    @abstractmethod
    async def delete(self, meal_id: UUID) -> bool:
        pass




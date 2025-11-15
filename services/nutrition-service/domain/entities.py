from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4


class Food:
    def __init__(
        self,
        name: str,
        barcode: Optional[str] = None,
        calories_per_100g: Optional[float] = None,
        proteins: Optional[float] = None,
        carbs: Optional[float] = None,
        fats: Optional[float] = None,
        food_id: Optional[UUID] = None,
        created_at: Optional[datetime] = None
    ):
        self.food_id = food_id or uuid4()
        self.name = name
        self.barcode = barcode
        self.calories_per_100g = calories_per_100g
        self.proteins = proteins
        self.carbs = carbs
        self.fats = fats
        self.created_at = created_at or datetime.utcnow()

    def update(
        self,
        calories_per_100g: Optional[float] = None,
        proteins: Optional[float] = None,
        carbs: Optional[float] = None,
        fats: Optional[float] = None
    ):
        if calories_per_100g is not None:
            self.calories_per_100g = calories_per_100g
        if proteins is not None:
            self.proteins = proteins
        if carbs is not None:
            self.carbs = carbs
        if fats is not None:
            self.fats = fats


class Meal:
    def __init__(
        self,
        user_id: UUID,
        food_id: UUID,
        quantity_grams: float,
        meal_id: Optional[UUID] = None,
        consumed_at: Optional[datetime] = None,
        created_at: Optional[datetime] = None
    ):
        self.meal_id = meal_id or uuid4()
        self.user_id = user_id
        self.food_id = food_id
        self.quantity_grams = quantity_grams
        self.consumed_at = consumed_at or datetime.utcnow()
        self.created_at = created_at or datetime.utcnow()

    def update(self, quantity_grams: Optional[float] = None):
        if quantity_grams is not None:
            self.quantity_grams = quantity_grams




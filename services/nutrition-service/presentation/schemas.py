from datetime import datetime
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel


class FoodCreate(BaseModel):
    name: str
    barcode: Optional[str] = None
    calories_per_100g: Optional[float] = None
    proteins: Optional[float] = None
    carbs: Optional[float] = None
    fats: Optional[float] = None


class FoodResponse(BaseModel):
    food_id: UUID
    name: str
    barcode: Optional[str]
    calories_per_100g: Optional[float]
    proteins: Optional[float]
    carbs: Optional[float]
    fats: Optional[float]
    created_at: datetime

    class Config:
        from_attributes = True


class MealCreate(BaseModel):
    food_id: UUID
    quantity_grams: float


class MealResponse(BaseModel):
    meal_id: UUID
    user_id: UUID
    food_id: UUID
    quantity_grams: float
    consumed_at: datetime
    created_at: datetime

    class Config:
        from_attributes = True




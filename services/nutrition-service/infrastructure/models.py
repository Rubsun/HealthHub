from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import Column, String, Float, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PGUUID

from infrastructure.database import Base


class FoodModel(Base):
    __tablename__ = "foods"

    food_id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String, nullable=False, index=True)
    barcode = Column(String, nullable=True, unique=True, index=True)
    calories_per_100g = Column(Float, nullable=True)
    proteins = Column(Float, nullable=True)
    carbs = Column(Float, nullable=True)
    fats = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class MealModel(Base):
    __tablename__ = "meals"

    meal_id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(PGUUID(as_uuid=True), nullable=False, index=True)
    food_id = Column(PGUUID(as_uuid=True), ForeignKey("foods.food_id"), nullable=False)
    quantity_grams = Column(Float, nullable=False)
    consumed_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)




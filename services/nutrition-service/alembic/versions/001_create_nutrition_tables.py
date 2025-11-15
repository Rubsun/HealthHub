"""create_nutrition_tables

Revision ID: 001
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'foods',
        sa.Column('food_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('barcode', sa.String(), nullable=True),
        sa.Column('calories_per_100g', sa.Float(), nullable=True),
        sa.Column('proteins', sa.Float(), nullable=True),
        sa.Column('carbs', sa.Float(), nullable=True),
        sa.Column('fats', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('food_id')
    )
    op.create_index('ix_foods_name', 'foods', ['name'], unique=False)
    op.create_index('ix_foods_barcode', 'foods', ['barcode'], unique=True)

    op.create_table(
        'meals',
        sa.Column('meal_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('food_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('quantity_grams', sa.Float(), nullable=False),
        sa.Column('consumed_at', sa.DateTime(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['food_id'], ['foods.food_id'], ),
        sa.PrimaryKeyConstraint('meal_id')
    )
    op.create_index('ix_meals_user_id', 'meals', ['user_id'], unique=False)


def downgrade() -> None:
    op.drop_index('ix_meals_user_id', table_name='meals')
    op.drop_table('meals')
    op.drop_index('ix_foods_barcode', table_name='foods')
    op.drop_index('ix_foods_name', table_name='foods')
    op.drop_table('foods')


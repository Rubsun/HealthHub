"""create_weather_logs_table

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
        'weather_logs',
        sa.Column('log_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('city', sa.String(), nullable=False),
        sa.Column('temperature', sa.Float(), nullable=False),
        sa.Column('description', sa.String(), nullable=False),
        sa.Column('humidity', sa.Integer(), nullable=True),
        sa.Column('wind_speed', sa.Float(), nullable=True),
        sa.Column('recorded_at', sa.DateTime(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('log_id')
    )
    op.create_index(op.f('ix_weather_logs_city'), 'weather_logs', ['city'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_weather_logs_city'), table_name='weather_logs')
    op.drop_table('weather_logs')




"""change_activity_type_to_string

Revision ID: 002
Revises: 001
Create Date: 2025-01-02 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '002'
down_revision: Union[str, None] = '001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("ALTER TABLE activities ALTER COLUMN activity_type TYPE VARCHAR(20) USING activity_type::text")
    op.execute("DROP TYPE IF EXISTS activitytype")


def downgrade() -> None:
    op.execute("CREATE TYPE activitytype AS ENUM ('walking', 'running', 'cycling', 'swimming', 'gym', 'other')")
    op.execute("ALTER TABLE activities ALTER COLUMN activity_type TYPE activitytype USING activity_type::activitytype")


"""Add user notification_preferences field.

Revision ID: 006
Revises: 005
Create Date: 2026-02-11

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "006"
down_revision: Union[str, None] = "005"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add notification_preferences JSON field to user table
    op.add_column(
        "user",
        sa.Column("notification_preferences", postgresql.JSON(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("user", "notification_preferences")

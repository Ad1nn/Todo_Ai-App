"""Add display_name field to user table.

Revision ID: 004
Revises: 003
Create Date: 2026-02-06

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "004"
down_revision: Union[str, None] = "003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add display_name column to user table
    op.add_column("user", sa.Column("display_name", sa.String(100), nullable=True))


def downgrade() -> None:
    # Remove display_name column
    op.drop_column("user", "display_name")

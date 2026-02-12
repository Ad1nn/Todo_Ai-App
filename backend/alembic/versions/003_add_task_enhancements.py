"""Add task enhancements: due_date, priority, category.

Revision ID: 003
Revises: 002
Create Date: 2026-02-05

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "003"
down_revision: Union[str, None] = "002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add new columns to task table
    op.add_column("task", sa.Column("due_date", sa.DateTime(), nullable=True))
    op.add_column("task", sa.Column("priority", sa.String(10), nullable=True))
    op.add_column("task", sa.Column("category", sa.String(50), nullable=True))

    # Add indexes for query performance
    op.create_index("ix_task_due_date", "task", ["due_date"], unique=False)
    op.create_index("ix_task_priority", "task", ["priority"], unique=False)
    op.create_index("ix_task_category", "task", ["category"], unique=False)


def downgrade() -> None:
    # Remove indexes
    op.drop_index("ix_task_category", table_name="task")
    op.drop_index("ix_task_priority", table_name="task")
    op.drop_index("ix_task_due_date", table_name="task")

    # Remove columns
    op.drop_column("task", "category")
    op.drop_column("task", "priority")
    op.drop_column("task", "due_date")

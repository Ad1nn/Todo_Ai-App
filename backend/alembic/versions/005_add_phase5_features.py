"""Add Phase 5 features: recurrence, notifications, audit trail.

Revision ID: 005
Revises: 004
Create Date: 2026-02-11

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "005"
down_revision: Union[str, None] = "004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # === Task table: Add recurrence fields ===
    op.add_column(
        "task",
        sa.Column("recurrence_rule", sa.String(20), nullable=True, server_default="none"),
    )
    op.add_column(
        "task", sa.Column("last_reminder_sent", sa.DateTime(), nullable=True)
    )
    op.add_column(
        "task",
        sa.Column("parent_task_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.create_foreign_key(
        "fk_task_parent_task_id", "task", "task", ["parent_task_id"], ["id"]
    )
    op.create_index("ix_task_recurrence_rule", "task", ["recurrence_rule"], unique=False)

    # === Notification table ===
    op.create_table(
        "notification",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("type", sa.String(20), nullable=False),
        sa.Column("title", sa.String(100), nullable=False),
        sa.Column("message", sa.String(500), nullable=True),
        sa.Column("task_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("read", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("read_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"]),
        sa.ForeignKeyConstraint(["task_id"], ["task.id"]),
    )
    op.create_index("ix_notification_user_id", "notification", ["user_id"], unique=False)
    op.create_index("ix_notification_read", "notification", ["read"], unique=False)
    op.create_index("ix_notification_created_at", "notification", ["created_at"], unique=False)

    # === AuditEntry table ===
    op.create_table(
        "audit_entry",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("entity_type", sa.String(50), nullable=False),
        sa.Column("entity_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("action", sa.String(20), nullable=False),
        sa.Column("before_value", postgresql.JSON(), nullable=True),
        sa.Column("after_value", postgresql.JSON(), nullable=True),
        sa.Column("timestamp", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("extra_data", postgresql.JSON(), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"]),
    )
    op.create_index("ix_audit_entry_user_id", "audit_entry", ["user_id"], unique=False)
    op.create_index("ix_audit_entry_timestamp", "audit_entry", ["timestamp"], unique=False)
    op.create_index("ix_audit_entry_entity", "audit_entry", ["entity_type", "entity_id"], unique=False)


def downgrade() -> None:
    # Drop audit_entry table
    op.drop_index("ix_audit_entry_entity", table_name="audit_entry")
    op.drop_index("ix_audit_entry_timestamp", table_name="audit_entry")
    op.drop_index("ix_audit_entry_user_id", table_name="audit_entry")
    op.drop_table("audit_entry")

    # Drop notification table
    op.drop_index("ix_notification_created_at", table_name="notification")
    op.drop_index("ix_notification_read", table_name="notification")
    op.drop_index("ix_notification_user_id", table_name="notification")
    op.drop_table("notification")

    # Remove task recurrence fields
    op.drop_index("ix_task_recurrence_rule", table_name="task")
    op.drop_constraint("fk_task_parent_task_id", "task", type_="foreignkey")
    op.drop_column("task", "parent_task_id")
    op.drop_column("task", "last_reminder_sent")
    op.drop_column("task", "recurrence_rule")

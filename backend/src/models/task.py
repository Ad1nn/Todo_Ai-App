"""Task model definitions."""

from datetime import datetime
from enum import Enum
from uuid import UUID, uuid4

from sqlalchemy import String
from sqlmodel import Field, SQLModel


class Priority(str, Enum):
    """Task priority levels in order of urgency."""

    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class RecurrenceRule(str, Enum):
    """Task recurrence patterns."""

    NONE = "none"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


class TaskBase(SQLModel):
    """Base task fields shared across schemas."""

    title: str = Field(max_length=200)
    description: str | None = Field(default=None, max_length=2000)
    due_date: datetime | None = Field(default=None)
    priority: Priority | None = Field(default=None, sa_type=String(10))
    category: str | None = Field(default=None, max_length=50)
    recurrence_rule: RecurrenceRule = Field(
        default=RecurrenceRule.NONE, sa_type=String(20)
    )


class Task(TaskBase, table=True):
    """Task database model."""

    __tablename__ = "task"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="user.id", index=True)
    completed: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    # Phase 5: Recurrence tracking
    last_reminder_sent: datetime | None = Field(default=None)
    parent_task_id: UUID | None = Field(default=None, foreign_key="task.id")


class TaskCreate(SQLModel):
    """Schema for creating a new task."""

    title: str = Field(min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=2000)
    due_date: datetime | None = Field(default=None)
    priority: Priority | None = Field(default=None)
    category: str | None = Field(default=None, max_length=50)
    recurrence_rule: RecurrenceRule = Field(default=RecurrenceRule.NONE)


class TaskUpdate(SQLModel):
    """Schema for updating a task."""

    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=2000)
    due_date: datetime | None = Field(default=None)
    priority: Priority | None = Field(default=None)
    category: str | None = Field(default=None, max_length=50)
    recurrence_rule: RecurrenceRule | None = Field(default=None)


class TaskPublic(TaskBase):
    """Public task data."""

    id: UUID
    completed: bool
    created_at: datetime
    updated_at: datetime
    parent_task_id: UUID | None = None
    # Inherited from TaskBase: due_date, priority, category, recurrence_rule

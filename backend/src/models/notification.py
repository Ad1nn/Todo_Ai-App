"""Notification model definitions for in-app notifications."""

from datetime import datetime
from enum import Enum
from uuid import UUID, uuid4

from sqlalchemy import String
from sqlmodel import Field, SQLModel


class NotificationType(str, Enum):
    """Types of notifications."""

    REMINDER = "reminder"  # Task due soon
    SYSTEM = "system"  # General system info
    ACTION = "action"  # Task completed, etc.


class NotificationBase(SQLModel):
    """Base notification fields shared across schemas."""

    type: NotificationType = Field(sa_type=String(20))
    title: str = Field(max_length=100)
    message: str | None = Field(default=None, max_length=500)
    task_id: UUID | None = Field(default=None, foreign_key="task.id")


class Notification(NotificationBase, table=True):
    """Notification database model."""

    __tablename__ = "notification"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="user.id", index=True)
    read: bool = Field(default=False, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    read_at: datetime | None = Field(default=None)


class NotificationCreate(SQLModel):
    """Schema for creating a new notification."""

    type: NotificationType
    title: str = Field(min_length=1, max_length=100)
    message: str | None = Field(default=None, max_length=500)
    task_id: UUID | None = Field(default=None)
    user_id: UUID


class NotificationPublic(NotificationBase):
    """Public notification data."""

    id: UUID
    user_id: UUID
    read: bool
    created_at: datetime
    read_at: datetime | None = None

"""User model definitions."""

from datetime import datetime
from typing import TYPE_CHECKING, Any
from uuid import UUID, uuid4

from pydantic import EmailStr
from sqlalchemy import JSON
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from src.models.conversation import Conversation
    from src.models.message import Message


# Default notification preferences
DEFAULT_NOTIFICATION_PREFERENCES = {
    "reminders_enabled": True,
    "reminder_minutes_before": 15,
    "email_notifications": False,
    "toast_notifications": True,
}


class UserBase(SQLModel):
    """Base user fields shared across schemas."""

    email: EmailStr = Field(max_length=255, index=True, unique=True)
    display_name: str | None = Field(default=None, max_length=100)


class User(UserBase, table=True):
    """User database model."""

    __tablename__ = "user"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    password_hash: str = Field(max_length=255)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    # Phase 5: Notification preferences (JSON field)
    notification_preferences: dict[str, Any] | None = Field(
        default=None, sa_type=JSON
    )

    # Relationships (Phase 3)
    conversations: list["Conversation"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )
    messages: list["Message"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )

    def get_notification_preferences(self) -> dict[str, Any]:
        """Get notification preferences with defaults."""
        if self.notification_preferences is None:
            return DEFAULT_NOTIFICATION_PREFERENCES.copy()
        return {**DEFAULT_NOTIFICATION_PREFERENCES, **self.notification_preferences}


class UserCreate(SQLModel):
    """Schema for creating a new user."""

    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8)


class UserLogin(SQLModel):
    """Schema for user login."""

    email: EmailStr
    password: str


class UserPublic(SQLModel):
    """Public user data (excludes password)."""

    id: UUID
    email: EmailStr
    display_name: str | None
    created_at: datetime


class UserUpdate(SQLModel):
    """Schema for updating user profile."""

    display_name: str | None = Field(default=None, max_length=100)


class UserStats(SQLModel):
    """User task statistics."""

    total_tasks: int
    completed_tasks: int
    pending_tasks: int
    overdue_tasks: int


class NotificationPreferences(SQLModel):
    """Notification preferences schema."""

    reminders_enabled: bool = True
    reminder_minutes_before: int = Field(default=15, ge=5, le=1440)
    email_notifications: bool = False
    toast_notifications: bool = True


class UserPreferencesUpdate(SQLModel):
    """Schema for updating user notification preferences."""

    reminders_enabled: bool | None = None
    reminder_minutes_before: int | None = Field(default=None, ge=5, le=1440)
    email_notifications: bool | None = None
    toast_notifications: bool | None = None

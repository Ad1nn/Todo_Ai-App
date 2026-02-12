"""User preferences service for managing notification settings."""

from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.user import (
    DEFAULT_NOTIFICATION_PREFERENCES,
    NotificationPreferences,
    User,
    UserPreferencesUpdate,
)


class UserPreferencesService:
    """Service for user notification preferences."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_preferences(self, user_id: UUID) -> NotificationPreferences:
        """Get user notification preferences with defaults."""
        result = await self.session.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        if not user:
            return NotificationPreferences(**DEFAULT_NOTIFICATION_PREFERENCES)

        prefs = user.get_notification_preferences()
        return NotificationPreferences(**prefs)

    async def update_preferences(
        self,
        user_id: UUID,
        updates: UserPreferencesUpdate,
    ) -> NotificationPreferences:
        """Update user notification preferences."""
        result = await self.session.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        if not user:
            raise ValueError(f"User {user_id} not found")

        # Get current preferences with defaults
        current = user.get_notification_preferences()

        # Apply updates (only non-None values)
        update_data = updates.model_dump(exclude_none=True)
        for key, value in update_data.items():
            current[key] = value

        # Save to database
        user.notification_preferences = current
        await self.session.flush()
        await self.session.refresh(user)

        return NotificationPreferences(**current)

    async def are_reminders_enabled(self, user_id: UUID) -> bool:
        """Check if reminders are enabled for a user."""
        prefs = await self.get_preferences(user_id)
        return prefs.reminders_enabled

    async def get_reminder_minutes(self, user_id: UUID) -> int:
        """Get how many minutes before due date to send reminder."""
        prefs = await self.get_preferences(user_id)
        return prefs.reminder_minutes_before

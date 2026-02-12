"""Notification service for business logic."""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.models.notification import Notification, NotificationPublic, NotificationType
from src.repositories.notification_repository import NotificationRepository


class NotificationService:
    """Service for notification operations."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.notification_repo = NotificationRepository(session)

    async def create(
        self,
        user_id: UUID,
        notification_type: NotificationType,
        title: str,
        message: str | None = None,
        task_id: UUID | None = None,
    ) -> Notification:
        """Create a new notification."""
        return await self.notification_repo.create(
            user_id=user_id,
            notification_type=notification_type,
            title=title,
            message=message,
            task_id=task_id,
        )

    async def get_by_id(
        self, notification_id: UUID, user_id: UUID
    ) -> Notification | None:
        """Get notification by ID with ownership check."""
        return await self.notification_repo.get_by_id_and_user(notification_id, user_id)

    async def list_by_user(
        self,
        user_id: UUID,
        unread_only: bool = False,
        limit: int = 50,
    ) -> list[Notification]:
        """List notifications for a user."""
        return await self.notification_repo.list_by_user(
            user_id=user_id,
            unread_only=unread_only,
            limit=limit,
        )

    async def get_unread_count(self, user_id: UUID) -> int:
        """Get count of unread notifications for a user."""
        return await self.notification_repo.get_unread_count(user_id)

    async def mark_as_read(
        self, notification_id: UUID, user_id: UUID
    ) -> Notification | None:
        """Mark a notification as read."""
        notification = await self.notification_repo.get_by_id_and_user(
            notification_id, user_id
        )
        if not notification:
            return None

        return await self.notification_repo.mark_as_read(notification)

    async def mark_all_as_read(self, user_id: UUID) -> int:
        """Mark all notifications as read for a user."""
        return await self.notification_repo.mark_all_as_read(user_id)

    async def delete(self, notification_id: UUID, user_id: UUID) -> bool:
        """Delete a notification. Returns True if deleted, False if not found."""
        notification = await self.notification_repo.get_by_id_and_user(
            notification_id, user_id
        )
        if not notification:
            return False

        await self.notification_repo.delete(notification)
        return True

    async def clear_old_notifications(
        self,
        user_id: UUID,
        days_old: int = 30,
    ) -> int:
        """Clear notifications older than specified days."""
        return await self.notification_repo.delete_old_notifications(
            user_id=user_id,
            days_old=days_old,
        )

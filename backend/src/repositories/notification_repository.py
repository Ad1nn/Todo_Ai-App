"""Notification repository for database operations."""

from datetime import datetime, timedelta
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.notification import Notification, NotificationType


class NotificationRepository:
    """Repository for Notification database operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self,
        user_id: UUID,
        notification_type: NotificationType,
        title: str,
        message: str | None = None,
        task_id: UUID | None = None,
    ) -> Notification:
        """Create a new notification."""
        notification = Notification(
            user_id=user_id,
            type=notification_type,
            title=title,
            message=message,
            task_id=task_id,
            read=False,
            created_at=datetime.utcnow(),
        )
        self.session.add(notification)
        await self.session.flush()
        await self.session.refresh(notification)
        return notification

    async def get_by_id(self, notification_id: UUID) -> Notification | None:
        """Get notification by ID."""
        result = await self.session.execute(
            select(Notification).where(Notification.id == notification_id)
        )
        return result.scalar_one_or_none()

    async def get_by_id_and_user(
        self, notification_id: UUID, user_id: UUID
    ) -> Notification | None:
        """Get notification by ID and user ID (ownership check)."""
        result = await self.session.execute(
            select(Notification).where(
                Notification.id == notification_id,
                Notification.user_id == user_id,
            )
        )
        return result.scalar_one_or_none()

    async def list_by_user(
        self,
        user_id: UUID,
        unread_only: bool = False,
        limit: int = 50,
    ) -> list[Notification]:
        """List notifications for a user, most recent first."""
        query = select(Notification).where(Notification.user_id == user_id)

        if unread_only:
            query = query.where(Notification.read == False)  # noqa: E712

        query = query.order_by(Notification.created_at.desc()).limit(limit)

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_unread_count(self, user_id: UUID) -> int:
        """Get count of unread notifications for a user."""
        result = await self.session.execute(
            select(func.count(Notification.id)).where(
                Notification.user_id == user_id,
                Notification.read == False,  # noqa: E712
            )
        )
        return result.scalar() or 0

    async def mark_as_read(self, notification: Notification) -> Notification:
        """Mark a notification as read."""
        notification.read = True
        notification.read_at = datetime.utcnow()
        self.session.add(notification)
        await self.session.flush()
        await self.session.refresh(notification)
        return notification

    async def mark_all_as_read(self, user_id: UUID) -> int:
        """Mark all notifications as read for a user. Returns count of updated."""
        # Get all unread notifications for user
        result = await self.session.execute(
            select(Notification).where(
                Notification.user_id == user_id,
                Notification.read == False,  # noqa: E712
            )
        )
        notifications = list(result.scalars().all())

        now = datetime.utcnow()
        for notification in notifications:
            notification.read = True
            notification.read_at = now
            self.session.add(notification)

        await self.session.flush()
        return len(notifications)

    async def delete(self, notification: Notification) -> None:
        """Delete a notification."""
        await self.session.delete(notification)
        await self.session.flush()

    async def delete_old_notifications(
        self,
        user_id: UUID,
        days_old: int = 30,
    ) -> int:
        """Delete notifications older than specified days. Returns count deleted."""
        cutoff = datetime.utcnow() - timedelta(days=days_old)
        result = await self.session.execute(
            select(Notification).where(
                Notification.user_id == user_id,
                Notification.created_at < cutoff,
            )
        )
        notifications = list(result.scalars().all())

        for notification in notifications:
            await self.session.delete(notification)

        await self.session.flush()
        return len(notifications)

"""Reminder service for checking due tasks and publishing reminder events."""

import logging
from datetime import datetime, timedelta
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.events import publish_reminder_event
from src.models.task import Task
from src.models.user import User

logger = logging.getLogger(__name__)


class ReminderService:
    """Service for reminder operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def check_due_tasks(
        self,
        reminder_window_minutes: int = 60,
        min_interval_minutes: int = 15,
    ) -> list[UUID]:
        """Check for tasks due soon and publish reminder events.

        Args:
            reminder_window_minutes: How far ahead to look for due tasks
            min_interval_minutes: Minimum time between reminders for same task

        Returns:
            List of task IDs that had reminders published
        """
        now = datetime.utcnow()
        window_end = now + timedelta(minutes=reminder_window_minutes)
        min_reminder_interval = now - timedelta(minutes=min_interval_minutes)

        # Find tasks due within the window that:
        # 1. Are not completed
        # 2. Have a due date
        # 3. Haven't had a reminder sent recently (or never had one)
        query = select(Task).where(
            Task.completed == False,  # noqa: E712
            Task.due_date.isnot(None),
            Task.due_date <= window_end,
            Task.due_date > now,  # Not already past due
        ).where(
            (Task.last_reminder_sent.is_(None))
            | (Task.last_reminder_sent < min_reminder_interval)
        )

        result = await self.session.execute(query)
        tasks = list(result.scalars().all())

        reminded_task_ids = []

        for task in tasks:
            try:
                # Check user preferences before sending reminder
                if not await self._user_has_reminders_enabled(task.user_id):
                    logger.debug(f"Skipping reminder for task {task.id}: user has reminders disabled")
                    continue

                # Publish reminder event
                success = await publish_reminder_event(
                    user_id=task.user_id,
                    task_id=task.id,
                    task_title=task.title,
                    due_date=task.due_date,
                )

                if success:
                    # Update last_reminder_sent
                    task.last_reminder_sent = now
                    self.session.add(task)
                    reminded_task_ids.append(task.id)
                    logger.info(f"Published reminder for task {task.id}: {task.title}")
                else:
                    logger.warning(f"Failed to publish reminder for task {task.id}")

            except Exception as e:
                logger.error(f"Error publishing reminder for task {task.id}: {e}")

        await self.session.flush()
        return reminded_task_ids

    async def _user_has_reminders_enabled(self, user_id: UUID) -> bool:
        """Check if user has reminders enabled in preferences."""
        result = await self.session.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        if not user:
            return True  # Default to enabled if user not found

        prefs = user.get_notification_preferences()
        return prefs.get("reminders_enabled", True)

    async def get_upcoming_reminders(
        self,
        user_id: UUID,
        hours_ahead: int = 24,
    ) -> list[Task]:
        """Get tasks for a user that are due within the specified hours.

        Args:
            user_id: User ID to check tasks for
            hours_ahead: How many hours ahead to look

        Returns:
            List of tasks due soon
        """
        now = datetime.utcnow()
        window_end = now + timedelta(hours=hours_ahead)

        result = await self.session.execute(
            select(Task).where(
                Task.user_id == user_id,
                Task.completed == False,  # noqa: E712
                Task.due_date.isnot(None),
                Task.due_date <= window_end,
                Task.due_date > now,
            ).order_by(Task.due_date.asc())
        )

        return list(result.scalars().all())


async def handle_cron_trigger(session: AsyncSession) -> dict:
    """Handle the cron trigger from Dapr binding.

    This is called every 15 minutes by the Dapr cron binding.

    Args:
        session: Database session

    Returns:
        Summary of reminder processing
    """
    logger.info("Cron trigger: Starting reminder check")

    reminder_service = ReminderService(session)
    reminded_task_ids = await reminder_service.check_due_tasks(
        reminder_window_minutes=60,  # 1 hour ahead
        min_interval_minutes=15,  # Don't re-remind within 15 min
    )

    await session.commit()

    result = {
        "status": "success",
        "checked_at": datetime.utcnow().isoformat(),
        "reminders_sent": len(reminded_task_ids),
        "task_ids": [str(tid) for tid in reminded_task_ids],
    }

    logger.info(f"Cron trigger: Sent {len(reminded_task_ids)} reminders")
    return result

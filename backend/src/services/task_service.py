"""Task service for business logic."""

from datetime import datetime
from typing import Literal
from uuid import UUID

from dateutil.relativedelta import relativedelta
from sqlalchemy.ext.asyncio import AsyncSession

from src.events import publish_audit_event
from src.models.task import Priority, RecurrenceRule, Task
from src.repositories.task_repository import TaskRepository


def _task_to_dict(task: Task) -> dict:
    """Convert task to dictionary for audit logging."""
    return {
        "id": str(task.id),
        "title": task.title,
        "description": task.description,
        "completed": task.completed,
        "due_date": task.due_date.isoformat() if task.due_date else None,
        "priority": task.priority.value if task.priority else None,
        "category": task.category,
        "recurrence_rule": task.recurrence_rule.value if task.recurrence_rule else None,
    }


def calculate_next_due_date(
    current_due: datetime,
    recurrence_rule: RecurrenceRule,
) -> datetime:
    """Calculate the next due date based on recurrence pattern.

    Args:
        current_due: Current due date
        recurrence_rule: The recurrence pattern

    Returns:
        Next due date based on the pattern
    """
    match recurrence_rule:
        case RecurrenceRule.DAILY:
            return current_due + relativedelta(days=1)
        case RecurrenceRule.WEEKLY:
            return current_due + relativedelta(weeks=1)
        case RecurrenceRule.MONTHLY:
            # relativedelta handles month-end edge cases
            return current_due + relativedelta(months=1)
        case RecurrenceRule.NONE:
            raise ValueError("Cannot calculate next due date for non-recurring task")
        case _:
            raise ValueError(f"Unknown recurrence rule: {recurrence_rule}")


class TaskService:
    """Service for task operations."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.task_repo = TaskRepository(session)

    async def create(
        self,
        user_id: UUID,
        title: str,
        description: str | None = None,
        due_date: datetime | None = None,
        priority: Priority | None = None,
        category: str | None = None,
        recurrence_rule: RecurrenceRule = RecurrenceRule.NONE,
        parent_task_id: UUID | None = None,
        skip_audit: bool = False,
    ) -> Task:
        """Create a new task."""
        task = await self.task_repo.create(
            user_id=user_id,
            title=title,
            description=description,
            due_date=due_date,
            priority=priority,
            category=category,
            recurrence_rule=recurrence_rule,
            parent_task_id=parent_task_id,
        )

        # Publish audit event (fire and forget)
        if not skip_audit:
            await publish_audit_event(
                user_id=user_id,
                entity_type="task",
                entity_id=task.id,
                action="create",
                after_value=_task_to_dict(task),
            )

        return task

    async def get_by_id(self, task_id: UUID, user_id: UUID) -> Task | None:
        """Get task by ID with ownership check."""
        return await self.task_repo.get_by_id_and_user(task_id, user_id)

    async def list_by_user(self, user_id: UUID) -> list[Task]:
        """List all tasks for a user."""
        return await self.task_repo.list_by_user(user_id)

    async def list_by_user_filtered(
        self,
        user_id: UUID,
        category: str | None = None,
        priority: Priority | None = None,
        completed: bool | None = None,
        overdue_only: bool = False,
        sort_by: Literal["created_at", "due_date", "priority"] = "created_at",
        sort_order: Literal["asc", "desc"] = "desc",
    ) -> list[Task]:
        """List tasks for a user with optional filters and sorting."""
        return await self.task_repo.list_by_user_filtered(
            user_id=user_id,
            category=category,
            priority=priority,
            completed=completed,
            overdue_only=overdue_only,
            sort_by=sort_by,
            sort_order=sort_order,
        )

    async def get_user_categories(self, user_id: UUID) -> list[str]:
        """Get distinct categories for a user's tasks."""
        return await self.task_repo.get_user_categories(user_id)

    async def update(
        self,
        task_id: UUID,
        user_id: UUID,
        title: str | None = None,
        description: str | None = None,
        due_date: datetime | None = None,
        priority: Priority | None = None,
        category: str | None = None,
        recurrence_rule: RecurrenceRule | None = None,
        clear_due_date: bool = False,
        clear_priority: bool = False,
        clear_category: bool = False,
        clear_recurrence: bool = False,
    ) -> Task | None:
        """Update task fields."""
        task = await self.task_repo.get_by_id_and_user(task_id, user_id)
        if not task:
            return None

        # Capture before state for audit
        before_value = _task_to_dict(task)

        if title is not None:
            task.title = title
        if description is not None:
            task.description = description
        if due_date is not None:
            task.due_date = due_date
        elif clear_due_date:
            task.due_date = None
        if priority is not None:
            task.priority = priority
        elif clear_priority:
            task.priority = None
        if category is not None:
            task.category = category.strip() if category else None
        elif clear_category:
            task.category = None
        if recurrence_rule is not None:
            task.recurrence_rule = recurrence_rule
        elif clear_recurrence:
            task.recurrence_rule = RecurrenceRule.NONE

        task.updated_at = datetime.utcnow()
        updated_task = await self.task_repo.update(task)

        # Publish audit event
        await publish_audit_event(
            user_id=user_id,
            entity_type="task",
            entity_id=task_id,
            action="update",
            before_value=before_value,
            after_value=_task_to_dict(updated_task),
        )

        return updated_task

    async def toggle_complete(self, task_id: UUID, user_id: UUID) -> Task | None:
        """Toggle task completion status."""
        task = await self.task_repo.get_by_id_and_user(task_id, user_id)
        if not task:
            return None

        task.completed = not task.completed
        task.updated_at = datetime.utcnow()
        return await self.task_repo.update(task)

    async def complete_recurring_task(
        self,
        task_id: UUID,
        user_id: UUID,
    ) -> tuple[Task | None, Task | None]:
        """Complete a task and create next occurrence if recurring.

        Args:
            task_id: Task to complete
            user_id: Owner of the task

        Returns:
            Tuple of (completed_task, new_task_or_none)
            - completed_task: The task that was marked complete, or None if not found
            - new_task_or_none: The newly created recurring task, or None if not recurring
        """
        task = await self.task_repo.get_by_id_and_user(task_id, user_id)
        if not task:
            return None, None

        # Mark task as completed
        task.completed = True
        task.updated_at = datetime.utcnow()
        completed_task = await self.task_repo.update(task)

        # Check if task has recurrence
        if (
            task.recurrence_rule
            and task.recurrence_rule != RecurrenceRule.NONE
            and task.due_date
        ):
            # Calculate next due date
            next_due = calculate_next_due_date(task.due_date, task.recurrence_rule)

            # Create next occurrence (skip audit - will be audited separately if needed)
            new_task = await self.create(
                user_id=user_id,
                title=task.title,
                description=task.description,
                due_date=next_due,
                priority=task.priority,
                category=task.category,
                recurrence_rule=task.recurrence_rule,
                parent_task_id=task.parent_task_id or task.id,
                skip_audit=True,  # Don't audit auto-created recurrence tasks
            )
            return completed_task, new_task

        return completed_task, None

    async def delete(self, task_id: UUID, user_id: UUID) -> bool:
        """Delete a task. Returns True if deleted, False if not found."""
        task = await self.task_repo.get_by_id_and_user(task_id, user_id)
        if not task:
            return False

        # Capture before state for audit
        before_value = _task_to_dict(task)

        await self.task_repo.delete(task)

        # Publish audit event
        await publish_audit_event(
            user_id=user_id,
            entity_type="task",
            entity_id=task_id,
            action="delete",
            before_value=before_value,
        )

        return True

    async def get_user_stats(self, user_id: UUID) -> dict[str, int]:
        """Get task statistics for a user."""
        return await self.task_repo.get_user_stats(user_id)

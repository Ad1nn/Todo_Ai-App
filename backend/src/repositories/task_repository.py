"""Task repository for database operations."""

from datetime import datetime
from typing import Literal
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.task import Priority, RecurrenceRule, Task


class TaskRepository:
    """Repository for Task database operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

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
    ) -> Task:
        """Create a new task."""
        task = Task(
            user_id=user_id,
            title=title,
            description=description,
            due_date=due_date,
            priority=priority,
            category=category.strip() if category else None,
            recurrence_rule=recurrence_rule,
            parent_task_id=parent_task_id,
        )
        self.session.add(task)
        await self.session.flush()
        await self.session.refresh(task)
        return task

    async def get_by_id(self, task_id: UUID) -> Task | None:
        """Get task by ID."""
        result = await self.session.execute(select(Task).where(Task.id == task_id))
        return result.scalar_one_or_none()

    async def get_by_id_and_user(self, task_id: UUID, user_id: UUID) -> Task | None:
        """Get task by ID and user ID (ownership check)."""
        result = await self.session.execute(
            select(Task).where(Task.id == task_id, Task.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def list_by_user(self, user_id: UUID) -> list[Task]:
        """List all tasks for a user."""
        result = await self.session.execute(
            select(Task).where(Task.user_id == user_id).order_by(Task.created_at.desc())
        )
        return list(result.scalars().all())

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
        query = select(Task).where(Task.user_id == user_id)

        # Apply filters
        if category is not None:
            query = query.where(Task.category == category)
        if priority is not None:
            query = query.where(Task.priority == priority)
        if completed is not None:
            query = query.where(Task.completed == completed)
        if overdue_only:
            query = query.where(
                Task.due_date < datetime.utcnow(),
                Task.completed == False,  # noqa: E712
            )

        # Apply sorting
        if sort_by == "due_date":
            # NULL dates go last
            sort_col = Task.due_date.asc().nullslast() if sort_order == "asc" else Task.due_date.desc().nullslast()
        elif sort_by == "priority":
            # Priority order: urgent, high, normal, low, NULL
            # We need custom ordering for enum
            sort_col = Task.priority.desc().nullslast() if sort_order == "desc" else Task.priority.asc().nullslast()
        else:  # created_at
            sort_col = Task.created_at.asc() if sort_order == "asc" else Task.created_at.desc()

        query = query.order_by(sort_col)

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_user_categories(self, user_id: UUID) -> list[str]:
        """Get distinct categories for a user's tasks."""
        result = await self.session.execute(
            select(Task.category)
            .where(Task.user_id == user_id, Task.category.isnot(None))
            .distinct()
            .order_by(Task.category)
        )
        return [row[0] for row in result.all()]

    async def update(self, task: Task) -> Task:
        """Update a task."""
        self.session.add(task)
        await self.session.flush()
        await self.session.refresh(task)
        return task

    async def delete(self, task: Task) -> None:
        """Delete a task."""
        await self.session.delete(task)
        await self.session.flush()

    async def get_user_stats(self, user_id: UUID) -> dict[str, int]:
        """Get task statistics for a user."""
        # Total tasks
        total_result = await self.session.execute(
            select(func.count(Task.id)).where(Task.user_id == user_id)
        )
        total = total_result.scalar() or 0

        # Completed tasks
        completed_result = await self.session.execute(
            select(func.count(Task.id)).where(
                Task.user_id == user_id,
                Task.completed == True,  # noqa: E712
            )
        )
        completed = completed_result.scalar() or 0

        # Overdue tasks (past due date and not completed)
        overdue_result = await self.session.execute(
            select(func.count(Task.id)).where(
                Task.user_id == user_id,
                Task.completed == False,  # noqa: E712
                Task.due_date < datetime.utcnow(),
            )
        )
        overdue = overdue_result.scalar() or 0

        return {
            "total_tasks": total,
            "completed_tasks": completed,
            "pending_tasks": total - completed,
            "overdue_tasks": overdue,
        }

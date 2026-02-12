"""MCP tools for task management operations."""

from datetime import datetime
from typing import Any, Literal
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.models.task import Priority, RecurrenceRule, Task
from src.repositories.task_repository import TaskRepository
from src.services.task_service import TaskService


class MCPToolError(Exception):
    """Error raised by MCP tools with user-friendly messages."""

    def __init__(self, code: str, message: str):
        self.code = code
        self.message = message
        super().__init__(message)


class MCPTools:
    """MCP tools for task management exposed to AI agent."""

    def __init__(self, session: AsyncSession, user_id: UUID):
        """Initialize with database session and authenticated user ID."""
        self.session = session
        self.user_id = user_id
        self.task_repo = TaskRepository(session)

    def _task_to_dict(self, task: Task) -> dict[str, Any]:
        """Convert task to dictionary for response."""
        # Handle priority - could be enum or string depending on source
        priority_value = None
        if task.priority:
            priority_value = task.priority.value if hasattr(task.priority, 'value') else task.priority

        # Handle recurrence_rule - could be enum or string
        recurrence_value = "none"
        if task.recurrence_rule:
            recurrence_value = (
                task.recurrence_rule.value
                if hasattr(task.recurrence_rule, "value")
                else task.recurrence_rule
            )

        return {
            "id": str(task.id),
            "title": task.title,
            "description": task.description,
            "completed": task.completed,
            "due_date": task.due_date.isoformat() if task.due_date else None,
            "priority": priority_value,
            "category": task.category,
            "recurrence_rule": recurrence_value,
            "parent_task_id": str(task.parent_task_id) if task.parent_task_id else None,
            "created_at": task.created_at.isoformat(),
            "updated_at": task.updated_at.isoformat(),
        }

    async def add_task(
        self,
        title: str,
        description: str | None = None,
        due_date: str | None = None,
        priority: str | None = None,
        category: str | None = None,
        recurrence_rule: str | None = None,
    ) -> dict[str, Any]:
        """
        Create a new task for the user.

        Args:
            title: Task title (required, 1-200 characters)
            description: Optional task description
            due_date: Optional due date in ISO format (e.g., "2024-12-31T23:59:59")
            priority: Optional priority level ("low", "normal", "high", "urgent")
            category: Optional category (e.g., "work", "personal", "shopping")
            recurrence_rule: Optional recurrence pattern ("none", "daily", "weekly", "monthly")

        Returns:
            {task_id, status, data} with created task details
        """
        if not title or len(title.strip()) == 0:
            raise MCPToolError("invalid_title", "Task title cannot be empty")
        if len(title) > 200:
            raise MCPToolError("invalid_title", "Task title cannot exceed 200 characters")

        # Parse due date
        parsed_due_date = None
        if due_date:
            try:
                parsed_due_date = datetime.fromisoformat(due_date.replace("Z", "+00:00"))
            except ValueError as e:
                raise MCPToolError("invalid_due_date", f"Invalid due date format: {due_date}") from e

        # Parse priority
        parsed_priority = None
        if priority:
            try:
                parsed_priority = Priority(priority.lower())
            except ValueError as e:
                raise MCPToolError(
                    "invalid_priority",
                    f"Invalid priority '{priority}'. Must be one of: low, normal, high, urgent"
                ) from e

        # Validate category
        parsed_category = category.strip() if category else None
        if parsed_category and len(parsed_category) > 50:
            raise MCPToolError("invalid_category", "Category cannot exceed 50 characters")

        # Parse recurrence rule
        parsed_recurrence = RecurrenceRule.NONE
        if recurrence_rule:
            try:
                parsed_recurrence = RecurrenceRule(recurrence_rule.lower())
            except ValueError as e:
                raise MCPToolError(
                    "invalid_recurrence",
                    f"Invalid recurrence rule '{recurrence_rule}'. Must be one of: none, daily, weekly, monthly"
                ) from e

        task = await self.task_repo.create(
            user_id=self.user_id,
            title=title.strip(),
            description=description.strip() if description else None,
            due_date=parsed_due_date,
            priority=parsed_priority,
            category=parsed_category,
            recurrence_rule=parsed_recurrence,
        )

        return {
            "task_id": str(task.id),
            "status": "success",
            "data": self._task_to_dict(task),
        }

    async def list_tasks(
        self,
        completed: bool | None = None,
        priority: str | None = None,
        category: str | None = None,
        overdue: bool | None = None,
        sort_by: str | None = None,
    ) -> dict[str, Any]:
        """
        List all tasks for the user, optionally filtered.

        Args:
            completed: Filter by completion status (None = all tasks)
            priority: Filter by priority level ("low", "normal", "high", "urgent")
            category: Filter by category name
            overdue: If True, only show overdue tasks
            sort_by: Sort results by "created_at", "due_date", or "priority"

        Returns:
            {status, tasks} with array of tasks matching filters
        """
        # Parse priority
        parsed_priority = None
        if priority:
            try:
                parsed_priority = Priority(priority.lower())
            except ValueError as e:
                raise MCPToolError(
                    "invalid_priority",
                    f"Invalid priority '{priority}'. Must be one of: low, normal, high, urgent"
                ) from e

        # Validate sort_by
        valid_sort_by: Literal["created_at", "due_date", "priority"] = "created_at"
        if sort_by:
            if sort_by not in ("created_at", "due_date", "priority"):
                raise MCPToolError(
                    "invalid_sort",
                    f"Invalid sort_by '{sort_by}'. Must be one of: created_at, due_date, priority"
                )
            valid_sort_by = sort_by  # type: ignore

        tasks = await self.task_repo.list_by_user_filtered(
            user_id=self.user_id,
            category=category,
            priority=parsed_priority,
            completed=completed,
            overdue_only=overdue or False,
            sort_by=valid_sort_by,
        )

        return {
            "status": "success",
            "tasks": [self._task_to_dict(t) for t in tasks],
        }

    async def complete_task(self, task_id: str) -> dict[str, Any]:
        """
        Mark a task as completed. For recurring tasks, creates the next occurrence.

        Args:
            task_id: UUID of the task to complete

        Returns:
            {task_id, status, data, next_occurrence} with completed task and optional next task

        Raises:
            MCPToolError: If task not found or access denied
        """
        try:
            task_uuid = UUID(task_id)
        except ValueError as e:
            raise MCPToolError("invalid_task_id", "Invalid task ID format") from e

        task_service = TaskService(self.session)
        completed_task, next_task = await task_service.complete_recurring_task(
            task_uuid, self.user_id
        )

        if not completed_task:
            raise MCPToolError("task_not_found", "Task not found or access denied")

        result = {
            "task_id": str(completed_task.id),
            "status": "success",
            "data": self._task_to_dict(completed_task),
        }

        if next_task:
            result["next_occurrence"] = self._task_to_dict(next_task)
            result["message"] = f"Task completed. Next occurrence created for {next_task.due_date.strftime('%Y-%m-%d') if next_task.due_date else 'N/A'}"

        return result

    async def delete_task(self, task_id: str) -> dict[str, Any]:
        """
        Delete a task.

        Args:
            task_id: UUID of the task to delete

        Returns:
            {task_id, status} confirming deletion

        Raises:
            MCPToolError: If task not found or access denied
        """
        try:
            task_uuid = UUID(task_id)
        except ValueError as e:
            raise MCPToolError("invalid_task_id", "Invalid task ID format") from e

        task = await self.task_repo.get_by_id_and_user(task_uuid, self.user_id)
        if not task:
            raise MCPToolError("task_not_found", "Task not found or access denied")

        await self.task_repo.delete(task)

        return {
            "task_id": task_id,
            "status": "success",
        }

    async def update_task(
        self,
        task_id: str,
        title: str | None = None,
        description: str | None = None,
        due_date: str | None = None,
        priority: str | None = None,
        category: str | None = None,
        recurrence_rule: str | None = None,
        clear_due_date: bool = False,
        clear_priority: bool = False,
        clear_category: bool = False,
        clear_recurrence: bool = False,
    ) -> dict[str, Any]:
        """
        Update task fields.

        Args:
            task_id: UUID of the task to update
            title: New task title (optional)
            description: New task description (optional)
            due_date: New due date in ISO format (optional)
            priority: New priority level ("low", "normal", "high", "urgent") (optional)
            category: New category (optional)
            recurrence_rule: New recurrence pattern ("none", "daily", "weekly", "monthly") (optional)
            clear_due_date: Set to True to remove the due date
            clear_priority: Set to True to remove the priority
            clear_category: Set to True to remove the category
            clear_recurrence: Set to True to remove the recurrence (set to "none")

        Returns:
            {task_id, status, data} with updated task details

        Raises:
            MCPToolError: If task not found, access denied, or no updates provided
        """
        has_updates = any([
            title is not None,
            description is not None,
            due_date is not None,
            priority is not None,
            category is not None,
            recurrence_rule is not None,
            clear_due_date,
            clear_priority,
            clear_category,
            clear_recurrence,
        ])
        if not has_updates:
            raise MCPToolError("no_updates", "Must provide at least one field to update")

        try:
            task_uuid = UUID(task_id)
        except ValueError as e:
            raise MCPToolError("invalid_task_id", "Invalid task ID format") from e

        task = await self.task_repo.get_by_id_and_user(task_uuid, self.user_id)
        if not task:
            raise MCPToolError("task_not_found", "Task not found or access denied")

        if title is not None:
            if len(title.strip()) == 0:
                raise MCPToolError("invalid_title", "Task title cannot be empty")
            if len(title) > 200:
                raise MCPToolError("invalid_title", "Task title cannot exceed 200 characters")
            task.title = title.strip()

        if description is not None:
            task.description = description.strip() if description else None

        # Handle due date
        if clear_due_date:
            task.due_date = None
        elif due_date is not None:
            try:
                task.due_date = datetime.fromisoformat(due_date.replace("Z", "+00:00"))
            except ValueError as e:
                raise MCPToolError("invalid_due_date", f"Invalid due date format: {due_date}") from e

        # Handle priority
        if clear_priority:
            task.priority = None
        elif priority is not None:
            try:
                task.priority = Priority(priority.lower())
            except ValueError as e:
                raise MCPToolError(
                    "invalid_priority",
                    f"Invalid priority '{priority}'. Must be one of: low, normal, high, urgent"
                ) from e

        # Handle category
        if clear_category:
            task.category = None
        elif category is not None:
            parsed_category = category.strip()
            if len(parsed_category) > 50:
                raise MCPToolError("invalid_category", "Category cannot exceed 50 characters")
            task.category = parsed_category if parsed_category else None

        # Handle recurrence rule
        if clear_recurrence:
            task.recurrence_rule = RecurrenceRule.NONE
        elif recurrence_rule is not None:
            try:
                task.recurrence_rule = RecurrenceRule(recurrence_rule.lower())
            except ValueError as e:
                raise MCPToolError(
                    "invalid_recurrence",
                    f"Invalid recurrence rule '{recurrence_rule}'. Must be one of: none, daily, weekly, monthly"
                ) from e

        task.updated_at = datetime.utcnow()
        task = await self.task_repo.update(task)

        return {
            "task_id": str(task.id),
            "status": "success",
            "data": self._task_to_dict(task),
        }

    async def uncomplete_task(self, task_id: str) -> dict[str, Any]:
        """
        Mark a task as not completed (undo completion).

        Args:
            task_id: UUID of the task to uncomplete

        Returns:
            {task_id, status, data} with updated task details

        Raises:
            MCPToolError: If task not found or access denied
        """
        try:
            task_uuid = UUID(task_id)
        except ValueError as e:
            raise MCPToolError("invalid_task_id", "Invalid task ID format") from e

        task = await self.task_repo.get_by_id_and_user(task_uuid, self.user_id)
        if not task:
            raise MCPToolError("task_not_found", "Task not found or access denied")

        task.completed = False
        task.updated_at = datetime.utcnow()
        task = await self.task_repo.update(task)

        return {
            "task_id": str(task.id),
            "status": "success",
            "data": self._task_to_dict(task),
        }

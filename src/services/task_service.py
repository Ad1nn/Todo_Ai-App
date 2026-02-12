"""TaskService - Business logic for task management."""

from dataclasses import replace

from src.models.task import Task
from src.storage.memory_store import MemoryStore


class TaskService:
    """Service layer for task management operations.

    Coordinates between CLI layer and storage layer, handling
    validation and business rules for all task operations.
    """

    def __init__(self, store: MemoryStore) -> None:
        """Initialize service with a storage backend.

        Args:
            store: Storage implementation for persisting tasks
        """
        self._store = store

    def add_task(self, title: str, description: str = "") -> Task:
        """Create a new task with the given title and description.

        Args:
            title: The task title (required, non-empty)
            description: Optional task description (defaults to empty string)

        Returns:
            The created Task with auto-generated ID and completed=False

        Raises:
            ValueError: If title is empty or whitespace-only
        """
        # Task validation happens in Task.__post_init__
        task = Task(id=0, title=title, description=description, completed=False)
        return self._store.add(task)

    def get_task(self, task_id: int) -> Task | None:
        """Retrieve a task by its ID.

        Args:
            task_id: The unique identifier of the task

        Returns:
            The Task if found, None otherwise
        """
        return self._store.get(task_id)

    def get_all_tasks(self) -> list[Task]:
        """Retrieve all tasks.

        Returns:
            List of all tasks (may be empty)
        """
        return self._store.get_all()

    def update_task(
        self, task_id: int, title: str | None = None, description: str | None = None
    ) -> Task | None:
        """Update an existing task's title and/or description.

        Args:
            task_id: The unique identifier of the task to update
            title: New title (if provided, must be non-empty)
            description: New description (if provided)

        Returns:
            The updated Task if found, None otherwise

        Raises:
            ValueError: If title is provided but empty
        """
        existing = self._store.get(task_id)
        if existing is None:
            return None

        # Validate new title if provided
        new_title = title if title is not None else existing.title
        new_description = description if description is not None else existing.description

        # Create updated task (validation in Task.__post_init__)
        updated = Task(
            id=existing.id,
            title=new_title,
            description=new_description,
            completed=existing.completed,
        )

        return self._store.update(updated)

    def delete_task(self, task_id: int) -> bool:
        """Delete a task by its ID.

        Args:
            task_id: The unique identifier of the task to delete

        Returns:
            True if task was found and deleted, False otherwise
        """
        return self._store.delete(task_id)

    def toggle_complete(self, task_id: int) -> Task | None:
        """Toggle a task's completion status.

        Args:
            task_id: The unique identifier of the task

        Returns:
            The updated Task if found, None otherwise
        """
        existing = self._store.get(task_id)
        if existing is None:
            return None

        toggled = replace(existing, completed=not existing.completed)
        return self._store.update(toggled)

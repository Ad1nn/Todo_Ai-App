"""
Service Layer Contract: TaskService

This file defines the interface contract for the TaskService.
Implementation must adhere to these signatures and behaviors.

Feature: 001-console-todo-app
Date: 2026-01-18
Phase: 1 Design
"""

from typing import Protocol

# Note: Task is imported from models.task in actual implementation
# This contract uses a Protocol to avoid circular imports


class TaskProtocol(Protocol):
    """Protocol defining Task entity structure."""

    id: int
    title: str
    description: str
    completed: bool


class TaskServiceContract(Protocol):
    """
    Contract for TaskService implementation.

    The TaskService is responsible for all business logic related to task management.
    It coordinates between the CLI layer (user input) and the storage layer (data persistence).
    """

    def add_task(self, title: str, description: str = "") -> TaskProtocol:
        """
        Create a new task with the given title and description.

        Args:
            title: The task title (required, non-empty)
            description: Optional task description (defaults to empty string)

        Returns:
            The created Task with auto-generated ID and completed=False

        Raises:
            ValueError: If title is empty or whitespace-only

        Spec Reference: FR-001, FR-002, FR-003
        """
        ...

    def get_task(self, task_id: int) -> TaskProtocol | None:
        """
        Retrieve a task by its ID.

        Args:
            task_id: The unique identifier of the task

        Returns:
            The Task if found, None otherwise

        Spec Reference: FR-004
        """
        ...

    def get_all_tasks(self) -> list[TaskProtocol]:
        """
        Retrieve all tasks.

        Returns:
            List of all tasks (may be empty)

        Spec Reference: FR-004
        """
        ...

    def update_task(
        self, task_id: int, title: str | None = None, description: str | None = None
    ) -> TaskProtocol | None:
        """
        Update an existing task's title and/or description.

        Args:
            task_id: The unique identifier of the task to update
            title: New title (if provided, must be non-empty)
            description: New description (if provided)

        Returns:
            The updated Task if found, None otherwise

        Raises:
            ValueError: If title is provided but empty

        Spec Reference: FR-007, FR-010
        """
        ...

    def delete_task(self, task_id: int) -> bool:
        """
        Delete a task by its ID.

        Args:
            task_id: The unique identifier of the task to delete

        Returns:
            True if task was found and deleted, False otherwise

        Spec Reference: FR-008, FR-009
        """
        ...

    def toggle_complete(self, task_id: int) -> TaskProtocol | None:
        """
        Toggle a task's completion status.

        Args:
            task_id: The unique identifier of the task

        Returns:
            The updated Task if found, None otherwise

        Spec Reference: FR-006
        """
        ...


class StorageContract(Protocol):
    """
    Contract for Storage layer implementation.

    The storage layer handles data persistence. In Phase 1, this is in-memory.
    Future phases may implement database storage with the same interface.
    """

    def add(self, task: TaskProtocol) -> TaskProtocol:
        """Store a new task and return it with assigned ID."""
        ...

    def get(self, task_id: int) -> TaskProtocol | None:
        """Retrieve a task by ID, or None if not found."""
        ...

    def get_all(self) -> list[TaskProtocol]:
        """Retrieve all stored tasks."""
        ...

    def update(self, task: TaskProtocol) -> TaskProtocol | None:
        """Update an existing task, or return None if not found."""
        ...

    def delete(self, task_id: int) -> bool:
        """Delete a task by ID. Return True if deleted, False if not found."""
        ...

    def next_id(self) -> int:
        """Generate and return the next available task ID."""
        ...


# Error Messages (for consistency across implementation)
ERROR_MESSAGES = {
    "empty_title": "Error: Task title cannot be empty.",
    "task_not_found": "Error: Task with ID {task_id} not found.",
    "invalid_id": "Error: Please enter a valid numeric ID.",
    "invalid_option": "Error: Invalid option. Please try again.",
}

# Success Messages
SUCCESS_MESSAGES = {
    "task_added": "Task added successfully with ID {task_id}.",
    "task_updated": "Task {task_id} updated successfully.",
    "task_deleted": "Task {task_id} deleted successfully.",
    "task_completed": "Task {task_id} marked as complete.",
    "task_incomplete": "Task {task_id} marked as incomplete.",
}

# Display Constants
DISPLAY = {
    "complete_indicator": "[x]",
    "incomplete_indicator": "[ ]",
    "empty_list_message": "No tasks found. Add a task to get started!",
}

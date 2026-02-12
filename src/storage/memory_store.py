"""In-memory storage for tasks using Python dict."""

from dataclasses import replace

from src.models.task import Task


class MemoryStore:
    """In-memory storage implementation using dict.

    Stores tasks in a dictionary keyed by task ID.
    IDs are auto-generated and never reused within a session.
    """

    def __init__(self) -> None:
        """Initialize empty storage."""
        self._tasks: dict[int, Task] = {}
        self._next_id: int = 1

    def add(self, task: Task) -> Task:
        """Store a new task and return it with assigned ID.

        Args:
            task: Task to store (id field will be replaced with generated ID)

        Returns:
            The stored task with its assigned ID
        """
        new_id = self.next_id()
        stored_task = replace(task, id=new_id)
        self._tasks[new_id] = stored_task
        return stored_task

    def get(self, task_id: int) -> Task | None:
        """Retrieve a task by ID.

        Args:
            task_id: The unique identifier of the task

        Returns:
            The Task if found, None otherwise
        """
        return self._tasks.get(task_id)

    def get_all(self) -> list[Task]:
        """Retrieve all stored tasks.

        Returns:
            List of all tasks (may be empty)
        """
        return list(self._tasks.values())

    def update(self, task: Task) -> Task | None:
        """Update an existing task.

        Args:
            task: Task with updated values (id must match existing task)

        Returns:
            The updated Task if found, None otherwise
        """
        if task.id not in self._tasks:
            return None
        self._tasks[task.id] = task
        return task

    def delete(self, task_id: int) -> bool:
        """Delete a task by ID.

        Args:
            task_id: The unique identifier of the task to delete

        Returns:
            True if task was found and deleted, False otherwise
        """
        if task_id not in self._tasks:
            return False
        del self._tasks[task_id]
        return True

    def next_id(self) -> int:
        """Generate and return the next available task ID.

        Returns:
            The next available ID (increments internal counter)
        """
        current_id = self._next_id
        self._next_id += 1
        return current_id

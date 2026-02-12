"""Unit tests for TaskService business logic."""

import pytest
from src.services.task_service import TaskService
from src.storage.memory_store import MemoryStore


@pytest.fixture
def service() -> TaskService:
    """Create a TaskService with fresh MemoryStore."""
    return TaskService(MemoryStore())


# =============================================================================
# User Story 1: Add a New Task (T016, T017)
# =============================================================================


class TestAddTask:
    """Tests for TaskService.add_task() - US1."""

    def test_add_task_with_title_and_description(self, service: TaskService) -> None:
        """Adding task with title and description should succeed."""
        task = service.add_task("Buy groceries", "Milk, eggs, bread")

        assert task.id == 1
        assert task.title == "Buy groceries"
        assert task.description == "Milk, eggs, bread"
        assert task.completed is False

    def test_add_task_with_title_only(self, service: TaskService) -> None:
        """Adding task with only title should succeed with empty description."""
        task = service.add_task("Call mom")

        assert task.id == 1
        assert task.title == "Call mom"
        assert task.description == ""
        assert task.completed is False

    def test_add_task_assigns_sequential_ids(self, service: TaskService) -> None:
        """Multiple tasks should get sequential IDs."""
        task1 = service.add_task("First")
        task2 = service.add_task("Second")
        task3 = service.add_task("Third")

        assert task1.id == 1
        assert task2.id == 2
        assert task3.id == 3

    def test_add_task_empty_title_raises_error(self, service: TaskService) -> None:
        """Adding task with empty title should raise ValueError."""
        with pytest.raises(ValueError, match="Task title cannot be empty"):
            service.add_task("")

    def test_add_task_whitespace_title_raises_error(self, service: TaskService) -> None:
        """Adding task with whitespace-only title should raise ValueError."""
        with pytest.raises(ValueError, match="Task title cannot be empty"):
            service.add_task("   ")


# =============================================================================
# User Story 2: View All Tasks (T023, T024)
# =============================================================================


class TestGetAllTasks:
    """Tests for TaskService.get_all_tasks() - US2."""

    def test_get_all_empty_returns_empty_list(self, service: TaskService) -> None:
        """Getting all from empty service should return empty list."""
        tasks = service.get_all_tasks()

        assert tasks == []

    def test_get_all_returns_all_tasks(self, service: TaskService) -> None:
        """Getting all should return all added tasks."""
        service.add_task("First", "Desc 1")
        service.add_task("Second", "Desc 2")
        service.add_task("Third", "Desc 3")

        tasks = service.get_all_tasks()

        assert len(tasks) == 3
        titles = [t.title for t in tasks]
        assert "First" in titles
        assert "Second" in titles
        assert "Third" in titles

    def test_get_all_includes_completed_tasks(self, service: TaskService) -> None:
        """Getting all should include both complete and incomplete tasks."""
        service.add_task("Incomplete")
        task2 = service.add_task("Complete")
        service.toggle_complete(task2.id)

        tasks = service.get_all_tasks()

        assert len(tasks) == 2
        statuses = {t.title: t.completed for t in tasks}
        assert statuses["Incomplete"] is False
        assert statuses["Complete"] is True


# =============================================================================
# User Story 3: Mark Task as Complete (T030, T031)
# =============================================================================


class TestToggleComplete:
    """Tests for TaskService.toggle_complete() - US3."""

    def test_toggle_incomplete_to_complete(self, service: TaskService) -> None:
        """Toggling incomplete task should mark it complete."""
        task = service.add_task("Test task")
        assert task.completed is False

        result = service.toggle_complete(task.id)

        assert result is not None
        assert result.completed is True

    def test_toggle_complete_to_incomplete(self, service: TaskService) -> None:
        """Toggling complete task should mark it incomplete."""
        task = service.add_task("Test task")
        service.toggle_complete(task.id)  # Now complete

        result = service.toggle_complete(task.id)

        assert result is not None
        assert result.completed is False

    def test_toggle_persists_change(self, service: TaskService) -> None:
        """Toggle should persist the change in storage."""
        task = service.add_task("Test task")
        service.toggle_complete(task.id)

        retrieved = service.get_task(task.id)

        assert retrieved is not None
        assert retrieved.completed is True

    def test_toggle_invalid_id_returns_none(self, service: TaskService) -> None:
        """Toggling non-existent task should return None."""
        result = service.toggle_complete(999)

        assert result is None


# =============================================================================
# User Story 4: Update Task Details (T037, T038)
# =============================================================================


class TestUpdateTask:
    """Tests for TaskService.update_task() - US4."""

    def test_update_title_only(self, service: TaskService) -> None:
        """Updating only title should change title, keep description."""
        task = service.add_task("Original", "Original desc")

        result = service.update_task(task.id, title="Updated")

        assert result is not None
        assert result.title == "Updated"
        assert result.description == "Original desc"

    def test_update_description_only(self, service: TaskService) -> None:
        """Updating only description should change description, keep title."""
        task = service.add_task("Original", "Original desc")

        result = service.update_task(task.id, description="New desc")

        assert result is not None
        assert result.title == "Original"
        assert result.description == "New desc"

    def test_update_both_title_and_description(self, service: TaskService) -> None:
        """Updating both fields should change both."""
        task = service.add_task("Original", "Original desc")

        result = service.update_task(task.id, title="New title", description="New desc")

        assert result is not None
        assert result.title == "New title"
        assert result.description == "New desc"

    def test_update_preserves_completion_status(self, service: TaskService) -> None:
        """Update should preserve completion status."""
        task = service.add_task("Test")
        service.toggle_complete(task.id)

        result = service.update_task(task.id, title="Updated")

        assert result is not None
        assert result.completed is True

    def test_update_invalid_id_returns_none(self, service: TaskService) -> None:
        """Updating non-existent task should return None."""
        result = service.update_task(999, title="Test")

        assert result is None

    def test_update_empty_title_raises_error(self, service: TaskService) -> None:
        """Updating with empty title should raise ValueError."""
        task = service.add_task("Original")

        with pytest.raises(ValueError, match="Task title cannot be empty"):
            service.update_task(task.id, title="")

    def test_update_whitespace_title_raises_error(self, service: TaskService) -> None:
        """Updating with whitespace title should raise ValueError."""
        task = service.add_task("Original")

        with pytest.raises(ValueError, match="Task title cannot be empty"):
            service.update_task(task.id, title="   ")


# =============================================================================
# User Story 5: Delete a Task (T044, T045)
# =============================================================================


class TestDeleteTask:
    """Tests for TaskService.delete_task() - US5."""

    def test_delete_existing_task(self, service: TaskService) -> None:
        """Deleting existing task should return True."""
        task = service.add_task("Test task")

        result = service.delete_task(task.id)

        assert result is True

    def test_delete_removes_from_storage(self, service: TaskService) -> None:
        """Deleted task should no longer be retrievable."""
        task = service.add_task("Test task")
        service.delete_task(task.id)

        retrieved = service.get_task(task.id)

        assert retrieved is None

    def test_delete_invalid_id_returns_false(self, service: TaskService) -> None:
        """Deleting non-existent task should return False."""
        result = service.delete_task(999)

        assert result is False

    def test_delete_does_not_affect_other_tasks(self, service: TaskService) -> None:
        """Deleting one task should not affect others."""
        task1 = service.add_task("First")
        task2 = service.add_task("Second")
        service.delete_task(task1.id)

        tasks = service.get_all_tasks()

        assert len(tasks) == 1
        assert tasks[0].id == task2.id


# =============================================================================
# Additional: get_task (used for validation)
# =============================================================================


class TestGetTask:
    """Tests for TaskService.get_task()."""

    def test_get_existing_task(self, service: TaskService) -> None:
        """Getting existing task should return it."""
        added = service.add_task("Test", "Description")

        task = service.get_task(added.id)

        assert task is not None
        assert task.id == added.id
        assert task.title == "Test"

    def test_get_nonexistent_task_returns_none(self, service: TaskService) -> None:
        """Getting non-existent task should return None."""
        task = service.get_task(999)

        assert task is None

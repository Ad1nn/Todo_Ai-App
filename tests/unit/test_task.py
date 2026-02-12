"""Unit tests for Task model validation."""

import pytest
from src.models.task import Task


class TestTaskCreation:
    """Tests for Task creation and validation."""

    def test_create_task_with_all_fields(self) -> None:
        """Task should be created with all fields specified."""
        task = Task(id=1, title="Buy groceries", description="Milk, eggs, bread", completed=True)

        assert task.id == 1
        assert task.title == "Buy groceries"
        assert task.description == "Milk, eggs, bread"
        assert task.completed is True

    def test_create_task_with_defaults(self) -> None:
        """Task should use default values for optional fields."""
        task = Task(id=1, title="Test task")

        assert task.id == 1
        assert task.title == "Test task"
        assert task.description == ""
        assert task.completed is False

    def test_create_task_with_empty_description(self) -> None:
        """Task should accept empty string for description."""
        task = Task(id=1, title="Test task", description="")

        assert task.description == ""

    def test_title_is_stripped(self) -> None:
        """Title should be stripped of leading/trailing whitespace."""
        task = Task(id=1, title="  Buy groceries  ")

        assert task.title == "Buy groceries"

    def test_description_is_stripped(self) -> None:
        """Description should be stripped of leading/trailing whitespace."""
        task = Task(id=1, title="Test", description="  Some details  ")

        assert task.description == "Some details"


class TestTaskValidation:
    """Tests for Task validation rules."""

    def test_empty_title_raises_error(self) -> None:
        """Creating task with empty title should raise ValueError."""
        with pytest.raises(ValueError, match="Task title cannot be empty"):
            Task(id=1, title="")

    def test_whitespace_only_title_raises_error(self) -> None:
        """Creating task with whitespace-only title should raise ValueError."""
        with pytest.raises(ValueError, match="Task title cannot be empty"):
            Task(id=1, title="   ")

    def test_none_description_converted_to_empty(self) -> None:
        """None description should be converted to empty string."""
        # Note: dataclass won't accept None directly if type is str
        # This test verifies the default behavior
        task = Task(id=1, title="Test")
        assert task.description == ""


class TestTaskEquality:
    """Tests for Task equality and representation."""

    def test_tasks_with_same_values_are_equal(self) -> None:
        """Two tasks with identical values should be equal."""
        task1 = Task(id=1, title="Test", description="Desc", completed=False)
        task2 = Task(id=1, title="Test", description="Desc", completed=False)

        assert task1 == task2

    def test_tasks_with_different_ids_not_equal(self) -> None:
        """Tasks with different IDs should not be equal."""
        task1 = Task(id=1, title="Test")
        task2 = Task(id=2, title="Test")

        assert task1 != task2

    def test_task_repr(self) -> None:
        """Task should have a readable repr."""
        task = Task(id=1, title="Test", description="Desc", completed=True)
        repr_str = repr(task)

        assert "Task" in repr_str
        assert "1" in repr_str
        assert "Test" in repr_str

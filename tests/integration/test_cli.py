"""Integration tests for CLI menu workflow."""

import io
from unittest.mock import patch

import pytest
from src.cli.menu import Menu
from src.services.task_service import TaskService
from src.storage.memory_store import MemoryStore


@pytest.fixture
def menu() -> Menu:
    """Create a Menu with fresh service and storage."""
    store = MemoryStore()
    service = TaskService(store)
    return Menu(service)


class TestMenuAddTask:
    """Integration tests for add task workflow."""

    def test_add_task_with_title_and_description(self, menu: Menu) -> None:
        """Adding task via menu should work with title and description."""
        inputs = ["Buy groceries", "Milk, eggs, bread"]

        with (
            patch("builtins.input", side_effect=inputs),
            patch("sys.stdout", new=io.StringIO()) as output,
        ):
            menu.add_task()

        output_text = output.getvalue()
        assert "Task added successfully" in output_text
        assert "ID 1" in output_text

    def test_add_task_with_empty_title_shows_error(self, menu: Menu) -> None:
        """Adding task with empty title should show error."""
        inputs = ["", "Some description"]

        with (
            patch("builtins.input", side_effect=inputs),
            patch("sys.stdout", new=io.StringIO()) as output,
        ):
            menu.add_task()

        output_text = output.getvalue()
        assert "Error" in output_text
        assert "title cannot be empty" in output_text.lower()


class TestMenuViewTasks:
    """Integration tests for view tasks workflow."""

    def test_view_empty_list_shows_message(self, menu: Menu) -> None:
        """Viewing empty list should show appropriate message."""
        with patch("sys.stdout", new=io.StringIO()) as output:
            menu.view_tasks()

        output_text = output.getvalue()
        assert "No tasks found" in output_text or "empty" in output_text.lower()

    def test_view_tasks_shows_all_tasks(self, menu: Menu) -> None:
        """Viewing tasks should show all added tasks."""
        # Add some tasks first
        with patch("builtins.input", side_effect=["First task", "Desc 1"]):
            menu.add_task()
        with patch("builtins.input", side_effect=["Second task", "Desc 2"]):
            menu.add_task()

        with patch("sys.stdout", new=io.StringIO()) as output:
            menu.view_tasks()

        output_text = output.getvalue()
        assert "First task" in output_text
        assert "Second task" in output_text

    def test_view_tasks_shows_status_indicators(self, menu: Menu) -> None:
        """View should show completion status indicators."""
        with patch("builtins.input", side_effect=["Test task", ""]):
            menu.add_task()

        with patch("sys.stdout", new=io.StringIO()) as output:
            menu.view_tasks()

        output_text = output.getvalue()
        assert "[ ]" in output_text or "[x]" in output_text


class TestMenuToggleComplete:
    """Integration tests for toggle complete workflow."""

    def test_toggle_complete_changes_status(self, menu: Menu) -> None:
        """Toggling should change completion status."""
        # Add a task
        with patch("builtins.input", side_effect=["Test task", ""]):
            menu.add_task()

        # Toggle complete
        with (
            patch("builtins.input", side_effect=["1"]),
            patch("sys.stdout", new=io.StringIO()) as output,
        ):
            menu.toggle_complete()

        output_text = output.getvalue()
        assert "marked as complete" in output_text.lower() or "Task 1" in output_text

    def test_toggle_invalid_id_shows_error(self, menu: Menu) -> None:
        """Toggling non-existent task should show error."""
        with (
            patch("builtins.input", side_effect=["999"]),
            patch("sys.stdout", new=io.StringIO()) as output,
        ):
            menu.toggle_complete()

        output_text = output.getvalue()
        assert "not found" in output_text.lower() or "Error" in output_text

    def test_toggle_non_numeric_input_shows_error(self, menu: Menu) -> None:
        """Non-numeric ID input should show error."""
        with (
            patch("builtins.input", side_effect=["abc"]),
            patch("sys.stdout", new=io.StringIO()) as output,
        ):
            menu.toggle_complete()

        output_text = output.getvalue()
        assert "valid" in output_text.lower() or "Error" in output_text


class TestMenuUpdateTask:
    """Integration tests for update task workflow."""

    def test_update_task_title(self, menu: Menu) -> None:
        """Updating task title should work."""
        # Add a task
        with patch("builtins.input", side_effect=["Original", "Desc"]):
            menu.add_task()

        # Update title (empty description keeps original)
        with (
            patch("builtins.input", side_effect=["1", "Updated title", ""]),
            patch("sys.stdout", new=io.StringIO()) as output,
        ):
            menu.update_task()

        output_text = output.getvalue()
        assert "updated" in output_text.lower()

    def test_update_invalid_id_shows_error(self, menu: Menu) -> None:
        """Updating non-existent task should show error."""
        with (
            patch("builtins.input", side_effect=["999", "New title", "New desc"]),
            patch("sys.stdout", new=io.StringIO()) as output,
        ):
            menu.update_task()

        output_text = output.getvalue()
        assert "not found" in output_text.lower() or "Error" in output_text


class TestMenuDeleteTask:
    """Integration tests for delete task workflow."""

    def test_delete_task_removes_it(self, menu: Menu) -> None:
        """Deleting task should remove it from list."""
        # Add a task
        with patch("builtins.input", side_effect=["Test task", ""]):
            menu.add_task()

        # Delete it
        with (
            patch("builtins.input", side_effect=["1"]),
            patch("sys.stdout", new=io.StringIO()) as output,
        ):
            menu.delete_task()

        output_text = output.getvalue()
        assert "deleted" in output_text.lower()

    def test_delete_invalid_id_shows_error(self, menu: Menu) -> None:
        """Deleting non-existent task should show error."""
        with (
            patch("builtins.input", side_effect=["999"]),
            patch("sys.stdout", new=io.StringIO()) as output,
        ):
            menu.delete_task()

        output_text = output.getvalue()
        assert "not found" in output_text.lower() or "Error" in output_text


class TestMenuDisplay:
    """Tests for menu display."""

    def test_display_menu_shows_all_options(self, menu: Menu) -> None:
        """Menu display should show all options."""
        with patch("sys.stdout", new=io.StringIO()) as output:
            menu.display_menu()

        output_text = output.getvalue()
        assert "1" in output_text and "Add" in output_text
        assert "2" in output_text and "View" in output_text
        assert "3" in output_text
        assert "4" in output_text
        assert "5" in output_text
        assert "6" in output_text and "Exit" in output_text


class TestMenuInvalidOption:
    """Tests for invalid menu options."""

    def test_invalid_option_shows_error(self, menu: Menu) -> None:
        """Invalid option should show error message."""
        with patch("sys.stdout", new=io.StringIO()) as output:
            result = menu.process_choice("99")

        output_text = output.getvalue()
        assert "Invalid" in output_text or "Error" in output_text
        assert result is True  # Should continue running

    def test_non_numeric_option_shows_error(self, menu: Menu) -> None:
        """Non-numeric option should show error message."""
        with patch("sys.stdout", new=io.StringIO()) as output:
            menu.process_choice("abc")

        output_text = output.getvalue()
        assert "Invalid" in output_text or "Error" in output_text


class TestMenuExit:
    """Tests for exit functionality."""

    def test_exit_option_returns_false(self, menu: Menu) -> None:
        """Exit option should return False to stop loop."""
        result = menu.process_choice("6")

        assert result is False

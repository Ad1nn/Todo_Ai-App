"""Unit tests for TaskService."""

from datetime import datetime, timedelta
from uuid import uuid4

import pytest

from src.models.task import Priority
from src.services.task_service import TaskService


class TestTaskServiceCreate:
    """Tests for task creation."""

    @pytest.mark.asyncio
    async def test_create_task_success(self, db_session, test_user):
        """Create task returns new task with provided data."""
        task_service = TaskService(db_session)

        task = await task_service.create(
            user_id=test_user.id,
            title="Test Task",
            description="Test description"
        )

        assert task is not None
        assert task.title == "Test Task"
        assert task.description == "Test description"
        assert task.user_id == test_user.id
        assert task.completed is False

    @pytest.mark.asyncio
    async def test_create_task_without_description(self, db_session, test_user):
        """Create task without description succeeds."""
        task_service = TaskService(db_session)

        task = await task_service.create(
            user_id=test_user.id,
            title="Test Task"
        )

        assert task is not None
        assert task.title == "Test Task"
        assert task.description is None


class TestTaskServiceList:
    """Tests for listing tasks."""

    @pytest.mark.asyncio
    async def test_list_tasks_empty(self, db_session, test_user):
        """List tasks returns empty list for user with no tasks."""
        task_service = TaskService(db_session)

        tasks = await task_service.list_by_user(test_user.id)

        assert tasks == []

    @pytest.mark.asyncio
    async def test_list_tasks_returns_user_tasks(self, db_session, test_user):
        """List tasks returns all tasks for the user."""
        task_service = TaskService(db_session)

        # Create multiple tasks
        await task_service.create(user_id=test_user.id, title="Task 1")
        await task_service.create(user_id=test_user.id, title="Task 2")
        await task_service.create(user_id=test_user.id, title="Task 3")

        tasks = await task_service.list_by_user(test_user.id)

        assert len(tasks) == 3
        titles = [t.title for t in tasks]
        assert "Task 1" in titles
        assert "Task 2" in titles
        assert "Task 3" in titles

    @pytest.mark.asyncio
    async def test_list_tasks_isolates_users(self, db_session, test_user):
        """List tasks only returns tasks for the specified user."""
        task_service = TaskService(db_session)

        # Create task for test user
        await task_service.create(user_id=test_user.id, title="User Task")

        # Verify only user's own tasks are returned (isolation)
        tasks = await task_service.list_by_user(test_user.id)

        assert len(tasks) == 1
        assert tasks[0].title == "User Task"


class TestTaskServiceGet:
    """Tests for getting a single task."""

    @pytest.mark.asyncio
    async def test_get_task_success(self, db_session, test_user):
        """Get task returns the task if it exists and belongs to user."""
        task_service = TaskService(db_session)

        created = await task_service.create(
            user_id=test_user.id,
            title="Test Task"
        )

        task = await task_service.get_by_id(created.id, test_user.id)

        assert task is not None
        assert task.id == created.id

    @pytest.mark.asyncio
    async def test_get_task_not_found(self, db_session, test_user):
        """Get task returns None for non-existent task."""
        task_service = TaskService(db_session)

        task = await task_service.get_by_id(uuid4(), test_user.id)

        assert task is None

    @pytest.mark.asyncio
    async def test_get_task_wrong_user(self, db_session, test_user):
        """Get task returns None for task belonging to different user."""
        task_service = TaskService(db_session)

        created = await task_service.create(
            user_id=test_user.id,
            title="Test Task"
        )

        # Try to access with different user
        task = await task_service.get_by_id(created.id, uuid4())

        assert task is None


class TestTaskServiceEnhancements:
    """Tests for task enhancement fields: due_date, priority, category."""

    @pytest.mark.asyncio
    async def test_create_task_with_enhancements(self, db_session, test_user):
        """Create task with due_date, priority, and category."""
        task_service = TaskService(db_session)
        due_date = datetime.utcnow() + timedelta(days=7)

        task = await task_service.create(
            user_id=test_user.id,
            title="Enhanced Task",
            due_date=due_date,
            priority=Priority.HIGH,
            category="work"
        )

        assert task is not None
        assert task.due_date is not None
        assert task.priority == Priority.HIGH
        assert task.category == "work"

    @pytest.mark.asyncio
    async def test_create_task_without_enhancements(self, db_session, test_user):
        """Create task without enhancement fields (nullable)."""
        task_service = TaskService(db_session)

        task = await task_service.create(
            user_id=test_user.id,
            title="Basic Task"
        )

        assert task is not None
        assert task.due_date is None
        assert task.priority is None
        assert task.category is None

    @pytest.mark.asyncio
    async def test_update_task_enhancements(self, db_session, test_user):
        """Update task enhancement fields."""
        task_service = TaskService(db_session)
        due_date = datetime.utcnow() + timedelta(days=3)

        task = await task_service.create(
            user_id=test_user.id,
            title="Task to update"
        )

        updated = await task_service.update(
            task_id=task.id,
            user_id=test_user.id,
            due_date=due_date,
            priority=Priority.URGENT,
            category="personal"
        )

        assert updated is not None
        assert updated.due_date is not None
        assert updated.priority == Priority.URGENT
        assert updated.category == "personal"

    @pytest.mark.asyncio
    async def test_clear_enhancement_fields(self, db_session, test_user):
        """Clear enhancement fields using clear_* flags."""
        task_service = TaskService(db_session)
        due_date = datetime.utcnow() + timedelta(days=1)

        task = await task_service.create(
            user_id=test_user.id,
            title="Task with enhancements",
            due_date=due_date,
            priority=Priority.HIGH,
            category="work"
        )

        updated = await task_service.update(
            task_id=task.id,
            user_id=test_user.id,
            clear_due_date=True,
            clear_priority=True,
            clear_category=True
        )

        assert updated is not None
        assert updated.due_date is None
        assert updated.priority is None
        assert updated.category is None

    @pytest.mark.asyncio
    async def test_list_filtered_by_category(self, db_session, test_user):
        """List tasks filtered by category."""
        task_service = TaskService(db_session)

        await task_service.create(user_id=test_user.id, title="Work task", category="work")
        await task_service.create(user_id=test_user.id, title="Personal task", category="personal")

        work_tasks = await task_service.list_by_user_filtered(
            user_id=test_user.id,
            category="work"
        )

        assert len(work_tasks) == 1
        assert work_tasks[0].title == "Work task"

    @pytest.mark.asyncio
    async def test_list_filtered_by_priority(self, db_session, test_user):
        """List tasks filtered by priority."""
        task_service = TaskService(db_session)

        await task_service.create(user_id=test_user.id, title="Urgent task", priority=Priority.URGENT)
        await task_service.create(user_id=test_user.id, title="Low task", priority=Priority.LOW)

        urgent_tasks = await task_service.list_by_user_filtered(
            user_id=test_user.id,
            priority=Priority.URGENT
        )

        assert len(urgent_tasks) == 1
        assert urgent_tasks[0].title == "Urgent task"

    @pytest.mark.asyncio
    async def test_list_filtered_overdue(self, db_session, test_user):
        """List only overdue tasks."""
        task_service = TaskService(db_session)
        past = datetime.utcnow() - timedelta(days=1)
        future = datetime.utcnow() + timedelta(days=1)

        await task_service.create(user_id=test_user.id, title="Overdue", due_date=past)
        await task_service.create(user_id=test_user.id, title="Future", due_date=future)

        overdue_tasks = await task_service.list_by_user_filtered(
            user_id=test_user.id,
            overdue_only=True
        )

        assert len(overdue_tasks) == 1
        assert overdue_tasks[0].title == "Overdue"

    @pytest.mark.asyncio
    async def test_get_user_categories(self, db_session, test_user):
        """Get distinct categories for a user."""
        task_service = TaskService(db_session)

        await task_service.create(user_id=test_user.id, title="Task 1", category="work")
        await task_service.create(user_id=test_user.id, title="Task 2", category="personal")
        await task_service.create(user_id=test_user.id, title="Task 3", category="work")  # duplicate

        categories = await task_service.get_user_categories(test_user.id)

        assert len(categories) == 2
        assert "work" in categories
        assert "personal" in categories

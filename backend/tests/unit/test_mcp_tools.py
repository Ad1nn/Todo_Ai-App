"""Unit tests for MCP tools."""

from datetime import datetime, timedelta
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.mcp.tools import MCPToolError, MCPTools
from src.models.user import User
from src.services.auth_service import AuthService


@pytest.fixture
async def user_a(db_session: AsyncSession) -> User:
    """Create test user A."""
    auth_service = AuthService(db_session)
    user = await auth_service.register(
        email=f"user-a-{uuid4().hex[:8]}@example.com",
        password="password123",
    )
    return user


@pytest.fixture
async def user_b(db_session: AsyncSession) -> User:
    """Create test user B."""
    auth_service = AuthService(db_session)
    user = await auth_service.register(
        email=f"user-b-{uuid4().hex[:8]}@example.com",
        password="password123",
    )
    return user


@pytest.fixture
def mcp_tools_a(db_session: AsyncSession, user_a: User) -> MCPTools:
    """Create MCP tools instance for user A."""
    return MCPTools(db_session, user_a.id)


@pytest.fixture
def mcp_tools_b(db_session: AsyncSession, user_b: User) -> MCPTools:
    """Create MCP tools instance for user B."""
    return MCPTools(db_session, user_b.id)


class TestAddTask:
    """Tests for add_task MCP tool."""

    async def test_add_task_success(self, mcp_tools_a: MCPTools) -> None:
        """Test successful task creation."""
        result = await mcp_tools_a.add_task(
            title="Buy groceries",
            description="Milk, eggs, bread",
        )

        assert result["status"] == "success"
        assert result["task_id"] is not None
        assert result["data"]["title"] == "Buy groceries"
        assert result["data"]["description"] == "Milk, eggs, bread"
        assert result["data"]["completed"] is False

    async def test_add_task_without_description(self, mcp_tools_a: MCPTools) -> None:
        """Test task creation without description."""
        result = await mcp_tools_a.add_task(title="Simple task")

        assert result["status"] == "success"
        assert result["data"]["title"] == "Simple task"
        assert result["data"]["description"] is None

    async def test_add_task_empty_title_fails(self, mcp_tools_a: MCPTools) -> None:
        """Test that empty title raises error."""
        with pytest.raises(MCPToolError) as exc_info:
            await mcp_tools_a.add_task(title="")

        assert exc_info.value.code == "invalid_title"
        assert "empty" in exc_info.value.message.lower()

    async def test_add_task_whitespace_title_fails(self, mcp_tools_a: MCPTools) -> None:
        """Test that whitespace-only title raises error."""
        with pytest.raises(MCPToolError) as exc_info:
            await mcp_tools_a.add_task(title="   ")

        assert exc_info.value.code == "invalid_title"

    async def test_add_task_title_too_long_fails(self, mcp_tools_a: MCPTools) -> None:
        """Test that title exceeding 200 chars raises error."""
        long_title = "x" * 201
        with pytest.raises(MCPToolError) as exc_info:
            await mcp_tools_a.add_task(title=long_title)

        assert exc_info.value.code == "invalid_title"
        assert "200" in exc_info.value.message

    async def test_add_task_trims_whitespace(self, mcp_tools_a: MCPTools) -> None:
        """Test that title and description are trimmed."""
        result = await mcp_tools_a.add_task(
            title="  Trimmed title  ",
            description="  Trimmed description  ",
        )

        assert result["data"]["title"] == "Trimmed title"
        assert result["data"]["description"] == "Trimmed description"


class TestListTasks:
    """Tests for list_tasks MCP tool."""

    async def test_list_tasks_empty(self, mcp_tools_a: MCPTools) -> None:
        """Test listing tasks when none exist."""
        result = await mcp_tools_a.list_tasks()

        assert result["status"] == "success"
        assert result["tasks"] == []

    async def test_list_tasks_returns_all(self, mcp_tools_a: MCPTools) -> None:
        """Test listing all tasks."""
        await mcp_tools_a.add_task(title="Task 1")
        await mcp_tools_a.add_task(title="Task 2")

        result = await mcp_tools_a.list_tasks()

        assert result["status"] == "success"
        assert len(result["tasks"]) == 2

    async def test_list_tasks_filter_completed(self, mcp_tools_a: MCPTools) -> None:
        """Test filtering by completed status."""
        task_result = await mcp_tools_a.add_task(title="Task to complete")
        await mcp_tools_a.add_task(title="Pending task")
        await mcp_tools_a.complete_task(task_result["task_id"])

        completed = await mcp_tools_a.list_tasks(completed=True)
        pending = await mcp_tools_a.list_tasks(completed=False)

        assert len(completed["tasks"]) == 1
        assert completed["tasks"][0]["title"] == "Task to complete"
        assert len(pending["tasks"]) == 1
        assert pending["tasks"][0]["title"] == "Pending task"

    async def test_list_tasks_user_isolation(
        self, mcp_tools_a: MCPTools, mcp_tools_b: MCPTools
    ) -> None:
        """Test that users only see their own tasks."""
        await mcp_tools_a.add_task(title="User A task")
        await mcp_tools_b.add_task(title="User B task")

        result_a = await mcp_tools_a.list_tasks()
        result_b = await mcp_tools_b.list_tasks()

        assert len(result_a["tasks"]) == 1
        assert result_a["tasks"][0]["title"] == "User A task"
        assert len(result_b["tasks"]) == 1
        assert result_b["tasks"][0]["title"] == "User B task"


class TestCompleteTask:
    """Tests for complete_task MCP tool."""

    async def test_complete_task_success(self, mcp_tools_a: MCPTools) -> None:
        """Test successful task completion."""
        task_result = await mcp_tools_a.add_task(title="Task to complete")
        task_id = task_result["task_id"]

        result = await mcp_tools_a.complete_task(task_id)

        assert result["status"] == "success"
        assert result["data"]["completed"] is True

    async def test_complete_task_not_found(self, mcp_tools_a: MCPTools) -> None:
        """Test completing non-existent task."""
        fake_id = str(uuid4())
        with pytest.raises(MCPToolError) as exc_info:
            await mcp_tools_a.complete_task(fake_id)

        assert exc_info.value.code == "task_not_found"

    async def test_complete_task_invalid_uuid(self, mcp_tools_a: MCPTools) -> None:
        """Test completing with invalid UUID."""
        with pytest.raises(MCPToolError) as exc_info:
            await mcp_tools_a.complete_task("not-a-uuid")

        assert exc_info.value.code == "invalid_task_id"

    async def test_complete_task_user_isolation(
        self, mcp_tools_a: MCPTools, mcp_tools_b: MCPTools
    ) -> None:
        """Test that user A cannot complete user B's task."""
        task_result = await mcp_tools_a.add_task(title="User A's task")
        task_id = task_result["task_id"]

        with pytest.raises(MCPToolError) as exc_info:
            await mcp_tools_b.complete_task(task_id)

        assert exc_info.value.code == "task_not_found"


class TestDeleteTask:
    """Tests for delete_task MCP tool."""

    async def test_delete_task_success(self, mcp_tools_a: MCPTools) -> None:
        """Test successful task deletion."""
        task_result = await mcp_tools_a.add_task(title="Task to delete")
        task_id = task_result["task_id"]

        result = await mcp_tools_a.delete_task(task_id)

        assert result["status"] == "success"
        assert result["task_id"] == task_id

        # Verify task is gone
        tasks = await mcp_tools_a.list_tasks()
        assert len(tasks["tasks"]) == 0

    async def test_delete_task_not_found(self, mcp_tools_a: MCPTools) -> None:
        """Test deleting non-existent task."""
        fake_id = str(uuid4())
        with pytest.raises(MCPToolError) as exc_info:
            await mcp_tools_a.delete_task(fake_id)

        assert exc_info.value.code == "task_not_found"

    async def test_delete_task_user_isolation(
        self, mcp_tools_a: MCPTools, mcp_tools_b: MCPTools
    ) -> None:
        """Test that user A cannot delete user B's task."""
        task_result = await mcp_tools_a.add_task(title="User A's task")
        task_id = task_result["task_id"]

        with pytest.raises(MCPToolError) as exc_info:
            await mcp_tools_b.delete_task(task_id)

        assert exc_info.value.code == "task_not_found"

        # Verify task still exists for user A
        tasks = await mcp_tools_a.list_tasks()
        assert len(tasks["tasks"]) == 1


class TestUpdateTask:
    """Tests for update_task MCP tool."""

    async def test_update_task_title(self, mcp_tools_a: MCPTools) -> None:
        """Test updating task title."""
        task_result = await mcp_tools_a.add_task(title="Original title")
        task_id = task_result["task_id"]

        result = await mcp_tools_a.update_task(task_id, title="New title")

        assert result["status"] == "success"
        assert result["data"]["title"] == "New title"

    async def test_update_task_description(self, mcp_tools_a: MCPTools) -> None:
        """Test updating task description."""
        task_result = await mcp_tools_a.add_task(
            title="Task",
            description="Original description",
        )
        task_id = task_result["task_id"]

        result = await mcp_tools_a.update_task(task_id, description="New description")

        assert result["status"] == "success"
        assert result["data"]["description"] == "New description"

    async def test_update_task_both_fields(self, mcp_tools_a: MCPTools) -> None:
        """Test updating both title and description."""
        task_result = await mcp_tools_a.add_task(title="Original")
        task_id = task_result["task_id"]

        result = await mcp_tools_a.update_task(
            task_id,
            title="New title",
            description="New description",
        )

        assert result["status"] == "success"
        assert result["data"]["title"] == "New title"
        assert result["data"]["description"] == "New description"

    async def test_update_task_no_changes_fails(self, mcp_tools_a: MCPTools) -> None:
        """Test that update without changes fails."""
        task_result = await mcp_tools_a.add_task(title="Task")
        task_id = task_result["task_id"]

        with pytest.raises(MCPToolError) as exc_info:
            await mcp_tools_a.update_task(task_id)

        assert exc_info.value.code == "no_updates"

    async def test_update_task_not_found(self, mcp_tools_a: MCPTools) -> None:
        """Test updating non-existent task."""
        fake_id = str(uuid4())
        with pytest.raises(MCPToolError) as exc_info:
            await mcp_tools_a.update_task(fake_id, title="New title")

        assert exc_info.value.code == "task_not_found"

    async def test_update_task_user_isolation(
        self, mcp_tools_a: MCPTools, mcp_tools_b: MCPTools
    ) -> None:
        """Test that user A cannot update user B's task."""
        task_result = await mcp_tools_a.add_task(title="User A's task")
        task_id = task_result["task_id"]

        with pytest.raises(MCPToolError) as exc_info:
            await mcp_tools_b.update_task(task_id, title="Hacked!")

        assert exc_info.value.code == "task_not_found"

        # Verify task is unchanged
        tasks = await mcp_tools_a.list_tasks()
        assert tasks["tasks"][0]["title"] == "User A's task"

    async def test_update_task_empty_title_fails(self, mcp_tools_a: MCPTools) -> None:
        """Test that empty title update fails."""
        task_result = await mcp_tools_a.add_task(title="Task")
        task_id = task_result["task_id"]

        with pytest.raises(MCPToolError) as exc_info:
            await mcp_tools_a.update_task(task_id, title="")

        assert exc_info.value.code == "invalid_title"


class TestUncompleteTask:
    """Tests for uncomplete_task MCP tool."""

    async def test_uncomplete_task_success(self, mcp_tools_a: MCPTools) -> None:
        """Test successful task uncomplete."""
        task_result = await mcp_tools_a.add_task(title="Task")
        task_id = task_result["task_id"]

        await mcp_tools_a.complete_task(task_id)
        result = await mcp_tools_a.uncomplete_task(task_id)

        assert result["status"] == "success"
        assert result["data"]["completed"] is False

    async def test_uncomplete_task_not_found(self, mcp_tools_a: MCPTools) -> None:
        """Test uncompleting non-existent task."""
        fake_id = str(uuid4())
        with pytest.raises(MCPToolError) as exc_info:
            await mcp_tools_a.uncomplete_task(fake_id)

        assert exc_info.value.code == "task_not_found"

    async def test_uncomplete_task_user_isolation(
        self, mcp_tools_a: MCPTools, mcp_tools_b: MCPTools
    ) -> None:
        """Test that user A cannot uncomplete user B's task."""
        task_result = await mcp_tools_a.add_task(title="User A's task")
        task_id = task_result["task_id"]
        await mcp_tools_a.complete_task(task_id)

        with pytest.raises(MCPToolError) as exc_info:
            await mcp_tools_b.uncomplete_task(task_id)

        assert exc_info.value.code == "task_not_found"


class TestTaskEnhancements:
    """Tests for task enhancement fields: due_date, priority, category."""

    async def test_add_task_with_all_enhancements(self, mcp_tools_a: MCPTools) -> None:
        """Test creating task with due_date, priority, and category."""
        due_date = (datetime.utcnow() + timedelta(days=7)).isoformat()

        result = await mcp_tools_a.add_task(
            title="Enhanced task",
            due_date=due_date,
            priority="high",
            category="work"
        )

        assert result["status"] == "success"
        assert result["data"]["priority"] == "high"
        assert result["data"]["category"] == "work"
        assert result["data"]["due_date"] is not None

    async def test_add_task_invalid_priority_fails(self, mcp_tools_a: MCPTools) -> None:
        """Test that invalid priority raises error."""
        with pytest.raises(MCPToolError) as exc_info:
            await mcp_tools_a.add_task(title="Task", priority="invalid")

        assert exc_info.value.code == "invalid_priority"

    async def test_add_task_invalid_due_date_fails(self, mcp_tools_a: MCPTools) -> None:
        """Test that invalid due date raises error."""
        with pytest.raises(MCPToolError) as exc_info:
            await mcp_tools_a.add_task(title="Task", due_date="not-a-date")

        assert exc_info.value.code == "invalid_due_date"

    async def test_add_task_category_too_long_fails(self, mcp_tools_a: MCPTools) -> None:
        """Test that category exceeding 50 chars raises error."""
        with pytest.raises(MCPToolError) as exc_info:
            await mcp_tools_a.add_task(title="Task", category="x" * 51)

        assert exc_info.value.code == "invalid_category"

    async def test_list_tasks_filter_by_priority(self, mcp_tools_a: MCPTools) -> None:
        """Test filtering tasks by priority."""
        await mcp_tools_a.add_task(title="Urgent task", priority="urgent")
        await mcp_tools_a.add_task(title="Low task", priority="low")

        result = await mcp_tools_a.list_tasks(priority="urgent")

        assert len(result["tasks"]) == 1
        assert result["tasks"][0]["title"] == "Urgent task"

    async def test_list_tasks_filter_by_category(self, mcp_tools_a: MCPTools) -> None:
        """Test filtering tasks by category."""
        await mcp_tools_a.add_task(title="Work task", category="work")
        await mcp_tools_a.add_task(title="Personal task", category="personal")

        result = await mcp_tools_a.list_tasks(category="work")

        assert len(result["tasks"]) == 1
        assert result["tasks"][0]["title"] == "Work task"

    async def test_list_tasks_filter_overdue(self, mcp_tools_a: MCPTools) -> None:
        """Test filtering overdue tasks."""
        past = (datetime.utcnow() - timedelta(days=1)).isoformat()
        future = (datetime.utcnow() + timedelta(days=1)).isoformat()

        await mcp_tools_a.add_task(title="Overdue task", due_date=past)
        await mcp_tools_a.add_task(title="Future task", due_date=future)

        result = await mcp_tools_a.list_tasks(overdue=True)

        assert len(result["tasks"]) == 1
        assert result["tasks"][0]["title"] == "Overdue task"

    async def test_list_tasks_sort_by_due_date(self, mcp_tools_a: MCPTools) -> None:
        """Test sorting tasks by due date."""
        later = (datetime.utcnow() + timedelta(days=7)).isoformat()
        sooner = (datetime.utcnow() + timedelta(days=1)).isoformat()

        await mcp_tools_a.add_task(title="Later task", due_date=later)
        await mcp_tools_a.add_task(title="Sooner task", due_date=sooner)

        result = await mcp_tools_a.list_tasks(sort_by="due_date")

        assert len(result["tasks"]) == 2
        # Default sort order is desc, but due_date sorting uses nullslast
        # The sooner task should come after later in desc order

    async def test_update_task_enhancements(self, mcp_tools_a: MCPTools) -> None:
        """Test updating task enhancement fields."""
        task_result = await mcp_tools_a.add_task(title="Task to update")
        task_id = task_result["task_id"]

        due_date = (datetime.utcnow() + timedelta(days=3)).isoformat()
        result = await mcp_tools_a.update_task(
            task_id=task_id,
            priority="urgent",
            category="personal",
            due_date=due_date
        )

        assert result["status"] == "success"
        assert result["data"]["priority"] == "urgent"
        assert result["data"]["category"] == "personal"
        assert result["data"]["due_date"] is not None

    async def test_update_task_clear_enhancements(self, mcp_tools_a: MCPTools) -> None:
        """Test clearing task enhancement fields."""
        due_date = (datetime.utcnow() + timedelta(days=1)).isoformat()
        task_result = await mcp_tools_a.add_task(
            title="Task with enhancements",
            due_date=due_date,
            priority="high",
            category="work"
        )
        task_id = task_result["task_id"]

        result = await mcp_tools_a.update_task(
            task_id=task_id,
            clear_due_date=True,
            clear_priority=True,
            clear_category=True
        )

        assert result["status"] == "success"
        assert result["data"]["due_date"] is None
        assert result["data"]["priority"] is None
        assert result["data"]["category"] is None

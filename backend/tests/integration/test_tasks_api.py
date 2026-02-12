"""Integration tests for tasks API endpoints."""

from datetime import datetime, timedelta
from uuid import uuid4

import pytest


class TestCreateTaskEndpoint:
    """Tests for POST /api/v1/tasks."""

    @pytest.mark.asyncio
    async def test_create_task_success(self, client, auth_headers):
        """Successful task creation returns task data."""
        response = await client.post(
            "/api/v1/tasks",
            json={"title": "Test Task", "description": "Test description"},
            headers=auth_headers
        )

        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Test Task"
        assert data["description"] == "Test description"
        assert data["completed"] is False
        assert "id" in data

    @pytest.mark.asyncio
    async def test_create_task_without_description(self, client, auth_headers):
        """Task creation without description succeeds."""
        response = await client.post(
            "/api/v1/tasks",
            json={"title": "Test Task"},
            headers=auth_headers
        )

        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Test Task"
        assert data["description"] is None

    @pytest.mark.asyncio
    async def test_create_task_unauthenticated(self, client):
        """Unauthenticated task creation returns 401."""
        response = await client.post(
            "/api/v1/tasks",
            json={"title": "Test Task"}
        )

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_create_task_empty_title(self, client, auth_headers):
        """Task with empty title returns 422."""
        response = await client.post(
            "/api/v1/tasks",
            json={"title": ""},
            headers=auth_headers
        )

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_create_task_title_too_long(self, client, auth_headers):
        """Task with title over 200 chars returns 422."""
        response = await client.post(
            "/api/v1/tasks",
            json={"title": "x" * 201},
            headers=auth_headers
        )

        assert response.status_code == 422


class TestListTasksEndpoint:
    """Tests for GET /api/v1/tasks."""

    @pytest.mark.asyncio
    async def test_list_tasks_empty(self, client, auth_headers):
        """List tasks returns empty array for new user."""
        response = await client.get("/api/v1/tasks", headers=auth_headers)

        assert response.status_code == 200
        assert response.json() == []

    @pytest.mark.asyncio
    async def test_list_tasks_returns_user_tasks(self, client, auth_headers):
        """List tasks returns all tasks for authenticated user."""
        # Create tasks
        await client.post(
            "/api/v1/tasks",
            json={"title": "Task 1"},
            headers=auth_headers
        )
        await client.post(
            "/api/v1/tasks",
            json={"title": "Task 2"},
            headers=auth_headers
        )

        response = await client.get("/api/v1/tasks", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        titles = [t["title"] for t in data]
        assert "Task 1" in titles
        assert "Task 2" in titles

    @pytest.mark.asyncio
    async def test_list_tasks_unauthenticated(self, client):
        """Unauthenticated list request returns 401."""
        response = await client.get("/api/v1/tasks")

        assert response.status_code == 401


class TestGetTaskEndpoint:
    """Tests for GET /api/v1/tasks/{task_id}."""

    @pytest.mark.asyncio
    async def test_get_task_success(self, client, auth_headers):
        """Get task returns task data."""
        # Create a task
        create_response = await client.post(
            "/api/v1/tasks",
            json={"title": "Test Task"},
            headers=auth_headers
        )
        task_id = create_response.json()["id"]

        response = await client.get(f"/api/v1/tasks/{task_id}", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Test Task"

    @pytest.mark.asyncio
    async def test_get_task_not_found(self, client, auth_headers):
        """Get non-existent task returns 404."""
        response = await client.get(
            f"/api/v1/tasks/{uuid4()}",
            headers=auth_headers
        )

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_get_task_unauthenticated(self, client):
        """Unauthenticated get request returns 401."""
        response = await client.get(f"/api/v1/tasks/{uuid4()}")

        assert response.status_code == 401


class TestToggleTaskEndpoint:
    """Tests for PATCH /api/v1/tasks/{task_id}/toggle."""

    @pytest.mark.asyncio
    async def test_toggle_task_to_complete(self, client, auth_headers):
        """Toggle incomplete task to complete."""
        # Create a task
        create_response = await client.post(
            "/api/v1/tasks",
            json={"title": "Test Task"},
            headers=auth_headers
        )
        task_id = create_response.json()["id"]
        assert create_response.json()["completed"] is False

        # Toggle to complete
        response = await client.patch(
            f"/api/v1/tasks/{task_id}/toggle",
            headers=auth_headers
        )

        assert response.status_code == 200
        assert response.json()["completed"] is True

    @pytest.mark.asyncio
    async def test_toggle_task_to_incomplete(self, client, auth_headers):
        """Toggle complete task back to incomplete."""
        # Create and complete a task
        create_response = await client.post(
            "/api/v1/tasks",
            json={"title": "Test Task"},
            headers=auth_headers
        )
        task_id = create_response.json()["id"]

        # Toggle to complete
        await client.patch(f"/api/v1/tasks/{task_id}/toggle", headers=auth_headers)

        # Toggle back to incomplete
        response = await client.patch(
            f"/api/v1/tasks/{task_id}/toggle",
            headers=auth_headers
        )

        assert response.status_code == 200
        assert response.json()["completed"] is False

    @pytest.mark.asyncio
    async def test_toggle_task_not_found(self, client, auth_headers):
        """Toggle non-existent task returns 404."""
        response = await client.patch(
            f"/api/v1/tasks/{uuid4()}/toggle",
            headers=auth_headers
        )

        assert response.status_code == 404


class TestUpdateTaskEndpoint:
    """Tests for PUT /api/v1/tasks/{task_id}."""

    @pytest.mark.asyncio
    async def test_update_task_title(self, client, auth_headers):
        """Update task title successfully."""
        # Create a task
        create_response = await client.post(
            "/api/v1/tasks",
            json={"title": "Original Title"},
            headers=auth_headers
        )
        task_id = create_response.json()["id"]

        # Update title
        response = await client.put(
            f"/api/v1/tasks/{task_id}",
            json={"title": "Updated Title"},
            headers=auth_headers
        )

        assert response.status_code == 200
        assert response.json()["title"] == "Updated Title"

    @pytest.mark.asyncio
    async def test_update_task_description(self, client, auth_headers):
        """Update task description successfully."""
        # Create a task
        create_response = await client.post(
            "/api/v1/tasks",
            json={"title": "Test Task"},
            headers=auth_headers
        )
        task_id = create_response.json()["id"]

        # Update description
        response = await client.put(
            f"/api/v1/tasks/{task_id}",
            json={"description": "New description"},
            headers=auth_headers
        )

        assert response.status_code == 200
        assert response.json()["description"] == "New description"

    @pytest.mark.asyncio
    async def test_update_task_not_found(self, client, auth_headers):
        """Update non-existent task returns 404."""
        response = await client.put(
            f"/api/v1/tasks/{uuid4()}",
            json={"title": "Updated"},
            headers=auth_headers
        )

        assert response.status_code == 404


class TestDeleteTaskEndpoint:
    """Tests for DELETE /api/v1/tasks/{task_id}."""

    @pytest.mark.asyncio
    async def test_delete_task_success(self, client, auth_headers):
        """Delete task successfully."""
        # Create a task
        create_response = await client.post(
            "/api/v1/tasks",
            json={"title": "Test Task"},
            headers=auth_headers
        )
        task_id = create_response.json()["id"]

        # Delete the task
        response = await client.delete(
            f"/api/v1/tasks/{task_id}",
            headers=auth_headers
        )

        assert response.status_code == 204

        # Verify task is deleted
        get_response = await client.get(
            f"/api/v1/tasks/{task_id}",
            headers=auth_headers
        )
        assert get_response.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_task_not_found(self, client, auth_headers):
        """Delete non-existent task returns 404."""
        response = await client.delete(
            f"/api/v1/tasks/{uuid4()}",
            headers=auth_headers
        )

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_task_unauthenticated(self, client):
        """Unauthenticated delete request returns 401."""
        response = await client.delete(f"/api/v1/tasks/{uuid4()}")

        assert response.status_code == 401


class TestTaskEnhancementsEndpoint:
    """Tests for task enhancement fields via API."""

    @pytest.mark.asyncio
    async def test_create_task_with_enhancements(self, client, auth_headers):
        """Create task with due_date, priority, and category."""
        due_date = (datetime.utcnow() + timedelta(days=7)).isoformat()
        response = await client.post(
            "/api/v1/tasks",
            json={
                "title": "Enhanced Task",
                "due_date": due_date,
                "priority": "high",
                "category": "work"
            },
            headers=auth_headers
        )

        assert response.status_code == 201
        data = response.json()
        assert data["priority"] == "high"
        assert data["category"] == "work"
        assert data["due_date"] is not None

    @pytest.mark.asyncio
    async def test_create_task_without_enhancements(self, client, auth_headers):
        """Create task without enhancement fields (backward compatible)."""
        response = await client.post(
            "/api/v1/tasks",
            json={"title": "Basic Task"},
            headers=auth_headers
        )

        assert response.status_code == 201
        data = response.json()
        assert data["due_date"] is None
        assert data["priority"] is None
        assert data["category"] is None

    @pytest.mark.asyncio
    async def test_list_tasks_filter_by_category(self, client, auth_headers):
        """List tasks filtered by category."""
        await client.post(
            "/api/v1/tasks",
            json={"title": "Work Task", "category": "work"},
            headers=auth_headers
        )
        await client.post(
            "/api/v1/tasks",
            json={"title": "Personal Task", "category": "personal"},
            headers=auth_headers
        )

        response = await client.get(
            "/api/v1/tasks?category=work",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["title"] == "Work Task"

    @pytest.mark.asyncio
    async def test_list_tasks_filter_by_priority(self, client, auth_headers):
        """List tasks filtered by priority."""
        await client.post(
            "/api/v1/tasks",
            json={"title": "Urgent Task", "priority": "urgent"},
            headers=auth_headers
        )
        await client.post(
            "/api/v1/tasks",
            json={"title": "Low Task", "priority": "low"},
            headers=auth_headers
        )

        response = await client.get(
            "/api/v1/tasks?priority=urgent",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["title"] == "Urgent Task"

    @pytest.mark.asyncio
    async def test_list_tasks_sort_by_due_date(self, client, auth_headers):
        """List tasks sorted by due date."""
        later = (datetime.utcnow() + timedelta(days=7)).isoformat()
        sooner = (datetime.utcnow() + timedelta(days=1)).isoformat()

        await client.post(
            "/api/v1/tasks",
            json={"title": "Later Task", "due_date": later},
            headers=auth_headers
        )
        await client.post(
            "/api/v1/tasks",
            json={"title": "Sooner Task", "due_date": sooner},
            headers=auth_headers
        )

        response = await client.get(
            "/api/v1/tasks?sort=due_date&order=asc",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["title"] == "Sooner Task"
        assert data[1]["title"] == "Later Task"

    @pytest.mark.asyncio
    async def test_list_tasks_overdue_filter(self, client, auth_headers):
        """List only overdue tasks."""
        past = (datetime.utcnow() - timedelta(days=1)).isoformat()
        future = (datetime.utcnow() + timedelta(days=1)).isoformat()

        await client.post(
            "/api/v1/tasks",
            json={"title": "Overdue Task", "due_date": past},
            headers=auth_headers
        )
        await client.post(
            "/api/v1/tasks",
            json={"title": "Future Task", "due_date": future},
            headers=auth_headers
        )

        response = await client.get(
            "/api/v1/tasks?overdue=true",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["title"] == "Overdue Task"

    @pytest.mark.asyncio
    async def test_get_categories_endpoint(self, client, auth_headers):
        """Get user's distinct categories."""
        await client.post(
            "/api/v1/tasks",
            json={"title": "Task 1", "category": "work"},
            headers=auth_headers
        )
        await client.post(
            "/api/v1/tasks",
            json={"title": "Task 2", "category": "personal"},
            headers=auth_headers
        )
        await client.post(
            "/api/v1/tasks",
            json={"title": "Task 3", "category": "work"},  # duplicate
            headers=auth_headers
        )

        response = await client.get(
            "/api/v1/tasks/categories",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert "work" in data
        assert "personal" in data

    @pytest.mark.asyncio
    async def test_update_task_enhancements(self, client, auth_headers):
        """Update task enhancement fields."""
        create_response = await client.post(
            "/api/v1/tasks",
            json={"title": "Task to update"},
            headers=auth_headers
        )
        task_id = create_response.json()["id"]
        due_date = (datetime.utcnow() + timedelta(days=3)).isoformat()

        response = await client.put(
            f"/api/v1/tasks/{task_id}",
            json={
                "due_date": due_date,
                "priority": "urgent",
                "category": "personal"
            },
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["priority"] == "urgent"
        assert data["category"] == "personal"
        assert data["due_date"] is not None

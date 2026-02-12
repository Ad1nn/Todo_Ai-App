"""Tasks API routes."""

from typing import Literal
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, status

from src.api.deps import CurrentUser, DbSession
from pydantic import BaseModel

from src.events import publish_audit_event
from src.models.task import Priority, RecurrenceRule, Task, TaskCreate, TaskPublic, TaskUpdate
from src.services.task_service import TaskService


class CompleteTaskResponse(BaseModel):
    """Response for completing a task."""

    completed_task: TaskPublic
    next_occurrence: TaskPublic | None = None

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post("", response_model=TaskPublic, status_code=status.HTTP_201_CREATED)
async def create_task(task_data: TaskCreate, session: DbSession, current_user: CurrentUser) -> Task:
    """Create a new task."""
    task_service = TaskService(session)
    task = await task_service.create(
        user_id=current_user.id,
        title=task_data.title,
        description=task_data.description,
        due_date=task_data.due_date,
        priority=task_data.priority,
        category=task_data.category,
        recurrence_rule=task_data.recurrence_rule,
    )
    return task


@router.get("/categories", response_model=list[str])
async def list_categories(session: DbSession, current_user: CurrentUser) -> list[str]:
    """List all distinct categories for the current user's tasks."""
    task_service = TaskService(session)
    categories = await task_service.get_user_categories(current_user.id)
    return categories


@router.get("", response_model=list[TaskPublic])
async def list_tasks(
    session: DbSession,
    current_user: CurrentUser,
    category: str | None = Query(default=None, max_length=50),
    priority: Priority | None = Query(default=None),
    completed: bool | None = Query(default=None),
    overdue: bool | None = Query(default=None),
    sort: Literal["created_at", "due_date", "priority"] = Query(default="created_at"),
    order: Literal["asc", "desc"] = Query(default="desc"),
) -> list[Task]:
    """List all tasks for the current user with optional filters."""
    task_service = TaskService(session)
    tasks = await task_service.list_by_user_filtered(
        user_id=current_user.id,
        category=category,
        priority=priority,
        completed=completed,
        overdue_only=overdue or False,
        sort_by=sort,
        sort_order=order,
    )
    return tasks


@router.get("/{task_id}", response_model=TaskPublic)
async def get_task(task_id: UUID, session: DbSession, current_user: CurrentUser) -> Task:
    """Get a specific task by ID."""
    task_service = TaskService(session)
    task = await task_service.get_by_id(task_id, current_user.id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return task


@router.put("/{task_id}", response_model=TaskPublic)
async def update_task(
    task_id: UUID, task_data: TaskUpdate, session: DbSession, current_user: CurrentUser
) -> Task:
    """Update a task."""
    task_service = TaskService(session)
    task = await task_service.update(
        task_id=task_id,
        user_id=current_user.id,
        title=task_data.title,
        description=task_data.description,
        due_date=task_data.due_date,
        priority=task_data.priority,
        category=task_data.category,
        recurrence_rule=task_data.recurrence_rule,
    )
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return task


@router.patch("/{task_id}/toggle", response_model=TaskPublic)
async def toggle_task_complete(
    task_id: UUID, session: DbSession, current_user: CurrentUser
) -> Task:
    """Toggle task completion status."""
    task_service = TaskService(session)
    task = await task_service.toggle_complete(task_id, current_user.id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return task


@router.post("/{task_id}/complete", response_model=CompleteTaskResponse)
async def complete_task(
    task_id: UUID, session: DbSession, current_user: CurrentUser
) -> CompleteTaskResponse:
    """Complete a task and create next occurrence if recurring.

    For recurring tasks, this will:
    1. Mark the current task as completed
    2. Create a new task for the next occurrence
    3. Publish a task.completed audit event
    """
    task_service = TaskService(session)
    completed_task, next_task = await task_service.complete_recurring_task(
        task_id, current_user.id
    )

    if not completed_task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    # Publish audit event for task completion
    await publish_audit_event(
        user_id=current_user.id,
        entity_type="task",
        entity_id=task_id,
        action="complete",
        before_value={"completed": False},
        after_value={
            "completed": True,
            "next_occurrence_id": str(next_task.id) if next_task else None,
        },
    )

    return CompleteTaskResponse(
        completed_task=TaskPublic.model_validate(completed_task),
        next_occurrence=TaskPublic.model_validate(next_task) if next_task else None,
    )


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(task_id: UUID, session: DbSession, current_user: CurrentUser) -> None:
    """Delete a task."""
    task_service = TaskService(session)
    deleted = await task_service.delete(task_id, current_user.id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

# Quickstart: Task Enhancements Implementation

**Feature**: 005-task-enhancements
**Date**: 2026-02-04

## Overview

This guide provides step-by-step instructions for implementing due dates, priority levels, and categories for tasks.

## Prerequisites

- Backend running (Phase 2 complete)
- Frontend running (Phase 2 complete)
- AI agent working (Phase 3 complete)
- Database accessible (Neon PostgreSQL)

## Implementation Order

```
1. Database Migration (003_add_task_enhancements.py)
   ↓
2. Backend Model Updates (models/task.py)
   ↓
3. Repository Layer (repositories/task_repository.py)
   ↓
4. Service Layer (services/task_service.py)
   ↓
5. API Endpoints (api/tasks.py)
   ↓
6. MCP Tools (mcp/tools.py)
   ↓
7. Agent Prompts (agent/prompts.py)
   ↓
8. Frontend Types (lib/types.ts)
   ↓
9. Frontend Components (TaskItem, TaskForm, TaskList)
   ↓
10. useTasks Hook (hooks/useTasks.ts)
```

## Step 1: Database Migration

Create `backend/alembic/versions/003_add_task_enhancements.py`:

```python
"""Add task enhancements: due_date, priority, category

Revision ID: 003
Revises: 002
Create Date: 2026-02-04
"""
from alembic import op
import sqlalchemy as sa

revision = "003"
down_revision = "002"
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.add_column("task", sa.Column("due_date", sa.DateTime(), nullable=True))
    op.add_column("task", sa.Column("priority", sa.String(10), nullable=True))
    op.add_column("task", sa.Column("category", sa.String(50), nullable=True))

    op.create_index("ix_task_due_date", "task", ["due_date"])
    op.create_index("ix_task_priority", "task", ["priority"])
    op.create_index("ix_task_category", "task", ["category"])

def downgrade() -> None:
    op.drop_index("ix_task_category")
    op.drop_index("ix_task_priority")
    op.drop_index("ix_task_due_date")

    op.drop_column("task", "category")
    op.drop_column("task", "priority")
    op.drop_column("task", "due_date")
```

Run migration:
```bash
cd backend
alembic upgrade head
```

## Step 2: Backend Model Updates

Update `backend/src/models/task.py`:

```python
from enum import Enum

class Priority(str, Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"

class TaskBase(SQLModel):
    title: str = Field(min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=2000)
    due_date: datetime | None = Field(default=None)
    priority: Priority | None = Field(default=None)
    category: str | None = Field(default=None, max_length=50)
```

## Step 3: Repository Updates

Add to `backend/src/repositories/task_repository.py`:

```python
async def list_by_user_filtered(
    self,
    user_id: UUID,
    category: str | None = None,
    priority: Priority | None = None,
    completed: bool | None = None,
    overdue_only: bool = False,
) -> list[Task]:
    query = select(Task).where(Task.user_id == user_id)

    if category is not None:
        query = query.where(Task.category == category)
    if priority is not None:
        query = query.where(Task.priority == priority)
    if completed is not None:
        query = query.where(Task.completed == completed)
    if overdue_only:
        query = query.where(
            Task.due_date < datetime.utcnow(),
            Task.completed == False
        )

    query = query.order_by(Task.created_at.desc())
    result = await self.session.execute(query)
    return list(result.scalars().all())

async def get_user_categories(self, user_id: UUID) -> list[str]:
    query = (
        select(Task.category)
        .where(Task.user_id == user_id, Task.category.isnot(None))
        .distinct()
        .order_by(Task.category)
    )
    result = await self.session.execute(query)
    return [row[0] for row in result.all()]
```

## Step 4: Service Layer Updates

Update `backend/src/services/task_service.py`:

```python
async def create(
    self,
    user_id: UUID,
    title: str,
    description: str | None = None,
    due_date: datetime | None = None,
    priority: Priority | None = None,
    category: str | None = None,
) -> Task:
    return await self.task_repo.create(
        user_id=user_id,
        title=title,
        description=description,
        due_date=due_date,
        priority=priority,
        category=category,
    )
```

## Step 5: API Endpoint Updates

Update `backend/src/api/tasks.py`:

```python
@router.get("", response_model=list[TaskPublic])
async def list_tasks(
    session: DbSession,
    current_user: CurrentUser,
    category: str | None = None,
    priority: Priority | None = None,
    completed: bool | None = None,
    overdue: bool | None = None,
) -> list[Task]:
    task_service = TaskService(session)
    return await task_service.list_by_user_filtered(
        user_id=current_user.id,
        category=category,
        priority=priority,
        completed=completed,
        overdue_only=overdue or False,
    )

@router.get("/categories", response_model=list[str])
async def list_categories(
    session: DbSession,
    current_user: CurrentUser,
) -> list[str]:
    task_service = TaskService(session)
    return await task_service.get_user_categories(current_user.id)
```

## Step 6: MCP Tools Updates

Update `backend/src/mcp/tools.py`:

```python
async def add_task(
    self,
    title: str,
    description: str | None = None,
    due_date: str | None = None,
    priority: str | None = None,
    category: str | None = None,
) -> dict:
    # Parse due_date from ISO 8601 string
    parsed_due_date = None
    if due_date:
        parsed_due_date = datetime.fromisoformat(due_date.replace("Z", "+00:00"))

    # Parse priority
    parsed_priority = None
    if priority:
        parsed_priority = Priority(priority.lower())

    task = await self.task_service.create(
        user_id=self.user_id,
        title=title,
        description=description,
        due_date=parsed_due_date,
        priority=parsed_priority,
        category=category,
    )
    return {"task_id": str(task.id), "status": "success", "data": self._task_to_dict(task)}
```

## Step 7: Agent Prompt Updates

Update `backend/src/agent/prompts.py` with enhanced SYSTEM_PROMPT (see contracts/mcp-tools.md).

## Step 8: Frontend Types

Update `frontend/src/lib/types.ts`:

```typescript
export type Priority = 'low' | 'normal' | 'high' | 'urgent';

export interface Task {
  id: string;
  title: string;
  description: string | null;
  completed: boolean;
  created_at: string;
  updated_at: string;
  due_date: string | null;
  priority: Priority | null;
  category: string | null;
}
```

## Step 9: Frontend Components

### TaskForm.tsx
Add fields for due_date, priority, category.

### TaskItem.tsx
Display priority badge, due date indicator, category tag.

### TaskList.tsx
Add filter dropdowns for priority and category.

## Step 10: useTasks Hook

Update `frontend/src/hooks/useTasks.ts` to accept filters:

```typescript
export function useTasks(filters?: TaskFilters) {
  const queryString = filters ? buildTaskQueryString(filters) : '';
  const { data, mutate } = useSWR<Task[]>(`/api/v1/tasks${queryString}`, fetcher);
  // ...
}
```

## Verification Checklist

### Backend

- [ ] Migration runs successfully: `alembic upgrade head`
- [ ] Migration rollback works: `alembic downgrade -1`
- [ ] Create task with all fields via API
- [ ] Filter tasks by category, priority, overdue
- [ ] List user categories endpoint returns distinct values
- [ ] Existing tasks still accessible (backward compatibility)

### MCP/AI

- [ ] Add task via chat: "add urgent task test due tomorrow"
- [ ] List filtered tasks: "show my work tasks"
- [ ] List overdue tasks: "what's overdue?"
- [ ] Update priority: "change task X to high priority"

### Frontend

- [ ] TaskForm shows new fields
- [ ] TaskItem displays priority badge, due date, category
- [ ] Filter dropdowns work on TaskList
- [ ] Overdue tasks show red indicator
- [ ] Tasks due today show yellow indicator

## Test Commands

```bash
# Backend tests
cd backend && pytest tests/ -v

# Run specific test file
pytest tests/test_tasks.py -v

# Frontend tests
cd frontend && npm test

# E2E (if configured)
npm run test:e2e
```

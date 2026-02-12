# Data Model: Full-Stack Web Todo Application

**Feature**: 002-fullstack-web-app
**Date**: 2026-01-20
**Phase**: 1 - Design

## Entity Relationship Diagram

```
┌─────────────────────────────────────┐
│              User                    │
├─────────────────────────────────────┤
│ id: UUID (PK)                       │
│ email: VARCHAR(255) UNIQUE NOT NULL │
│ password_hash: VARCHAR(255) NOT NULL│
│ created_at: TIMESTAMP NOT NULL      │
│ updated_at: TIMESTAMP NOT NULL      │
└─────────────────────────────────────┘
                │
                │ 1:N
                ▼
┌─────────────────────────────────────┐
│              Task                    │
├─────────────────────────────────────┤
│ id: UUID (PK)                       │
│ user_id: UUID (FK → User.id)        │
│ title: VARCHAR(200) NOT NULL        │
│ description: TEXT (nullable)         │
│ completed: BOOLEAN DEFAULT FALSE    │
│ created_at: TIMESTAMP NOT NULL      │
│ updated_at: TIMESTAMP NOT NULL      │
└─────────────────────────────────────┘
```

## Entity Definitions

### User

Represents a registered user of the system.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK, auto-generated | Unique identifier |
| email | VARCHAR(255) | UNIQUE, NOT NULL | Login identifier |
| password_hash | VARCHAR(255) | NOT NULL | bcrypt hashed password |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Registration timestamp |
| updated_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Last modification |

**Indexes**:
- Primary key on `id`
- Unique index on `email` (for login lookups)

**Validation Rules**:
- Email must be valid format (RFC 5322)
- Email max length 255 characters
- Password minimum 8 characters (validated before hashing)

### Task

Represents a todo item belonging to a user.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK, auto-generated | Unique identifier |
| user_id | UUID | FK → User.id, NOT NULL | Owner reference |
| title | VARCHAR(200) | NOT NULL | Task title |
| description | TEXT | NULLABLE | Optional details |
| completed | BOOLEAN | NOT NULL, DEFAULT FALSE | Completion status |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Creation timestamp |
| updated_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Last modification |

**Indexes**:
- Primary key on `id`
- Index on `user_id` (for listing user's tasks)
- Composite index on `(user_id, completed)` (for filtered queries)

**Validation Rules**:
- Title required, max 200 characters
- Description max 2000 characters
- Completed must be boolean

**Foreign Key**:
- `user_id` → `User.id` with CASCADE DELETE (deleting user deletes their tasks)

## SQLModel Definitions

### User Model

```python
from datetime import datetime
from uuid import UUID, uuid4
from sqlmodel import SQLModel, Field

class UserBase(SQLModel):
    email: str = Field(max_length=255, index=True, unique=True)

class User(UserBase, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    password_hash: str = Field(max_length=255)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class UserCreate(UserBase):
    password: str = Field(min_length=8)

class UserPublic(UserBase):
    id: UUID
    created_at: datetime
```

### Task Model

```python
from datetime import datetime
from uuid import UUID, uuid4
from sqlmodel import SQLModel, Field

class TaskBase(SQLModel):
    title: str = Field(max_length=200)
    description: str | None = Field(default=None, max_length=2000)

class Task(TaskBase, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="user.id", index=True)
    completed: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class TaskCreate(TaskBase):
    pass

class TaskUpdate(SQLModel):
    title: str | None = Field(default=None, max_length=200)
    description: str | None = Field(default=None, max_length=2000)

class TaskPublic(TaskBase):
    id: UUID
    completed: bool
    created_at: datetime
    updated_at: datetime
```

## State Transitions

### Task Completion

```
[incomplete] ──toggle──► [complete]
     ▲                        │
     └────────toggle──────────┘
```

- Tasks start as `completed=False`
- Toggle operation flips the boolean
- No intermediate states

### User Lifecycle

```
[registered] ──login──► [authenticated]
      │                       │
      │                       ▼
      │               [session active]
      │                       │
      │                 logout/expire
      │                       │
      └───────────────────────┘
```

## Migration Script (Alembic)

### Initial Migration

```python
"""Initial schema

Revision ID: 001
Create Date: 2026-01-20
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

def upgrade() -> None:
    # User table
    op.create_table(
        'user',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('email', sa.String(255), nullable=False, unique=True),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_user_email', 'user', ['email'])

    # Task table
    op.create_table(
        'task',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', UUID(as_uuid=True), sa.ForeignKey('user.id', ondelete='CASCADE'), nullable=False),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('completed', sa.Boolean(), nullable=False, default=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_task_user_id', 'task', ['user_id'])
    op.create_index('ix_task_user_completed', 'task', ['user_id', 'completed'])

def downgrade() -> None:
    op.drop_table('task')
    op.drop_table('user')
```

## TypeScript Types (Frontend)

```typescript
// types.ts

export interface User {
  id: string;
  email: string;
  created_at: string;
}

export interface Task {
  id: string;
  title: string;
  description: string | null;
  completed: boolean;
  created_at: string;
  updated_at: string;
}

export interface TaskCreate {
  title: string;
  description?: string;
}

export interface TaskUpdate {
  title?: string;
  description?: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface ApiError {
  detail: string;
  code?: string;
  field?: string;
}
```

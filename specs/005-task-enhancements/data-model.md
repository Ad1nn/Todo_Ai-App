# Data Model: Task Enhancements

**Feature**: 005-task-enhancements
**Date**: 2026-02-04
**Status**: Draft

## Entity Changes

### Task (Enhanced)

**Table**: `task` (existing)

| Column | Type | Nullable | Default | Index | Notes |
|--------|------|----------|---------|-------|-------|
| id | UUID | No | uuid4() | PK | Existing |
| user_id | UUID | No | - | Yes (FK) | Existing |
| title | VARCHAR(200) | No | - | - | Existing |
| description | VARCHAR(2000) | Yes | NULL | - | Existing |
| completed | BOOLEAN | No | FALSE | - | Existing |
| created_at | TIMESTAMP | No | now() | - | Existing |
| updated_at | TIMESTAMP | No | now() | - | Existing |
| **due_date** | TIMESTAMP | Yes | NULL | Yes | **NEW** |
| **priority** | VARCHAR(10) | Yes | NULL | Yes | **NEW** |
| **category** | VARCHAR(50) | Yes | NULL | Yes | **NEW** |

### Priority Enum

**Python StrEnum** (not a database table):

```python
class Priority(str, Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"
```

**Sort Order** (for queries):
1. `urgent` (highest)
2. `high`
3. `normal`
4. `low`
5. `NULL` (lowest/last)

### Category

**No separate entity** - stored as free-text on Task.

**Suggested Values** (hard-coded in UI):
- work
- personal
- shopping
- health
- finance

## SQLModel Schema Changes

### TaskBase (Updated)

```python
class TaskBase(SQLModel):
    title: str = Field(min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=2000)
    due_date: datetime | None = Field(default=None)
    priority: Priority | None = Field(default=None)
    category: str | None = Field(default=None, max_length=50)
```

### Task (Updated)

```python
class Task(TaskBase, table=True):
    __tablename__ = "task"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="user.id", index=True)
    completed: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    # Inherited: due_date, priority, category from TaskBase
```

### TaskCreate (Updated)

```python
class TaskCreate(SQLModel):
    title: str = Field(min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=2000)
    due_date: datetime | None = Field(default=None)
    priority: Priority | None = Field(default=None)
    category: str | None = Field(default=None, max_length=50)
```

### TaskUpdate (Updated)

```python
class TaskUpdate(SQLModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=2000)
    due_date: datetime | None = Field(default=None)
    priority: Priority | None = Field(default=None)
    category: str | None = Field(default=None, max_length=50)
```

### TaskPublic (Updated)

```python
class TaskPublic(SQLModel):
    id: UUID
    title: str
    description: str | None
    completed: bool
    created_at: datetime
    updated_at: datetime
    due_date: datetime | None
    priority: Priority | None
    category: str | None
```

## Database Migration

**Migration**: `003_add_task_enhancements.py`

### Upgrade

```sql
-- Add new columns
ALTER TABLE task ADD COLUMN due_date TIMESTAMP NULL;
ALTER TABLE task ADD COLUMN priority VARCHAR(10) NULL;
ALTER TABLE task ADD COLUMN category VARCHAR(50) NULL;

-- Add indexes for query performance
CREATE INDEX ix_task_due_date ON task(due_date);
CREATE INDEX ix_task_priority ON task(priority);
CREATE INDEX ix_task_category ON task(category);
```

### Downgrade

```sql
-- Remove indexes
DROP INDEX IF EXISTS ix_task_category;
DROP INDEX IF EXISTS ix_task_priority;
DROP INDEX IF EXISTS ix_task_due_date;

-- Remove columns
ALTER TABLE task DROP COLUMN category;
ALTER TABLE task DROP COLUMN priority;
ALTER TABLE task DROP COLUMN due_date;
```

## Validation Rules

### Due Date
- Must be valid ISO 8601 datetime if provided
- No restriction on past dates (user may log completed work)
- Stored as UTC in database
- Frontend converts to local time for display

### Priority
- Must be one of: `low`, `normal`, `high`, `urgent`
- Case-insensitive on input, stored lowercase
- NULL allowed (no priority set)

### Category
- Maximum 50 characters
- Any non-empty string allowed
- Case-sensitive storage
- NULL allowed (no category set)
- Whitespace trimmed on save

## Query Patterns

### List with Filters

```python
# Repository method signature
async def list_by_user_filtered(
    user_id: UUID,
    category: str | None = None,
    priority: Priority | None = None,
    completed: bool | None = None,
    overdue_only: bool = False,
    sort_by: Literal["created_at", "due_date", "priority"] = "created_at",
    sort_order: Literal["asc", "desc"] = "desc"
) -> list[Task]
```

### Get User Categories

```python
# Repository method - returns distinct categories for user
async def get_user_categories(user_id: UUID) -> list[str]
```

**SQL**:
```sql
SELECT DISTINCT category
FROM task
WHERE user_id = :user_id AND category IS NOT NULL
ORDER BY category;
```

### Overdue Tasks Query

```python
# Find tasks where due_date < now AND completed = false
```

**SQL**:
```sql
SELECT * FROM task
WHERE user_id = :user_id
  AND due_date < NOW()
  AND completed = FALSE
ORDER BY due_date ASC;
```

## State Transitions

### Task Completion with Due Date

```
[incomplete, overdue] → complete() → [completed]
                                      (due_date preserved but not shown as overdue)
```

### Priority Changes

```
[any priority] → update(priority=new) → [new priority]
                                         (no side effects)
```

### Category Changes

```
[any category] → update(category=new) → [new category]
                                         (no side effects, no cascade)
```

## Backward Compatibility

| Scenario | Behavior |
|----------|----------|
| Existing tasks | due_date=NULL, priority=NULL, category=NULL |
| API call without new fields | New fields default to NULL |
| Frontend without new fields | Displays task normally, new fields hidden |
| AI creates task without metadata | Task created with NULL for new fields |

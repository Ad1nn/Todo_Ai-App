# Data Model: In-Memory Console Todo App

**Feature**: 001-console-todo-app | **Date**: 2026-01-18 | **Phase**: 1

## Entities

### Task

The core entity representing a todo item.

**Source**: Spec.md Key Entities section

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | `int` | Unique, auto-generated, > 0 | Unique identifier for the task |
| `title` | `str` | Non-empty, required | Brief description of the task |
| `description` | `str` | Optional (empty string default) | Detailed description |
| `completed` | `bool` | Default: `False` | Completion status |

**Python Implementation**:

```python
from dataclasses import dataclass, field

@dataclass
class Task:
    """Represents a todo item with title, description, and completion status."""

    id: int
    title: str
    description: str = ""
    completed: bool = False

    def __post_init__(self) -> None:
        """Validate task fields after initialization."""
        if not self.title or not self.title.strip():
            raise ValueError("Task title cannot be empty")
        self.title = self.title.strip()
        self.description = self.description.strip() if self.description else ""
```

**Validation Rules**:
- `id`: Must be positive integer (enforced by storage layer)
- `title`: Must be non-empty after stripping whitespace
- `description`: Stripped of leading/trailing whitespace; empty string if None
- `completed`: Boolean, defaults to False for new tasks

---

## State Transitions

### Task Completion Status

```
                    toggle_complete()
                    ┌─────────────┐
                    │             │
                    ▼             │
    ┌──────────┐         ┌───────┴────┐
    │Incomplete│ ◄─────► │  Complete  │
    └──────────┘         └────────────┘
         │                     │
         │  toggle_complete()  │
         └─────────────────────┘
```

**States**:
- `Incomplete`: `completed = False` (default for new tasks)
- `Complete`: `completed = True`

**Transitions**:
- `toggle_complete()`: Flips between Incomplete ↔ Complete

---

## Storage Schema

### MemoryStore

In-memory storage using Python dict.

**Structure**:
```python
class MemoryStore:
    _tasks: dict[int, Task]  # Key: task_id, Value: Task instance
    _next_id: int            # Counter for auto-generating IDs
```

**Invariants**:
- All task IDs in `_tasks` are unique
- `_next_id` is always greater than any existing task ID
- Deleted task IDs are never reused within a session

**Operations Complexity**:

| Operation | Complexity | Notes |
|-----------|------------|-------|
| `add(task)` | O(1) | Dict insertion |
| `get(id)` | O(1) | Dict lookup |
| `get_all()` | O(n) | Dict values iteration |
| `update(task)` | O(1) | Dict update |
| `delete(id)` | O(1) | Dict deletion |
| `next_id()` | O(1) | Counter increment |

---

## Relationships

```
┌─────────────┐         ┌─────────────┐
│ MemoryStore │ ──1:N── │    Task     │
└─────────────┘         └─────────────┘
      │                       │
      │ stores                │ instance of
      ▼                       ▼
  dict[int, Task]         dataclass
```

- **MemoryStore → Task**: One-to-many (store contains multiple tasks)
- No relationships between Task entities in Phase 1

---

## Example Data

### Sample Tasks

```python
tasks = {
    1: Task(id=1, title="Buy groceries", description="Milk, eggs, bread", completed=False),
    2: Task(id=2, title="Call mom", description="", completed=True),
    3: Task(id=3, title="Finish project", description="Complete Phase 1 implementation", completed=False),
}
```

### Display Format (CLI output)

```
ID  | Status | Title           | Description
----|--------|-----------------|---------------------------
1   | [ ]    | Buy groceries   | Milk, eggs, bread
2   | [x]    | Call mom        |
3   | [ ]    | Finish project  | Complete Phase 1 implementation
```

**Status Indicators**:
- `[ ]` = Incomplete
- `[x]` = Complete

---

## Migration Notes

### Phase 2 Considerations

When adding database persistence in Phase 2:

1. **Schema Translation**:
   ```sql
   CREATE TABLE tasks (
       id INTEGER PRIMARY KEY AUTOINCREMENT,
       title TEXT NOT NULL,
       description TEXT DEFAULT '',
       completed BOOLEAN DEFAULT FALSE
   );
   ```

2. **Storage Interface**: The `MemoryStore` interface is designed to be database-agnostic. A `DatabaseStore` can implement the same interface.

3. **ID Generation**: Database will handle auto-increment; `next_id()` method becomes unnecessary.

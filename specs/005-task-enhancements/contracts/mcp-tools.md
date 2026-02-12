# MCP Tools Contract: Task Enhancements

**Feature**: 005-task-enhancements
**Date**: 2026-02-04

## Tool Definitions

### add_task (Enhanced)

**Description**: Create a new task with optional due date, priority, and category.

**Parameters**:
| Name | Type | Required | Description |
|------|------|----------|-------------|
| title | string | Yes | Task title (1-200 chars) |
| description | string | No | Task description (max 2000 chars) |
| due_date | string | No | ISO 8601 datetime (e.g., "2026-02-05T17:00:00Z") |
| priority | string | No | One of: low, normal, high, urgent |
| category | string | No | Category label (max 50 chars) |

**Response**:
```json
{
  "task_id": "uuid-string",
  "status": "success",
  "data": {
    "id": "uuid-string",
    "title": "Task title",
    "description": "Optional description",
    "completed": false,
    "created_at": "2026-02-04T10:00:00Z",
    "updated_at": "2026-02-04T10:00:00Z",
    "due_date": "2026-02-05T17:00:00Z",
    "priority": "high",
    "category": "work"
  }
}
```

**Error Codes**:
- `invalid_title`: Title is empty or exceeds 200 characters
- `invalid_priority`: Priority is not one of the allowed values
- `invalid_due_date`: Due date is not valid ISO 8601 format

---

### list_tasks (Enhanced)

**Description**: List tasks with optional filters for completion, priority, category, and overdue status.

**Parameters**:
| Name | Type | Required | Description |
|------|------|----------|-------------|
| completed | boolean | No | Filter by completion status |
| priority | string | No | Filter by priority level |
| category | string | No | Filter by category (exact match) |
| overdue | boolean | No | If true, show only overdue tasks |

**Response**:
```json
{
  "status": "success",
  "data": [
    {
      "id": "uuid-1",
      "title": "Task 1",
      "description": null,
      "completed": false,
      "created_at": "2026-02-04T10:00:00Z",
      "updated_at": "2026-02-04T10:00:00Z",
      "due_date": "2026-02-03T17:00:00Z",
      "priority": "urgent",
      "category": "work"
    }
  ],
  "count": 1
}
```

---

### update_task (Enhanced)

**Description**: Update a task's title, description, due date, priority, or category.

**Parameters**:
| Name | Type | Required | Description |
|------|------|----------|-------------|
| task_id | string | Yes | Task UUID |
| title | string | No | New title (1-200 chars) |
| description | string | No | New description |
| due_date | string | No | New due date (ISO 8601) or "clear" to remove |
| priority | string | No | New priority or "clear" to remove |
| category | string | No | New category or "clear" to remove |

**Response**:
```json
{
  "task_id": "uuid-string",
  "status": "success",
  "data": {
    "id": "uuid-string",
    "title": "Updated title",
    "description": "Updated description",
    "completed": false,
    "created_at": "2026-02-04T10:00:00Z",
    "updated_at": "2026-02-04T11:00:00Z",
    "due_date": "2026-02-06T09:00:00Z",
    "priority": "normal",
    "category": "personal"
  }
}
```

**Error Codes**:
- `task_not_found`: Task does not exist or user lacks access
- `invalid_task_id`: Task ID is not a valid UUID
- `no_updates`: No fields provided to update
- `invalid_priority`: Invalid priority value
- `invalid_due_date`: Invalid date format

**Special Values**:
- Pass `"clear"` for due_date, priority, or category to set to NULL

---

### complete_task (Unchanged)

**Description**: Mark a task as completed.

**Parameters**:
| Name | Type | Required | Description |
|------|------|----------|-------------|
| task_id | string | Yes | Task UUID |

**Response**: Same as update_task with `completed: true`

---

### uncomplete_task (Unchanged)

**Description**: Mark a task as not completed.

**Parameters**:
| Name | Type | Required | Description |
|------|------|----------|-------------|
| task_id | string | Yes | Task UUID |

**Response**: Same as update_task with `completed: false`

---

### delete_task (Unchanged)

**Description**: Permanently delete a task.

**Parameters**:
| Name | Type | Required | Description |
|------|------|----------|-------------|
| task_id | string | Yes | Task UUID |

**Response**:
```json
{
  "task_id": "uuid-string",
  "status": "success",
  "message": "Task deleted successfully"
}
```

---

## Agent Prompt Additions

### System Prompt Extension

Add to SYSTEM_PROMPT after existing tool descriptions:

```
## Enhanced Task Features

You can now create and manage tasks with:
- **Due dates**: Set deadlines for tasks
- **Priority levels**: low, normal, high, urgent
- **Categories**: Organize tasks by area (work, personal, shopping, health, finance, or custom)

### Interpreting User Intent

**Date expressions** (interpret relative to today):
- "tomorrow" → tomorrow's date, 9:00 AM
- "next Monday" → next Monday, 9:00 AM
- "in 3 days" → 3 days from now, 9:00 AM
- "Friday at 5pm" → this Friday, 5:00 PM
- "end of week" → this Friday, 5:00 PM

**Priority keywords**:
- urgent, asap, immediately, critical → priority: urgent
- important, soon, pressing → priority: high
- normal, regular (or no priority mentioned) → priority: normal
- low, whenever, no rush, eventually → priority: low

**Category inference**:
- meeting, project, deadline, work, office → category: work
- grocery, shopping, buy, store → category: shopping
- doctor, gym, health, workout, medicine → category: health
- bills, payment, budget, money, bank → category: finance
- Other tasks → category: personal

### Example Interactions

User: "add task buy groceries due tomorrow"
→ add_task(title="buy groceries", due_date="2026-02-05T09:00:00Z", category="shopping")

User: "add urgent task fix production bug"
→ add_task(title="fix production bug", priority="urgent", category="work")

User: "show my overdue tasks"
→ list_tasks(overdue=true)

User: "what high priority work tasks do I have?"
→ list_tasks(priority="high", category="work")

User: "change the priority of task X to low"
→ update_task(task_id="X", priority="low")

User: "remove the due date from task Y"
→ update_task(task_id="Y", due_date="clear")
```

### Tool Descriptions Update

```python
TOOL_DESCRIPTIONS = {
    "add_task": "Create a new task. Optionally set due_date (ISO 8601), priority (low/normal/high/urgent), and category.",
    "list_tasks": "List tasks. Filter by completed (bool), priority, category, or overdue (bool).",
    "update_task": "Update a task's title, description, due_date, priority, or category. Use 'clear' to remove optional fields.",
    "complete_task": "Mark a task as completed.",
    "uncomplete_task": "Mark a task as not completed.",
    "delete_task": "Permanently delete a task.",
}
```

# Data Model: Advanced Cloud Deployment

**Feature**: 007-advanced-cloud-deployment
**Date**: 2026-02-09

## Entity Overview

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│      Task       │────▶│   Notification  │     │   AuditEntry    │
│  (extended)     │     │     (NEW)       │     │     (NEW)       │
└─────────────────┘     └─────────────────┘     └─────────────────┘
        │                       │                       │
        │                       │                       │
        ▼                       ▼                       ▼
   ┌─────────┐           ┌─────────┐            ┌─────────┐
   │  User   │◀──────────│  User   │◀───────────│  User   │
   └─────────┘           └─────────┘            └─────────┘
```

---

## 1. Task (Extended)

Extends existing Task model from Phase 2-4.

### New Fields

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| recurrence_rule | RecurrenceRule | No | none | Repeat pattern |
| last_reminder_sent | datetime | No | null | Prevent duplicate reminders |
| parent_task_id | UUID | No | null | Link to original recurring task |

### RecurrenceRule Enum

```python
class RecurrenceRule(str, Enum):
    NONE = "none"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
```

### State Transitions

```
[pending] ──complete()──▶ [completed]
                              │
                              │ if recurrence_rule != none
                              ▼
                    Create new [pending] task
                    with next due_date
```

### Validation Rules

- `recurrence_rule` requires `due_date` to be set
- `parent_task_id` is set when task is auto-created from recurring parent
- `last_reminder_sent` is updated when reminder notification is created

---

## 2. Notification (NEW)

Represents in-app notifications for users.

### Fields

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| id | UUID | Yes | auto | Primary key |
| user_id | UUID | Yes | - | Owner of notification |
| type | NotificationType | Yes | - | Category of notification |
| title | string(100) | Yes | - | Short notification title |
| message | string(500) | No | null | Detailed message |
| read | boolean | Yes | false | Read status |
| task_id | UUID | No | null | Related task (for navigation) |
| created_at | datetime | Yes | now() | Creation timestamp |
| read_at | datetime | No | null | When marked as read |

### NotificationType Enum

```python
class NotificationType(str, Enum):
    REMINDER = "reminder"      # Task due soon
    SYSTEM = "system"          # General system info
    ACTION = "action"          # Task completed, etc.
```

### Indexes

- `ix_notification_user_unread`: (user_id, read) for unread count
- `ix_notification_user_created`: (user_id, created_at DESC) for listing
- `ix_notification_task`: (task_id) for task-related queries

### Validation Rules

- `title` max 100 characters
- `message` max 500 characters
- `task_id` must reference valid task owned by same user
- Notifications older than 90 days are auto-archived

---

## 3. AuditEntry (NEW)

Represents logged actions for audit trail.

### Fields

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| id | UUID | Yes | auto | Primary key |
| user_id | UUID | Yes | - | User who performed action |
| entity_type | string(50) | Yes | - | Type of entity (e.g., "task") |
| entity_id | UUID | Yes | - | ID of affected entity |
| action | AuditAction | Yes | - | Type of action |
| before_value | JSON | No | null | State before change |
| after_value | JSON | No | null | State after change |
| timestamp | datetime | Yes | now() | When action occurred |
| metadata | JSON | No | null | Additional context |

### AuditAction Enum

```python
class AuditAction(str, Enum):
    CREATE = "create"
    UPDATE = "update"
    COMPLETE = "complete"
    DELETE = "delete"
```

### Indexes

- `ix_audit_user_timestamp`: (user_id, timestamp DESC) for user history
- `ix_audit_entity`: (entity_type, entity_id, timestamp DESC) for entity history
- `ix_audit_timestamp`: (timestamp) for archival queries

### Validation Rules

- `entity_type` limited to known types: "task", "notification"
- `before_value` required for UPDATE actions
- `after_value` required for CREATE and UPDATE actions
- Entries older than 90 days are archived (moved or deleted)

---

## 4. Event Schemas

### TaskCompletedEvent

Published when a task is marked complete.

```json
{
  "schema_version": "1.0",
  "event_type": "task.completed",
  "timestamp": "2026-02-09T12:00:00Z",
  "user_id": "uuid",
  "task_id": "uuid",
  "task": {
    "id": "uuid",
    "title": "string",
    "recurrence_rule": "daily|weekly|monthly|none",
    "due_date": "2026-02-09T12:00:00Z"
  }
}
```

### ReminderEvent

Published when reminder check finds due tasks.

```json
{
  "schema_version": "1.0",
  "event_type": "task.reminder",
  "timestamp": "2026-02-09T12:00:00Z",
  "user_id": "uuid",
  "task_id": "uuid",
  "task_title": "string",
  "due_date": "2026-02-09T12:00:00Z"
}
```

### AuditEvent

Published for all task mutations.

```json
{
  "schema_version": "1.0",
  "event_type": "task.created|task.updated|task.completed|task.deleted",
  "timestamp": "2026-02-09T12:00:00Z",
  "user_id": "uuid",
  "entity_type": "task",
  "entity_id": "uuid",
  "action": "create|update|complete|delete",
  "before": { "field": "old_value" },
  "after": { "field": "new_value" }
}
```

---

## 5. Database Migration

### Migration: Add recurrence fields to Task

```sql
-- Add recurrence fields to task table
ALTER TABLE task ADD COLUMN recurrence_rule VARCHAR(20) DEFAULT 'none';
ALTER TABLE task ADD COLUMN last_reminder_sent TIMESTAMP NULL;
ALTER TABLE task ADD COLUMN parent_task_id UUID NULL REFERENCES task(id);

-- Create index for recurring tasks
CREATE INDEX ix_task_recurrence ON task(user_id, recurrence_rule) WHERE recurrence_rule != 'none';
```

### Migration: Create Notification table

```sql
CREATE TABLE notification (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
    type VARCHAR(20) NOT NULL,
    title VARCHAR(100) NOT NULL,
    message VARCHAR(500),
    read BOOLEAN NOT NULL DEFAULT FALSE,
    task_id UUID REFERENCES task(id) ON DELETE SET NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    read_at TIMESTAMP
);

CREATE INDEX ix_notification_user_unread ON notification(user_id, read);
CREATE INDEX ix_notification_user_created ON notification(user_id, created_at DESC);
CREATE INDEX ix_notification_task ON notification(task_id);
```

### Migration: Create AuditEntry table

```sql
CREATE TABLE audit_entry (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
    entity_type VARCHAR(50) NOT NULL,
    entity_id UUID NOT NULL,
    action VARCHAR(20) NOT NULL,
    before_value JSONB,
    after_value JSONB,
    timestamp TIMESTAMP NOT NULL DEFAULT NOW(),
    metadata JSONB
);

CREATE INDEX ix_audit_user_timestamp ON audit_entry(user_id, timestamp DESC);
CREATE INDEX ix_audit_entity ON audit_entry(entity_type, entity_id, timestamp DESC);
CREATE INDEX ix_audit_timestamp ON audit_entry(timestamp);
```

---

## 6. Relationships Summary

| From | To | Relationship | Cascade |
|------|-----|--------------|---------|
| Notification | User | Many-to-One | Delete |
| Notification | Task | Many-to-One (optional) | Set Null |
| AuditEntry | User | Many-to-One | Delete |
| Task | Task (parent) | Many-to-One (optional) | Set Null |

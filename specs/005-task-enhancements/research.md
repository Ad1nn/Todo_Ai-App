# Research: Task Enhancements (Quick Wins)

**Feature**: 005-task-enhancements
**Date**: 2026-02-04
**Status**: Complete

## Research Questions Resolved

### Q1: Current Task Model Structure

**Decision**: Extend existing `Task` SQLModel with 3 new nullable columns

**Rationale**: The current Task model (backend/src/models/task.py:16-26) uses SQLModel with clear schema separation (TaskBase, Task, TaskCreate, TaskUpdate, TaskPublic). Adding nullable fields maintains backward compatibility.

**Current Fields**:
- `id: UUID` (primary key)
- `user_id: UUID` (foreign key, indexed)
- `title: str` (1-200 chars)
- `description: str | None` (0-2000 chars)
- `completed: bool` (default False)
- `created_at: datetime` (UTC)
- `updated_at: datetime` (UTC)

**Alternatives Considered**:
- Separate tables for priority/category: Rejected - over-engineering for optional metadata
- JSON field for all metadata: Rejected - loses query/index capability

---

### Q2: Priority Level Implementation

**Decision**: Python StrEnum with 4 levels stored as VARCHAR(10)

**Rationale**: StrEnum provides type safety and serializes cleanly to JSON. VARCHAR allows database indexing and efficient queries.

**Priority Levels** (in sort order):
1. `urgent` - Immediate attention required
2. `high` - Important, needs attention soon
3. `normal` - Standard priority
4. `low` - Can wait, no urgency

**Alternatives Considered**:
- Integer values (1-4): Rejected - less readable in DB and API
- Separate priority table: Rejected - overkill for 4 fixed values
- 5+ levels: Rejected - spec defines 4 levels, YAGNI

---

### Q3: Category Storage Strategy

**Decision**: Free-text VARCHAR(50) stored directly on task

**Rationale**:
- Spec allows custom categories beyond suggestions (FR-013)
- No need for category management UI in this phase
- Query by exact match sufficient for filtering
- User's categories derived from existing tasks via DISTINCT query

**Suggested Categories** (hard-coded in UI):
- work, personal, shopping, health, finance

**Alternatives Considered**:
- Separate Category table with foreign key: Rejected - over-engineering for free-text labels
- Enum with fixed categories only: Rejected - spec requires custom categories
- Tags/array field: Rejected - complicates queries, single category per task sufficient

---

### Q4: Date Handling for Due Dates

**Decision**: `datetime` (TIMESTAMP) with nullable, stored as UTC

**Rationale**:
- Consistent with existing `created_at`/`updated_at` fields
- Backend stores UTC; frontend converts to local time for display
- AI agent interprets relative dates ("tomorrow") using server time
- Time component allows specific deadlines (e.g., "5pm today")

**Alternatives Considered**:
- DATE only (no time): Rejected - less flexibility for time-sensitive tasks
- Store with timezone: Rejected - complicates logic; UTC is standard practice
- Frontend-only display: Rejected - need server-side filtering for overdue queries

---

### Q5: Repository Query Strategy

**Decision**: Add `list_by_user_filtered()` method with optional filter parameters

**Rationale**:
- Current `list_by_user()` returns all tasks (backend/src/repositories/task_repository.py:30-35)
- New method accepts optional `category`, `priority`, `completed` filters
- SQLAlchemy `select().where()` chains conditionally for each filter
- Maintains backward compatibility - existing `list_by_user()` unchanged

**Query Parameters**:
```python
async def list_by_user_filtered(
    user_id: UUID,
    category: str | None = None,
    priority: Priority | None = None,
    completed: bool | None = None,
    sort_by: str = "created_at",  # or "due_date", "priority"
    sort_order: str = "desc"
) -> list[Task]
```

**Alternatives Considered**:
- Multiple specialized methods (list_by_category, list_by_priority): Rejected - combinatorial explosion
- Query builder class: Rejected - over-engineering for current needs

---

### Q6: API Contract for Filtering

**Decision**: Query parameters on existing `GET /api/v1/tasks` endpoint

**Rationale**:
- REST convention: filtering via query params
- Backward compatible - no params returns all tasks
- Single endpoint avoids proliferation

**Enhanced Endpoint**:
```
GET /api/v1/tasks?category=work&priority=high&completed=false&sort=due_date
```

**New Endpoint for Categories**:
```
GET /api/v1/tasks/categories → ["work", "personal", "shopping"]
```

**Alternatives Considered**:
- POST with filter body: Rejected - not RESTful for read operations
- Separate filtered endpoints: Rejected - unnecessary complexity

---

### Q7: MCP Tool Enhancement Strategy

**Decision**: Extend existing tools with optional parameters; add list_overdue tool

**Rationale**:
- `add_task` gains `due_date`, `priority`, `category` optional params
- `update_task` gains same params for modification
- `list_tasks` gains filter params
- New `list_overdue` tool for AI convenience

**Tool Updates**:
```python
# add_task - add optional params
async def add_task(title: str, description: str | None = None,
                   due_date: str | None = None,  # ISO 8601
                   priority: str | None = None,  # low/normal/high/urgent
                   category: str | None = None) -> dict

# list_tasks - add filter params
async def list_tasks(completed: bool | None = None,
                     category: str | None = None,
                     priority: str | None = None,
                     overdue: bool | None = None) -> dict
```

**Alternatives Considered**:
- Separate tools per field (set_priority, set_category): Rejected - adds 3 tools when 1 update_task suffices
- Remove completed filter: Rejected - already exists, useful

---

### Q8: Agent Prompt Enhancement

**Decision**: Extend SYSTEM_PROMPT with priority/category interpretation guidelines

**Rationale**:
- AI needs guidance for natural language → structured data mapping
- Date expressions: "tomorrow" → tomorrow's date
- Priority keywords: "urgent", "ASAP" → priority=urgent
- Category inference: "meeting" → category=work

**Keyword Mappings**:
```
Priority Inference:
- urgent, asap, immediately, critical → "urgent"
- important, soon, pressing → "high"
- (default, normal) → "normal"
- low, whenever, no rush, eventually → "low"

Category Inference:
- meeting, project, deadline, work, office → "work"
- grocery, shopping, buy, store → "shopping"
- doctor, gym, health, workout → "health"
- bills, payment, budget, money → "finance"
- (default) → "personal"
```

---

### Q9: Frontend Component Strategy

**Decision**: Extend TaskForm with date picker, priority dropdown, category combobox

**Rationale**:
- Form already uses controlled inputs (backend/src/components/TaskForm.tsx)
- Native `<input type="datetime-local">` for date picker (good browser support)
- `<select>` for priority (4 fixed options)
- `<input>` with `<datalist>` for category (suggestions + custom)

**New Form Fields**:
```tsx
<input type="datetime-local" name="due_date" />
<select name="priority">
  <option value="">No priority</option>
  <option value="low">Low</option>
  <option value="normal">Normal</option>
  <option value="high">High</option>
  <option value="urgent">Urgent</option>
</select>
<input list="categories" name="category" />
<datalist id="categories">
  <option value="work" />
  <option value="personal" />
  <option value="shopping" />
  <option value="health" />
  <option value="finance" />
</datalist>
```

---

### Q10: Visual Indicators for Due Date Status

**Decision**: Color-coded badges/text based on due date comparison to now

**Rationale**:
- Overdue (past + not completed): Red text/badge
- Due today: Yellow/amber badge
- Due this week: Normal display
- No due date: No indicator

**Color Mapping** (using existing design tokens):
- Overdue: `colors.error[600]` (red)
- Due today: `colors.warning[500]` (yellow/amber)
- Due soon (within 3 days): `colors.warning[300]` (light amber)
- Future/none: default text color

---

## Dependencies Verified

| Dependency | Status | Notes |
|------------|--------|-------|
| SQLModel | ✅ Verified | Already in use, supports nullable fields |
| Alembic | ✅ Verified | Migration 002 exists, pattern established |
| FastAPI | ✅ Verified | Query params supported via Depends/Query |
| OpenAI Agents SDK | ✅ Verified | @function_tool decorators extensible |
| TypeScript types | ✅ Verified | Interface extension straightforward |
| Tailwind CSS | ✅ Verified | Design tokens available for colors |

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Migration fails on existing data | Low | High | All new fields nullable, default NULL |
| AI misinterprets date expressions | Medium | Low | Clear prompt examples, fallback to clarification |
| Performance with large task lists | Low | Medium | Indexes on new columns, pagination later |
| Frontend date picker inconsistency | Low | Low | Use native HTML5, test across browsers |

## Conclusion

All research questions resolved. No NEEDS CLARIFICATION markers remain. Ready for Phase 1 design artifacts.

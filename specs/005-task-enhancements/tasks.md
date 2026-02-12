# Tasks: Task Enhancements (Quick Wins)

**Input**: Design documents from `/specs/005-task-enhancements/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Organization**: Tasks grouped by user story to enable independent implementation and testing.

## Format: `[ID] [P?] [Story?] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1-US5)
- Paths: `backend/` and `frontend/` (web app monorepo structure)

---

## Phase 1: Setup (Database Foundation)

**Purpose**: Database migration and model updates that enable all user stories

- [x] T001 Create database migration in backend/alembic/versions/003_add_task_enhancements.py
- [x] T002 Add Priority enum to backend/src/models/task.py
- [x] T003 Update TaskBase schema with due_date, priority, category fields in backend/src/models/task.py
- [x] T004 Update TaskCreate, TaskUpdate, TaskPublic schemas in backend/src/models/task.py
- [ ] T005 Run and verify migration with alembic upgrade head

**Checkpoint**: Database schema updated, all new fields available

---

## Phase 2: Foundational (Backend Core)

**Purpose**: Repository and service layer updates that MUST be complete before user story implementation

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T006 Update TaskRepository.create() to accept due_date, priority, category in backend/src/repositories/task_repository.py
- [x] T007 Add TaskRepository.list_by_user_filtered() method with filter params in backend/src/repositories/task_repository.py
- [x] T008 Add TaskRepository.get_user_categories() method in backend/src/repositories/task_repository.py
- [x] T009 Update TaskService.create() signature to accept new fields in backend/src/services/task_service.py
- [x] T010 Update TaskService.update() signature to accept new fields in backend/src/services/task_service.py
- [x] T011 Add TaskService.list_by_user_filtered() method in backend/src/services/task_service.py
- [x] T012 Add TaskService.get_user_categories() method in backend/src/services/task_service.py

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Set Due Dates for Time-Sensitive Tasks (Priority: P1) 🎯 MVP

**Goal**: Users can set, view, and edit due dates on tasks with visual overdue/today indicators

**Independent Test**: Create tasks with various due dates (past, today, future, none) and verify correct display with appropriate visual indicators

### Implementation for User Story 1

**Backend API (Due Date Support)**
- [x] T013 [US1] Update POST /tasks endpoint to accept due_date in backend/src/api/tasks.py
- [x] T014 [US1] Update PUT /tasks/{id} endpoint to accept due_date in backend/src/api/tasks.py

**Frontend Types**
- [x] T015 [P] [US1] Add due_date field to Task interface in frontend/src/lib/types.ts
- [x] T016 [P] [US1] Add TaskCreate and TaskUpdate due_date fields in frontend/src/lib/types.ts
- [x] T017 [P] [US1] Add helper functions (isTaskOverdue, isTaskDueToday, formatDueDate, getDueDateStatus) in frontend/src/lib/types.ts

**Frontend Components**
- [x] T018 [US1] Add due date picker input to TaskForm in frontend/src/components/TaskForm.tsx
- [x] T019 [US1] Add due date display with overdue/today indicators to TaskItem in frontend/src/components/TaskItem.tsx
- [x] T020 [US1] Update useTasks hook to include due_date in create/update in frontend/src/hooks/useTasks.ts

**Checkpoint**: Due dates fully functional - users can set, view, edit due dates with visual indicators

---

## Phase 4: User Story 2 - Assign Priority Levels to Tasks (Priority: P1)

**Goal**: Users can assign priority levels (low/normal/high/urgent) with color-coded badges and filtering

**Independent Test**: Create tasks with each priority level and verify correct display and filtering works

### Implementation for User Story 2

**Backend API (Priority Support)**
- [x] T021 [US2] Update POST /tasks endpoint to accept priority in backend/src/api/tasks.py
- [x] T022 [US2] Update PUT /tasks/{id} endpoint to accept priority in backend/src/api/tasks.py
- [x] T023 [US2] Add priority query param to GET /tasks endpoint in backend/src/api/tasks.py

**Frontend Types**
- [x] T024 [P] [US2] Add Priority type and PRIORITY_CONFIG constant in frontend/src/lib/types.ts
- [x] T025 [P] [US2] Add priority field to Task, TaskCreate, TaskUpdate interfaces in frontend/src/lib/types.ts

**Frontend Components**
- [x] T026 [US2] Add priority dropdown to TaskForm in frontend/src/components/TaskForm.tsx
- [x] T027 [US2] Add priority badge with color-coding to TaskItem in frontend/src/components/TaskItem.tsx
- [x] T028 [US2] Add priority filter dropdown to TaskList in frontend/src/components/TaskList.tsx
- [x] T029 [US2] Update useTasks hook to support priority filter param in frontend/src/hooks/useTasks.ts

**Checkpoint**: Priority levels fully functional - users can set, view, and filter by priority

---

## Phase 5: User Story 3 - Categorize Tasks for Organization (Priority: P2)

**Goal**: Users can assign categories with suggestions and filter by category

**Independent Test**: Create tasks in different categories and use category filters

### Implementation for User Story 3

**Backend API (Category Support)**
- [x] T030 [US3] Update POST /tasks endpoint to accept category in backend/src/api/tasks.py
- [x] T031 [US3] Update PUT /tasks/{id} endpoint to accept category in backend/src/api/tasks.py
- [x] T032 [US3] Add category query param to GET /tasks endpoint in backend/src/api/tasks.py
- [x] T033 [US3] Add GET /tasks/categories endpoint in backend/src/api/tasks.py

**Frontend Types**
- [x] T034 [P] [US3] Add DEFAULT_CATEGORIES constant in frontend/src/lib/types.ts
- [x] T035 [P] [US3] Add category field to Task, TaskCreate, TaskUpdate interfaces in frontend/src/lib/types.ts
- [x] T036 [P] [US3] Add TaskFilters interface and buildTaskQueryString helper in frontend/src/lib/types.ts

**Frontend Components**
- [x] T037 [US3] Add category input with datalist suggestions to TaskForm in frontend/src/components/TaskForm.tsx
- [x] T038 [US3] Add category tag display to TaskItem in frontend/src/components/TaskItem.tsx
- [x] T039 [US3] Add category filter dropdown to TaskList in frontend/src/components/TaskList.tsx
- [x] T040 [US3] Update useTasks hook to fetch categories and support category filter in frontend/src/hooks/useTasks.ts

**Checkpoint**: Categories fully functional - users can categorize tasks and filter by category

---

## Phase 6: User Story 4 - Natural Language Task Creation via AI Chat (Priority: P1)

**Goal**: AI chat interprets natural language for due dates, priorities, and categories

**Independent Test**: Send "add urgent task fix bug due tomorrow" via chat and verify correct metadata assignment

### Implementation for User Story 4

**MCP Tools**
- [x] T041 [US4] Update add_task tool to accept due_date, priority, category params in backend/src/mcp/tools.py
- [x] T042 [US4] Update list_tasks tool to accept priority, category, overdue filter params in backend/src/mcp/tools.py
- [x] T043 [US4] Update update_task tool to accept due_date, priority, category params in backend/src/mcp/tools.py
- [x] T044 [US4] Update _task_to_dict helper to include new fields in backend/src/mcp/tools.py

**Agent Configuration**
- [x] T045 [US4] Update TOOL_DESCRIPTIONS with enhanced descriptions in backend/src/agent/prompts.py
- [x] T046 [US4] Update SYSTEM_PROMPT with date/priority/category interpretation guidelines in backend/src/agent/prompts.py
- [x] T047 [US4] Update tool definitions in get_tool_definitions() in backend/src/agent/config.py

**Checkpoint**: AI chat understands natural language for all new task metadata

---

## Phase 7: User Story 5 - Combined Filtering and Sorting (Priority: P2)

**Goal**: Users can apply multiple filters and sort by due date or priority

**Independent Test**: Filter by category "work" AND priority "high", then sort by due date

### Implementation for User Story 5

**Backend API (Combined Filtering)**
- [x] T048 [US5] Add sort and order query params to GET /tasks endpoint in backend/src/api/tasks.py
- [x] T049 [US5] Add overdue query param to GET /tasks endpoint in backend/src/api/tasks.py
- [x] T050 [US5] Update list_by_user_filtered to support sorting in backend/src/repositories/task_repository.py

**Frontend Components**
- [x] T051 [US5] Add sort dropdown (created_at, due_date, priority) to TaskList in frontend/src/components/TaskList.tsx
- [x] T052 [US5] Add "show overdue only" toggle to TaskList in frontend/src/components/TaskList.tsx
- [x] T053 [US5] Implement filter state persistence (session) in TaskList in frontend/src/components/TaskList.tsx
- [x] T054 [US5] Add clear filters button to TaskList in frontend/src/components/TaskList.tsx
- [x] T055 [US5] Update useTasks hook to support all filter and sort params in frontend/src/hooks/useTasks.ts

**Checkpoint**: Combined filtering and sorting fully functional

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Integration testing, documentation, and cleanup

- [ ] T056 [P] Verify backward compatibility - existing tasks without new fields work correctly
- [ ] T057 [P] Verify migration rollback works with alembic downgrade -1
- [ ] T058 [P] Manual E2E test: create task with all fields via UI form
- [ ] T059 [P] Manual E2E test: create task via AI chat "add urgent work task review PR due Friday"
- [ ] T060 [P] Manual E2E test: filter by category and priority simultaneously
- [ ] T061 Run quickstart.md validation checklist

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - start immediately
- **Foundational (Phase 2)**: Depends on Phase 1 completion - BLOCKS all user stories
- **User Stories (Phases 3-7)**: All depend on Phase 2 completion
  - US1 (Due Dates) and US2 (Priority) can run in parallel after Phase 2
  - US3 (Categories) can run in parallel with US1/US2
  - US4 (AI Chat) depends on backend API changes from US1-US3 being deployed
  - US5 (Combined Filtering) depends on US2 and US3 filter implementations
- **Polish (Phase 8)**: Depends on all user stories being complete

### User Story Dependencies

| Story | Depends On | Can Parallelize With |
|-------|------------|----------------------|
| US1 (Due Dates) | Phase 2 | US2, US3 |
| US2 (Priority) | Phase 2 | US1, US3 |
| US3 (Categories) | Phase 2 | US1, US2 |
| US4 (AI Chat) | US1, US2, US3 backend API tasks | - |
| US5 (Combined Filtering) | US2 (T028-T029), US3 (T039-T040) | - |

### Within Each User Story

1. Backend API changes first
2. Frontend types second (can parallelize)
3. Frontend components third (depend on types)
4. Hook updates last (depend on components)

### Parallel Opportunities

**Phase 1 (Setup)** - Sequential (migration must complete before model changes)

**Phase 2 (Foundational)** - T006-T008 (repository) can run in parallel, then T009-T012 (service) can run in parallel

**Phase 3-5 (US1-US3)** - All three user stories can run in parallel after Phase 2:
```
Developer A: T013-T020 (US1: Due Dates)
Developer B: T021-T029 (US2: Priority)
Developer C: T030-T040 (US3: Categories)
```

**Within US1**:
```
# Parallel frontend types:
T015, T016, T017 (all different aspects of types.ts)
```

**Within US2**:
```
# Parallel frontend types:
T024, T025 (both types.ts but different sections)
```

**Within US3**:
```
# Parallel frontend types:
T034, T035, T036 (all different sections of types.ts)
```

**Phase 8 (Polish)** - T056-T060 can run in parallel (independent validation tests)

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T005)
2. Complete Phase 2: Foundational (T006-T012)
3. Complete Phase 3: User Story 1 - Due Dates (T013-T020)
4. **STOP and VALIDATE**: Test due dates independently
5. Deploy/demo - users can now set deadlines!

### Recommended Full Implementation

1. Setup + Foundational → Foundation ready
2. US1 (Due Dates) + US2 (Priority) in parallel → Both P1 stories complete
3. US3 (Categories) → P2 story complete
4. US4 (AI Chat) → Natural language support
5. US5 (Combined Filtering) → Power user features
6. Polish → Final validation

### Single Developer Path

```
Day 1: T001-T012 (Setup + Foundational)
Day 2: T013-T020 (US1: Due Dates) - DEMO READY
Day 3: T021-T029 (US2: Priority)
Day 4: T030-T040 (US3: Categories)
Day 5: T041-T047 (US4: AI Chat)
Day 6: T048-T055 (US5: Combined Filtering)
Day 7: T056-T061 (Polish)
```

---

## Summary

| Phase | Story | Tasks | Parallel Opportunities |
|-------|-------|-------|------------------------|
| 1 | Setup | T001-T005 | Sequential |
| 2 | Foundational | T006-T012 | T006-T008, then T009-T012 |
| 3 | US1: Due Dates | T013-T020 | T015-T017 |
| 4 | US2: Priority | T021-T029 | T024-T025 |
| 5 | US3: Categories | T030-T040 | T034-T036 |
| 6 | US4: AI Chat | T041-T047 | T041-T044 |
| 7 | US5: Combined Filtering | T048-T055 | - |
| 8 | Polish | T056-T061 | T056-T060 |

**Total Tasks**: 61
**MVP Tasks** (US1 only): 20 (T001-T020)
**Full Implementation**: 61 tasks

---

## Notes

- All new fields are nullable for backward compatibility
- Frontend types.ts changes can be batched into single commits per story
- AI chat (US4) requires backend API to be deployed first
- Each checkpoint is a valid demo/release point
- Commit after each task or logical group

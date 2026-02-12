# Tasks: In-Memory Console Todo App

**Input**: Design documents from `/specs/001-console-todo-app/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: TDD approach - tests written first (per Constitution Principle IV)

**Organization**: Tasks grouped by user story to enable independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/`, `tests/` at repository root
- Based on plan.md: 4-layer architecture (models, services, storage, cli)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [ ] T001 Create project structure with src/ and tests/ directories per plan.md
- [ ] T002 Initialize UV project with pyproject.toml (Python 3.13+, pytest, pytest-cov, ruff)
- [ ] T003 [P] Create src/__init__.py package marker
- [ ] T004 [P] Create src/models/__init__.py package marker
- [ ] T005 [P] Create src/services/__init__.py package marker
- [ ] T006 [P] Create src/storage/__init__.py package marker
- [ ] T007 [P] Create src/cli/__init__.py package marker
- [ ] T008 [P] Create tests/__init__.py package marker
- [ ] T009 [P] Create tests/unit/__init__.py package marker
- [ ] T010 [P] Create tests/integration/__init__.py package marker

**Checkpoint**: Project structure ready, UV configured, all packages initialized

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Tests for Foundational Components (TDD - write FIRST, ensure they FAIL)

- [ ] T011 [P] Unit tests for Task model validation in tests/unit/test_task.py
- [ ] T012 [P] Unit tests for MemoryStore CRUD operations in tests/unit/test_memory_store.py

### Implementation for Foundational Components

- [ ] T013 Implement Task dataclass with validation in src/models/task.py
- [ ] T014 Implement MemoryStore with CRUD operations in src/storage/memory_store.py
- [ ] T015 Verify T011 and T012 tests now PASS

**Checkpoint**: Foundation ready - Task model and MemoryStore working. User story implementation can now begin.

---

## Phase 3: User Story 1 - Add a New Task (Priority: P1) 🎯 MVP

**Goal**: Allow users to add a new task with title and optional description

**Independent Test**: Run app → Select "Add Task" → Enter title "Test Task" → Verify confirmation message and task stored

**Spec Reference**: US1, FR-001, FR-002, FR-003, FR-010

### Tests for User Story 1 (TDD - write FIRST, ensure they FAIL)

- [ ] T016 [P] [US1] Unit test for TaskService.add_task() in tests/unit/test_task_service.py
- [ ] T017 [P] [US1] Unit test for add_task validation (empty title rejection) in tests/unit/test_task_service.py

### Implementation for User Story 1

- [ ] T018 [US1] Implement TaskService.add_task() method in src/services/task_service.py
- [ ] T019 [US1] Implement CLI add task menu option in src/cli/menu.py
- [ ] T020 [US1] Add user input handling for title and description in src/cli/menu.py
- [ ] T021 [US1] Add success/error message display for add task in src/cli/menu.py
- [ ] T022 [US1] Verify T016 and T017 tests now PASS

**Checkpoint**: User can add tasks via CLI. Story 1 is independently functional and testable.

---

## Phase 4: User Story 2 - View All Tasks (Priority: P1)

**Goal**: Allow users to view all tasks with status indicators

**Independent Test**: Add 2-3 tasks → Select "View All" → Verify all tasks displayed with ID, title, description, and completion status

**Spec Reference**: US2, FR-004, FR-005

### Tests for User Story 2 (TDD - write FIRST, ensure they FAIL)

- [ ] T023 [P] [US2] Unit test for TaskService.get_all_tasks() in tests/unit/test_task_service.py
- [ ] T024 [P] [US2] Unit test for empty task list display in tests/unit/test_task_service.py

### Implementation for User Story 2

- [ ] T025 [US2] Implement TaskService.get_all_tasks() method in src/services/task_service.py
- [ ] T026 [US2] Implement CLI view all tasks menu option in src/cli/menu.py
- [ ] T027 [US2] Add formatted task list display with status indicators ([ ] / [x]) in src/cli/menu.py
- [ ] T028 [US2] Add empty list message handling in src/cli/menu.py
- [ ] T029 [US2] Verify T023 and T024 tests now PASS

**Checkpoint**: User can view all tasks with status. Stories 1 and 2 independently functional.

---

## Phase 5: User Story 3 - Mark Task as Complete (Priority: P2)

**Goal**: Allow users to toggle task completion status by ID

**Independent Test**: Add task → Mark as complete → View tasks → Verify [x] indicator → Toggle again → Verify [ ] indicator

**Spec Reference**: US3, FR-006, FR-009

### Tests for User Story 3 (TDD - write FIRST, ensure they FAIL)

- [ ] T030 [P] [US3] Unit test for TaskService.toggle_complete() in tests/unit/test_task_service.py
- [ ] T031 [P] [US3] Unit test for toggle_complete with invalid ID in tests/unit/test_task_service.py

### Implementation for User Story 3

- [ ] T032 [US3] Implement TaskService.toggle_complete() method in src/services/task_service.py
- [ ] T033 [US3] Implement CLI mark complete menu option in src/cli/menu.py
- [ ] T034 [US3] Add task ID input handling with validation in src/cli/menu.py
- [ ] T035 [US3] Add success/error message display for toggle in src/cli/menu.py
- [ ] T036 [US3] Verify T030 and T031 tests now PASS

**Checkpoint**: User can toggle task completion. Stories 1, 2, and 3 independently functional.

---

## Phase 6: User Story 4 - Update Task Details (Priority: P3)

**Goal**: Allow users to update task title and/or description by ID

**Independent Test**: Add task → Update title → View tasks → Verify changed title → Update description → Verify changed description

**Spec Reference**: US4, FR-007, FR-009, FR-010

### Tests for User Story 4 (TDD - write FIRST, ensure they FAIL)

- [ ] T037 [P] [US4] Unit test for TaskService.update_task() in tests/unit/test_task_service.py
- [ ] T038 [P] [US4] Unit test for update_task validation (empty title, invalid ID) in tests/unit/test_task_service.py

### Implementation for User Story 4

- [ ] T039 [US4] Implement TaskService.update_task() method in src/services/task_service.py
- [ ] T040 [US4] Implement CLI update task menu option in src/cli/menu.py
- [ ] T041 [US4] Add input handling for optional title/description updates in src/cli/menu.py
- [ ] T042 [US4] Add success/error message display for update in src/cli/menu.py
- [ ] T043 [US4] Verify T037 and T038 tests now PASS

**Checkpoint**: User can update tasks. Stories 1-4 independently functional.

---

## Phase 7: User Story 5 - Delete a Task (Priority: P3)

**Goal**: Allow users to delete a task by ID

**Independent Test**: Add task → Delete by ID → View tasks → Verify task removed

**Spec Reference**: US5, FR-008, FR-009

### Tests for User Story 5 (TDD - write FIRST, ensure they FAIL)

- [ ] T044 [P] [US5] Unit test for TaskService.delete_task() in tests/unit/test_task_service.py
- [ ] T045 [P] [US5] Unit test for delete_task with invalid ID in tests/unit/test_task_service.py

### Implementation for User Story 5

- [ ] T046 [US5] Implement TaskService.delete_task() method in src/services/task_service.py
- [ ] T047 [US5] Implement CLI delete task menu option in src/cli/menu.py
- [ ] T048 [US5] Add task ID input handling with validation in src/cli/menu.py
- [ ] T049 [US5] Add success/error message display for delete in src/cli/menu.py
- [ ] T050 [US5] Verify T044 and T045 tests now PASS

**Checkpoint**: User can delete tasks. All 5 user stories independently functional.

---

## Phase 8: CLI Integration & Exit (Cross-Story)

**Purpose**: Complete CLI with main loop and exit functionality

**Spec Reference**: FR-011, FR-012

### Tests for CLI Integration

- [ ] T051 [P] Integration test for full menu workflow in tests/integration/test_cli.py
- [ ] T052 [P] Integration test for invalid menu input handling in tests/integration/test_cli.py

### Implementation for CLI Integration

- [ ] T053 Implement main menu loop with option selection in src/cli/menu.py
- [ ] T054 Implement exit option (option 6) in src/cli/menu.py
- [ ] T055 Add invalid menu option error handling in src/cli/menu.py
- [ ] T056 Implement CLI entry point in src/cli/__main__.py
- [ ] T057 Verify T051 and T052 integration tests now PASS

**Checkpoint**: Complete working CLI application with all menu options.

---

## Phase 9: Polish & Quality Gates

**Purpose**: Final quality checks and documentation

- [ ] T058 Run full test suite: `uv run pytest --cov=src --cov-report=term-missing`
- [ ] T059 Verify coverage >80%: `uv run pytest --cov=src --cov-fail-under=80`
- [ ] T060 Run linting: `uv run ruff check src/ tests/`
- [ ] T061 Run formatting: `uv run ruff format --check src/ tests/`
- [ ] T062 Fix any linting/formatting issues
- [ ] T063 Validate quickstart.md workflow manually
- [ ] T064 Final code review against Constitution principles

**Checkpoint**: All quality gates passed. Phase 1 complete.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - start immediately
- **Foundational (Phase 2)**: Depends on Setup - BLOCKS all user stories
- **User Stories (Phases 3-7)**: All depend on Foundational completion
  - Can proceed sequentially (P1 → P1 → P2 → P3 → P3)
  - Or in parallel if multiple developers available
- **CLI Integration (Phase 8)**: Depends on all user stories complete
- **Polish (Phase 9)**: Depends on CLI Integration complete

### User Story Dependencies

| Story | Priority | Depends On | Can Start After |
|-------|----------|------------|-----------------|
| US1: Add Task | P1 | Foundational | Phase 2 |
| US2: View Tasks | P1 | Foundational | Phase 2 |
| US3: Mark Complete | P2 | Foundational | Phase 2 |
| US4: Update Task | P3 | Foundational | Phase 2 |
| US5: Delete Task | P3 | Foundational | Phase 2 |

**Note**: All user stories are independently testable after Phase 2.

### Within Each User Story (TDD Order)

1. Write tests FIRST - must FAIL initially
2. Implement service method
3. Implement CLI handling
4. Verify tests now PASS
5. Move to next story

### Parallel Opportunities

**Phase 1 (Setup)**:
```
T003, T004, T005, T006, T007, T008, T009, T010 can all run in parallel
```

**Phase 2 (Foundational Tests)**:
```
T011, T012 can run in parallel
```

**User Story Tests** (within each story):
```
All tests within a story marked [P] can run in parallel
```

---

## Parallel Example: User Story 1

```bash
# Launch tests for US1 in parallel:
Task: "Unit test for TaskService.add_task() in tests/unit/test_task_service.py"
Task: "Unit test for add_task validation in tests/unit/test_task_service.py"

# After tests written, implement sequentially:
Task: "Implement TaskService.add_task() method"
Task: "Implement CLI add task menu option"
Task: "Verify tests now PASS"
```

---

## Implementation Strategy

### MVP First (User Stories 1 & 2 Only)

1. ✅ Complete Phase 1: Setup
2. ✅ Complete Phase 2: Foundational
3. ✅ Complete Phase 3: US1 - Add Task
4. ✅ Complete Phase 4: US2 - View Tasks
5. **STOP and VALIDATE**: Test adding and viewing tasks
6. Can demonstrate/deploy minimal working todo app

### Full Implementation

1. Setup → Foundational → Foundation ready
2. US1 (Add) → US2 (View) → Basic CRUD visible
3. US3 (Complete) → Status tracking works
4. US4 (Update) → US5 (Delete) → Full CRUD complete
5. CLI Integration → Complete application
6. Polish → Quality gates passed

### Single Developer Order

```
T001 → T002 → T003-T010 (parallel) → T011-T012 (parallel) → T013 → T014 → T015
→ T016-T017 (parallel) → T018-T022 → T023-T024 (parallel) → T025-T029
→ T030-T031 (parallel) → T032-T036 → T037-T038 (parallel) → T039-T043
→ T044-T045 (parallel) → T046-T050 → T051-T052 (parallel) → T053-T057
→ T058-T064
```

---

## Task Summary

| Phase | Description | Task Count | Parallel Tasks |
|-------|-------------|------------|----------------|
| 1 | Setup | 10 | 8 |
| 2 | Foundational | 5 | 2 |
| 3 | US1: Add Task | 7 | 2 |
| 4 | US2: View Tasks | 7 | 2 |
| 5 | US3: Mark Complete | 7 | 2 |
| 6 | US4: Update Task | 7 | 2 |
| 7 | US5: Delete Task | 7 | 2 |
| 8 | CLI Integration | 7 | 2 |
| 9 | Polish | 7 | 0 |
| **Total** | | **64** | **22** |

---

## Notes

- TDD approach: Write tests first, verify they FAIL, then implement
- [P] tasks = different files, no dependencies - can run in parallel
- [Story] label maps task to specific user story for traceability
- Each user story is independently completable and testable after Phase 2
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- All tasks reference exact file paths per plan.md structure

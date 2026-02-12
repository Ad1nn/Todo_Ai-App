# Tasks: Full-Stack Web Todo Application

**Input**: Design documents from `/specs/002-fullstack-web-app/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/openapi.yaml

**Tests**: Test-first approach per constitution Principle IV. Tests included for each user story.

**Organization**: Tasks grouped by user story (6 stories: 2x P1, 2x P2, 2x P3)

## Format: `[ID] [P?] [Story?] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: US1, US2, US3, US4, US5, US6 (maps to spec.md user stories)
- Paths: `backend/src/`, `frontend/src/` (monorepo structure)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Initialize monorepo with backend and frontend projects

- [x] T001 Create monorepo directory structure with backend/ and frontend/ directories
- [x] T002 [P] Initialize backend Python project with UV in backend/pyproject.toml
- [x] T003 [P] Initialize frontend Next.js 15+ project with TypeScript in frontend/
- [x] T004 [P] Configure backend linting with ruff in backend/pyproject.toml
- [x] T005 [P] Configure frontend linting with ESLint and Prettier in frontend/
- [x] T006 [P] Create backend/.env.example with DATABASE_URL, JWT_SECRET, CORS_ORIGINS
- [x] T007 [P] Create frontend/.env.local.example with NEXT_PUBLIC_API_URL
- [x] T008 [P] Configure Tailwind CSS in frontend/tailwind.config.ts

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T009 Create database connection module in backend/src/db/session.py
- [x] T010 Create environment configuration in backend/src/config.py
- [x] T011 Initialize Alembic migrations in backend/alembic/
- [x] T012 [P] Create User SQLModel in backend/src/models/user.py
- [x] T013 [P] Create Task SQLModel in backend/src/models/task.py
- [x] T014 Create initial Alembic migration for User and Task tables in backend/alembic/versions/
- [x] T015 Create FastAPI app entry point in backend/src/main.py with CORS middleware
- [x] T016 Create API dependency injection module in backend/src/api/deps.py
- [x] T017 [P] Create TypeScript types in frontend/src/lib/types.ts
- [x] T018 [P] Create API client base in frontend/src/lib/api.ts
- [x] T019 [P] Create reusable Button component in frontend/src/components/ui/Button.tsx
- [x] T020 [P] Create reusable Input component in frontend/src/components/ui/Input.tsx
- [x] T021 [P] Create reusable Modal component in frontend/src/components/ui/Modal.tsx
- [x] T022 Create root layout with providers in frontend/src/app/layout.tsx
- [x] T023 Create pytest fixtures in backend/tests/conftest.py

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - User Registration and Login (Priority: P1) 🎯 MVP

**Goal**: Users can create accounts and authenticate to access the application

**Independent Test**: Register new account, login, verify session established, logout

### Tests for User Story 1

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T024 [P] [US1] Unit tests for AuthService in backend/tests/unit/test_auth_service.py
- [x] T025 [P] [US1] Integration tests for auth API in backend/tests/integration/test_auth_api.py

### Backend Implementation for User Story 1

- [x] T026 [US1] Create UserRepository in backend/src/repositories/user_repository.py
- [x] T027 [US1] Create AuthService with JWT and bcrypt in backend/src/services/auth_service.py
- [x] T028 [US1] Create auth API routes (register, login, logout, me) in backend/src/api/auth.py
- [x] T029 [US1] Add JWT validation dependency in backend/src/api/deps.py

### Frontend Implementation for User Story 1

- [x] T030 [P] [US1] Create auth utilities in frontend/src/lib/auth.ts
- [x] T031 [P] [US1] Create useAuth hook in frontend/src/hooks/useAuth.ts
- [x] T032 [US1] Create LoginForm component in frontend/src/components/LoginForm.tsx
- [x] T033 [US1] Create RegisterForm component in frontend/src/components/RegisterForm.tsx
- [x] T034 [US1] Create login page in frontend/src/app/login/page.tsx
- [x] T035 [US1] Create register page in frontend/src/app/register/page.tsx
- [x] T036 [US1] Create home page with auth redirect in frontend/src/app/page.tsx

**Checkpoint**: Users can register, login, and logout. Auth system complete.

---

## Phase 4: User Story 2 - Create and View Tasks (Priority: P1) 🎯 MVP

**Goal**: Authenticated users can create tasks and view their task list

**Independent Test**: Login, create task with title/description, verify task appears in list

### Tests for User Story 2

- [x] T037 [P] [US2] Unit tests for TaskService in backend/tests/unit/test_task_service.py
- [x] T038 [P] [US2] Integration tests for tasks API (create, list) in backend/tests/integration/test_tasks_api.py

### Backend Implementation for User Story 2

- [x] T039 [US2] Create TaskRepository in backend/src/repositories/task_repository.py
- [x] T040 [US2] Create TaskService with create/list methods in backend/src/services/task_service.py
- [x] T041 [US2] Create tasks API routes (POST, GET list) in backend/src/api/tasks.py

### Frontend Implementation for User Story 2

- [x] T042 [US2] Create useTasks hook in frontend/src/hooks/useTasks.ts
- [x] T043 [US2] Create TaskForm component in frontend/src/components/TaskForm.tsx
- [x] T044 [US2] Create TaskItem component in frontend/src/components/TaskItem.tsx
- [x] T045 [US2] Create TaskList component in frontend/src/components/TaskList.tsx
- [x] T046 [US2] Create tasks page in frontend/src/app/tasks/page.tsx

**Checkpoint**: Users can create and view tasks. Core todo functionality complete.

---

## Phase 5: User Story 3 - Mark Tasks Complete/Incomplete (Priority: P2)

**Goal**: Users can toggle task completion status

**Independent Test**: Create task, toggle complete, verify visual indicator, refresh and verify persisted

### Tests for User Story 3

- [x] T047 [P] [US3] Integration tests for toggle endpoint in backend/tests/integration/test_tasks_api.py

### Backend Implementation for User Story 3

- [x] T048 [US3] Add toggle_complete method to TaskService in backend/src/services/task_service.py
- [x] T049 [US3] Add PATCH toggle endpoint to tasks API in backend/src/api/tasks.py

### Frontend Implementation for User Story 3

- [x] T050 [US3] Add toggle functionality to useTasks hook in frontend/src/hooks/useTasks.ts
- [x] T051 [US3] Add completion toggle to TaskItem component in frontend/src/components/TaskItem.tsx

**Checkpoint**: Users can mark tasks complete/incomplete with visual feedback.

---

## Phase 6: User Story 4 - Update Task Details (Priority: P2)

**Goal**: Users can edit task title and description

**Independent Test**: Edit existing task, change title/description, save, verify changes

### Tests for User Story 4

- [x] T052 [P] [US4] Integration tests for update endpoint in backend/tests/integration/test_tasks_api.py

### Backend Implementation for User Story 4

- [x] T053 [US4] Add update method to TaskService in backend/src/services/task_service.py
- [x] T054 [US4] Add PUT update endpoint to tasks API in backend/src/api/tasks.py

### Frontend Implementation for User Story 4

- [x] T055 [US4] Add update functionality to useTasks hook in frontend/src/hooks/useTasks.ts
- [x] T056 [US4] Add edit mode to TaskItem component in frontend/src/components/TaskItem.tsx
- [x] T057 [US4] Add edit form/modal for task editing in frontend/src/components/TaskForm.tsx

**Checkpoint**: Users can edit task details with validation.

---

## Phase 7: User Story 5 - Delete Tasks (Priority: P3)

**Goal**: Users can permanently delete tasks with confirmation

**Independent Test**: Delete task, confirm dialog, verify removal from list

### Tests for User Story 5

- [x] T058 [P] [US5] Integration tests for delete endpoint in backend/tests/integration/test_tasks_api.py

### Backend Implementation for User Story 5

- [x] T059 [US5] Add delete method to TaskService in backend/src/services/task_service.py
- [x] T060 [US5] Add DELETE endpoint to tasks API in backend/src/api/tasks.py

### Frontend Implementation for User Story 5

- [x] T061 [US5] Add delete functionality to useTasks hook in frontend/src/hooks/useTasks.ts
- [x] T062 [US5] Add delete button with confirmation to TaskItem in frontend/src/components/TaskItem.tsx

**Checkpoint**: Users can delete tasks with confirmation dialog.

---

## Phase 8: User Story 6 - Responsive Web Interface (Priority: P3)

**Goal**: Application works well on mobile and desktop screens

**Independent Test**: Access app on 320px, 768px, 1920px widths, verify all features work

### Frontend Implementation for User Story 6

- [x] T063 [US6] Add responsive styles to TaskList component in frontend/src/components/TaskList.tsx
- [x] T064 [US6] Add responsive styles to TaskItem component in frontend/src/components/TaskItem.tsx
- [x] T065 [US6] Add responsive styles to LoginForm/RegisterForm in frontend/src/components/
- [x] T066 [US6] Add responsive layout to tasks page in frontend/src/app/tasks/page.tsx
- [x] T067 [US6] Add mobile navigation menu in frontend/src/app/layout.tsx

**Checkpoint**: Application fully responsive from 320px to 1920px.

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Quality improvements across all user stories

- [x] T068 Run all backend tests and ensure 80%+ coverage
- [x] T069 Run all frontend tests and ensure component coverage
- [x] T070 [P] Run ruff format and ruff check on backend
- [x] T071 [P] Run ESLint and Prettier on frontend
- [x] T072 Run Alembic migration up/down test
- [x] T073 Validate quickstart.md setup instructions
- [x] T074 Final end-to-end testing of all user stories

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies - start immediately
- **Phase 2 (Foundational)**: Depends on Phase 1 - BLOCKS all user stories
- **Phase 3 (US1 Auth)**: Depends on Phase 2 - MVP foundation
- **Phase 4 (US2 Create/View)**: Depends on Phase 3 (needs auth) - Core functionality
- **Phase 5 (US3 Toggle)**: Depends on Phase 4 (needs tasks)
- **Phase 6 (US4 Update)**: Depends on Phase 4 (needs tasks)
- **Phase 7 (US5 Delete)**: Depends on Phase 4 (needs tasks)
- **Phase 8 (US6 Responsive)**: Can start after Phase 2, polish after all features
- **Phase 9 (Polish)**: Depends on all stories complete

### User Story Dependencies

```
Phase 1 (Setup)
     ↓
Phase 2 (Foundational)
     ↓
Phase 3 (US1: Auth) ←── Required for all task operations
     ↓
Phase 4 (US2: Create/View) ←── Core task functionality
     ↓
   ┌─┴─┬───┐
   ↓   ↓   ↓
 US3  US4  US5  (can run in parallel)
   └─┬─┴───┘
     ↓
Phase 8 (US6: Responsive)
     ↓
Phase 9 (Polish)
```

### Parallel Opportunities

**Phase 1**: T002, T003, T004, T005, T006, T007, T008 (all independent)

**Phase 2**: T012+T013 (models), T017+T018+T019+T020+T021 (frontend foundations)

**Phase 3**: T024+T025 (tests), T030+T031 (frontend utilities)

**Phase 4**: T037+T038 (tests)

**Phases 5-7**: Can run in parallel after Phase 4 completes

---

## Implementation Strategy

### MVP First (User Stories 1 + 2)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: User Story 1 (Auth)
4. Complete Phase 4: User Story 2 (Create/View Tasks)
5. **STOP and VALIDATE**: Can register, login, create tasks, view tasks
6. Deploy MVP demo

### Incremental Delivery

1. Setup + Foundational → Backend and frontend scaffolds ready
2. + US1 (Auth) → Users can register and login
3. + US2 (Create/View) → **MVP COMPLETE** - Basic todo functionality
4. + US3 (Toggle) → Task completion tracking
5. + US4 (Update) → Edit capability
6. + US5 (Delete) → Cleanup capability
7. + US6 (Responsive) → Mobile-friendly
8. Polish → Production-ready

---

## Task Summary

| Phase | User Story | Task Count | Parallel Tasks |
|-------|------------|------------|----------------|
| 1 | Setup | 8 | 7 |
| 2 | Foundational | 15 | 8 |
| 3 | US1 (Auth) | 13 | 4 |
| 4 | US2 (Create/View) | 10 | 2 |
| 5 | US3 (Toggle) | 5 | 1 |
| 6 | US4 (Update) | 6 | 1 |
| 7 | US5 (Delete) | 5 | 1 |
| 8 | US6 (Responsive) | 5 | 0 |
| 9 | Polish | 7 | 2 |
| **Total** | | **74** | **26** |

---

## Notes

- [P] tasks can run in parallel (different files, no dependencies)
- Backend tests use pytest + httpx for async API testing
- Frontend uses TypeScript strict mode
- All tasks include file paths for immediate execution
- Commit after each task or logical group
- Run quality gates (T068-T071) before final validation

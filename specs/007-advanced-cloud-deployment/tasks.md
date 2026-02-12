# Tasks: Advanced Cloud Deployment

**Input**: Design documents from `/specs/007-advanced-cloud-deployment/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/

**Tests**: Not explicitly requested in specification. Implementation tasks focus on feature development.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Backend**: `backend/src/`, `backend/tests/`
- **Frontend**: `frontend/src/`, `frontend/tests/`
- **Events**: `backend/src/events/`
- **Dapr**: `backend/dapr/components/`
- **CI/CD**: `.github/workflows/`
- **Helm**: `helm/todo-app/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Initialize Dapr, Kafka, and event infrastructure

- [x] T001 Install Dapr CLI and initialize locally with `dapr init`
- [x] T002 Start Redpanda container for local Kafka with `docker run redpandadata/redpanda`
- [x] T003 Create Kafka topics `todo.reminders` and `todo.audit` using `rpk topic create`
- [x] T004 [P] Create Dapr components directory at backend/dapr/components/
- [x] T005 [P] Create pubsub.yaml Dapr component in backend/dapr/components/pubsub.yaml
- [x] T006 [P] Create cron-reminder.yaml Dapr binding in backend/dapr/components/cron-reminder.yaml
- [x] T007 [P] Create subscriptions.yaml for event routing in backend/dapr/components/subscriptions.yaml
- [x] T008 Add dapr-py SDK dependency to backend/pyproject.toml
- [x] T009 Verify Dapr sidecar starts with backend using `dapr run --app-id todo-backend`

**Checkpoint**: Dapr + Kafka infrastructure ready - database migrations can begin

---

## Phase 2: Foundational (Database Migrations)

**Purpose**: Database schema changes that ALL user stories depend on

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T010 Create RecurrenceRule enum in backend/src/models/task.py
- [x] T011 Add recurrence_rule field to Task model in backend/src/models/task.py
- [x] T012 Add last_reminder_sent field to Task model in backend/src/models/task.py
- [x] T013 Add parent_task_id field to Task model in backend/src/models/task.py
- [x] T014 [P] Create NotificationType enum in backend/src/models/notification.py
- [x] T015 [P] Create Notification model in backend/src/models/notification.py
- [x] T016 [P] Create AuditAction enum in backend/src/models/audit.py
- [x] T017 [P] Create AuditEntry model in backend/src/models/audit.py
- [x] T018 Generate Alembic migration for Phase 5 models with `alembic revision --autogenerate`
- [x] T019 Run database migration with `alembic upgrade head`
- [x] T020 [P] Add RecurrenceRule, Priority, and Notification types to frontend/src/lib/types.ts
- [x] T021 [P] Create events module directory at backend/src/events/
- [x] T022 Create event producer base in backend/src/events/producers.py
- [x] T023 Create event consumer base in backend/src/events/consumers.py

**Checkpoint**: Database ready, event infrastructure ready - user story implementation can begin

---

## Phase 3: User Story 1 - Set Recurring Tasks (Priority: P1) 🎯 MVP

**Goal**: Users can create tasks with daily/weekly/monthly recurrence patterns that auto-create next occurrence on completion

**Independent Test**: Create a task with daily recurrence, mark complete, verify new task is created for tomorrow

### Implementation for User Story 1

- [x] T024 [US1] Update TaskCreate schema to include recurrence_rule in backend/src/models/task.py
- [x] T025 [US1] Update TaskUpdate schema to include recurrence_rule in backend/src/models/task.py
- [x] T026 [US1] Update TaskPublic schema to include recurrence_rule, parent_task_id in backend/src/models/task.py
- [x] T027 [US1] Create calculate_next_due_date function in backend/src/services/task_service.py
- [x] T028 [US1] Update task_service.create() to handle recurrence_rule in backend/src/services/task_service.py
- [x] T029 [US1] Update task_service.update() to handle recurrence_rule in backend/src/services/task_service.py
- [x] T030 [US1] Create task_service.complete_recurring_task() that creates next occurrence in backend/src/services/task_service.py
- [x] T031 [US1] Update PUT /tasks/{id}/complete endpoint to call complete_recurring_task in backend/src/api/tasks.py
- [x] T032 [US1] Publish task.completed event on completion in backend/src/api/tasks.py
- [x] T033 [US1] Update add_task MCP tool to accept recurrence_rule in backend/src/mcp/tools.py
- [x] T034 [US1] Update update_task MCP tool to accept recurrence_rule in backend/src/mcp/tools.py
- [x] T035 [US1] Update agent prompts with recurrence examples in backend/src/agent/prompts.py
- [x] T036 [P] [US1] Add RecurrenceSelect dropdown component in frontend/src/components/RecurrenceSelect.tsx
- [x] T037 [US1] Update TaskForm to include RecurrenceSelect in frontend/src/components/TaskForm.tsx
- [x] T038 [US1] Add recurrence badge to TaskItem display in frontend/src/components/TaskItem.tsx
- [x] T039 [US1] Update useTasks hook to handle recurrence in task creation in frontend/src/hooks/useTasks.ts

**Checkpoint**: Recurring tasks feature complete - users can create and complete recurring tasks

---

## Phase 4: User Story 2 - Receive Task Reminders (Priority: P1) 🎯 MVP

**Goal**: Users receive toast notifications and see bell icon with unread count when tasks are due soon

**Independent Test**: Create task due in 15 minutes, trigger reminder check, verify toast appears and bell shows count

**Depends on**: User Story 1 (needs task with due_date), Foundational (Notification model)

### Implementation for User Story 2

- [x] T040 [P] [US2] Create NotificationCreate/NotificationPublic schemas in backend/src/models/notification.py
- [x] T041 [US2] Create notification_repository with CRUD operations in backend/src/repositories/notification_repository.py
- [x] T042 [US2] Create notification_service with create, list, mark_read, mark_all_read in backend/src/services/notification_service.py
- [x] T043 [US2] Create reminder_service.check_due_tasks() for cron handler in backend/src/services/reminder_service.py
- [x] T044 [US2] Create reminder_service.handle_cron_trigger() endpoint handler in backend/src/services/reminder_service.py
- [x] T045 [US2] Register cron handler endpoint at POST /events/cron/reminder-check in backend/src/api/events.py
- [x] T046 [US2] Create reminder event consumer to create notifications in backend/src/events/consumers.py
- [x] T047 [US2] Register reminder event subscription at POST /events/reminders in backend/src/api/events.py
- [x] T048 [P] [US2] Create GET /notifications endpoint in backend/src/api/notifications.py
- [x] T049 [P] [US2] Create GET /notifications/unread-count endpoint in backend/src/api/notifications.py
- [x] T050 [P] [US2] Create POST /notifications/{id}/read endpoint in backend/src/api/notifications.py
- [x] T051 [P] [US2] Create POST /notifications/mark-all-read endpoint in backend/src/api/notifications.py
- [x] T052 [US2] Register notifications router in backend/src/main.py
- [x] T053 [P] [US2] Create useNotifications hook with polling in frontend/src/hooks/useNotifications.ts
- [x] T054 [P] [US2] Create Toast component with 5s auto-dismiss in frontend/src/components/Toast.tsx
- [x] T055 [P] [US2] Create ToastContainer for managing toast queue in frontend/src/components/ToastContainer.tsx
- [x] T056 [P] [US2] Create NotificationBell with unread count badge in frontend/src/components/NotificationBell.tsx
- [x] T057 [US2] Create NotificationCenter dropdown with list in frontend/src/components/NotificationCenter.tsx
- [x] T058 [US2] Add NotificationBell to header layout in frontend/src/components/Header.tsx
- [x] T059 [US2] Add ToastContainer to root layout in frontend/src/app/layout.tsx
- [x] T060 [US2] Create NotificationContext for global state in frontend/src/providers/NotificationProvider.tsx

**Checkpoint**: Notification system complete - users receive reminders via toast and bell icon

---

## Phase 5: User Story 3 - View Activity Audit Trail (Priority: P2)

**Goal**: Users can see a history of all task operations with timestamps and before/after values

**Independent Test**: Create task, update title, complete task, verify audit log shows all 3 entries with correct details

**Depends on**: Foundational (AuditEntry model)

### Implementation for User Story 3

- [x] T061 [P] [US3] Create AuditEntryCreate/AuditEntryPublic schemas in backend/src/models/audit.py
- [x] T062 [US3] Create audit_repository with create, list_by_user, list_by_entity in backend/src/repositories/audit_repository.py
- [x] T063 [US3] Create audit_service with log_action, list_entries in backend/src/services/audit_service.py
- [x] T064 [US3] Create audit event producer function in backend/src/events/producers.py
- [x] T065 [US3] Create audit event consumer to persist entries in backend/src/events/consumers.py
- [x] T066 [US3] Register audit event subscription at POST /events/audit in backend/src/api/events.py
- [x] T067 [US3] Publish audit event on task create in backend/src/services/task_service.py
- [x] T068 [US3] Publish audit event on task update in backend/src/services/task_service.py
- [x] T069 [US3] Publish audit event on task complete in backend/src/services/task_service.py
- [x] T070 [US3] Publish audit event on task delete in backend/src/services/task_service.py
- [x] T071 [P] [US3] Create GET /audit endpoint with filters in backend/src/api/audit.py
- [x] T072 [P] [US3] Create GET /audit/task/{task_id} endpoint in backend/src/api/audit.py
- [x] T073 [US3] Register audit router in backend/src/main.py
- [x] T074 [P] [US3] Create useAudit hook for fetching audit log in frontend/src/hooks/useAudit.ts
- [x] T075 [P] [US3] Create AuditEntry component for single entry display in frontend/src/components/AuditEntry.tsx
- [x] T076 [US3] Create AuditLog component with filtering in frontend/src/components/AuditLog.tsx
- [x] T077 [US3] Add audit log tab/section to task detail view in frontend/src/components/TaskDetail.tsx

**Checkpoint**: Audit trail complete - users can view full history of task operations

---

## Phase 6: User Story 4 - Deploy Application to Cloud (Priority: P2)

**Goal**: Application is deployed to DigitalOcean DOKS with automated CI/CD via GitHub Actions

**Independent Test**: Push to main branch, verify GitHub Actions runs, application accessible via public URL

**Depends on**: US1, US2 complete (core features must work before cloud deploy)

### Implementation for User Story 4

- [x] T078 [US4] Create DigitalOcean Kubernetes cluster with `doctl kubernetes cluster create`
- [x] T079 [US4] Create DigitalOcean Container Registry with `doctl registry create`
- [x] T080 [US4] Configure kubectl context with `doctl kubernetes cluster kubeconfig save`
- [x] T081 [US4] Install Dapr on DOKS cluster with `helm install dapr dapr/dapr`
- [x] T082 [P] [US4] Create values-staging.yaml for Helm chart in helm/todo-app/values-staging.yaml
- [x] T083 [P] [US4] Create values-production.yaml for Helm chart in helm/todo-app/values-production.yaml
- [x] T084 [US4] Create Dapr components Kubernetes manifest in helm/todo-app/templates/dapr-components.yaml
- [x] T085 [US4] Update backend deployment to include Dapr annotations in helm/todo-app/templates/backend-deployment.yaml
- [x] T086 [P] [US4] Create GitHub Actions CI workflow in .github/workflows/ci.yml
- [x] T087 [P] [US4] Create GitHub Actions deploy workflow in .github/workflows/deploy.yml
- [ ] T088 [US4] Configure GitHub repository secrets (DIGITALOCEAN_ACCESS_TOKEN, etc.)
- [ ] T089 [US4] Push to main branch and verify CI/CD pipeline runs
- [ ] T090 [US4] Verify application is accessible via DigitalOcean Load Balancer URL
- [ ] T091 [US4] Test rollback with `helm rollback todo-app -n todo-app-production`

**Checkpoint**: Cloud deployment complete - application running on DOKS with automated deployments

---

## Phase 7: User Story 5 - Manage Notifications (Priority: P3)

**Goal**: Users can manage notification preferences and clear/archive old notifications

**Independent Test**: Disable reminders in settings, create due task, verify no notification appears

**Depends on**: User Story 2 (notification system must exist)

### Implementation for User Story 5

- [x] T092 [P] [US5] Add notification_preferences field to User model in backend/src/models/user.py
- [x] T093 [US5] Create user_preferences_service for managing settings in backend/src/services/user_preferences_service.py
- [x] T094 [P] [US5] Create GET /users/me/preferences endpoint in backend/src/api/users.py
- [x] T095 [P] [US5] Create PATCH /users/me/preferences endpoint in backend/src/api/users.py
- [x] T096 [US5] Create DELETE /notifications/clear endpoint in backend/src/api/notifications.py
- [x] T097 [US5] Update reminder_service to check user preferences before notifying in backend/src/services/reminder_service.py
- [x] T098 [US5] Create notification archival job for 30+ day old entries in backend/src/services/notification_service.py
- [x] T099 [P] [US5] Create NotificationSettings component in frontend/src/components/NotificationSettings.tsx
- [x] T100 [US5] Add settings modal to NotificationCenter in frontend/src/components/NotificationCenter.tsx
- [x] T101 [US5] Add "Clear all" button to NotificationCenter in frontend/src/components/NotificationCenter.tsx

**Checkpoint**: Notification management complete - users can customize notification behavior

---

## Phase 8: User Story 6 - Monitor Application Health (Priority: P3)

**Goal**: Developers can view application health metrics and logs in DigitalOcean

**Independent Test**: Access DO monitoring dashboard, verify metrics visible for all pods

**Depends on**: User Story 4 (must be deployed to cloud first)

### Implementation for User Story 6

- [ ] T102 [US6] Enable DigitalOcean Monitoring for DOKS cluster
- [ ] T103 [US6] Configure Kubernetes resource metrics in values-production.yaml
- [ ] T104 [P] [US6] Add structured logging to backend with JSON format in backend/src/core/logging.py
- [ ] T105 [P] [US6] Add request tracing with correlation IDs in backend/src/middleware/tracing.py
- [ ] T106 [US6] Configure log aggregation in DigitalOcean
- [ ] T107 [US6] Create health check documentation in docs/monitoring.md
- [ ] T108 [US6] Set up basic alerts for pod restarts and high CPU in DigitalOcean

**Checkpoint**: Monitoring complete - developers can observe and troubleshoot production

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Final documentation, cleanup, and validation

- [ ] T109 [P] Update quickstart.md with validated local development commands
- [ ] T110 [P] Create deployment runbook in docs/deployment.md
- [x] T111 [P] Update CLAUDE.md with Phase 5 technology additions
- [ ] T112 Run full end-to-end test: recurring task → reminder → notification → audit
- [ ] T113 Verify all health probes pass in production cluster
- [ ] T114 Create environment variable template in scripts/env.template
- [ ] T115 Security review: ensure no secrets in code or logs
- [ ] T116 Performance validation: verify reminders delivered within 1 minute

---

## Dependencies & Execution Order

### Phase Dependencies

```
Phase 1 (Setup) ──────────────────────────────────────────────────────┐
    │                                                                  │
    ▼                                                                  │
Phase 2 (Foundational - Database + Events) ───────────────────────────┤
    │                                                                  │
    ├────────────────┬────────────────┐                               │
    ▼                ▼                ▼                               │
Phase 3 (US1)    Phase 4 (US2)    Phase 5 (US3)                       │
Recurring        Reminders        Audit Trail                         │
    │                │                │                               │
    └────────────────┴────────────────┘                               │
                     │                                                 │
                     ▼                                                 │
              Phase 6 (US4) ◄─────────────────────────────────────────┘
              Cloud Deploy
                     │
         ┌──────────┴──────────┐
         ▼                     ▼
   Phase 7 (US5)         Phase 8 (US6)
   Notification Mgmt     Monitoring
         │                     │
         └──────────┬──────────┘
                    ▼
             Phase 9 (Polish)
```

### User Story Dependencies

| Story | Depends On | Can Start After |
|-------|------------|-----------------|
| US1 (Recurring Tasks) | Foundational | Phase 2 complete |
| US2 (Reminders) | Foundational, US1 (due_date) | Phase 2 complete |
| US3 (Audit Trail) | Foundational | Phase 2 complete |
| US4 (Cloud Deploy) | US1, US2 minimum | Phase 3+4 complete |
| US5 (Notification Mgmt) | US2 | Phase 4 complete |
| US6 (Monitoring) | US4 | Phase 6 complete |

### Parallel Opportunities

**Within Phase 1 (Setup)**:
- T004, T005, T006, T007 can run in parallel (different files)

**Within Phase 2 (Foundational)**:
- T014, T015, T016, T017 can run in parallel (different model files)
- T020, T021 can run in parallel with backend model work

**Within Phase 3 (US1)**:
- T036 can run in parallel with backend work (different directory)

**Within Phase 4 (US2)**:
- T048, T049, T050, T051 can run in parallel (different endpoints)
- T053, T054, T055, T056 can run in parallel (different components)

**Within Phase 5 (US3)**:
- T071, T072 can run in parallel (different endpoints)
- T074, T075 can run in parallel (different files)

**Within Phase 6 (US4)**:
- T082, T083 can run in parallel (different value files)
- T086, T087 can run in parallel (different workflow files)

**After Phase 2**:
- Phases 3, 4, 5 can proceed in parallel (if team capacity allows)

---

## Parallel Example: User Story 2

```bash
# Backend endpoints can be created in parallel:
T048: GET /notifications in backend/src/api/notifications.py
T049: GET /notifications/unread-count in backend/src/api/notifications.py
T050: POST /notifications/{id}/read in backend/src/api/notifications.py
T051: POST /notifications/mark-all-read in backend/src/api/notifications.py

# Frontend components can be created in parallel:
T053: useNotifications hook in frontend/src/hooks/useNotifications.ts
T054: Toast component in frontend/src/components/Toast.tsx
T055: ToastContainer in frontend/src/components/ToastContainer.tsx
T056: NotificationBell in frontend/src/components/NotificationBell.tsx
```

---

## Implementation Strategy

### MVP First (User Stories 1 + 2)

1. Complete Phase 1: Setup (Dapr + Kafka)
2. Complete Phase 2: Foundational (Database migrations)
3. Complete Phase 3: User Story 1 (Recurring Tasks)
4. Complete Phase 4: User Story 2 (Reminders + Notifications)
5. **STOP and VALIDATE**: Test recurring tasks with reminders locally
6. Demo/deploy if ready - this is the MVP!

### Incremental Delivery

| Milestone | Includes | Value Delivered |
|-----------|----------|-----------------|
| MVP | Setup + Foundational + US1 + US2 | Recurring tasks with reminders |
| +Audit | + US3 | Full task history tracking |
| +Cloud | + US4 | Production deployment |
| +Polish | + US5 + US6 + Polish | Notification settings, monitoring |

### Estimated Task Counts

| Phase | Tasks | Parallel Opportunities |
|-------|-------|------------------------|
| Phase 1: Setup | 9 | 4 |
| Phase 2: Foundational | 14 | 8 |
| Phase 3: US1 (Recurring) | 16 | 1 |
| Phase 4: US2 (Reminders) | 21 | 12 |
| Phase 5: US3 (Audit) | 17 | 6 |
| Phase 6: US4 (Cloud) | 14 | 4 |
| Phase 7: US5 (Notif Mgmt) | 10 | 4 |
| Phase 8: US6 (Monitoring) | 7 | 2 |
| Phase 9: Polish | 8 | 3 |
| **Total** | **116** | **44** |

---

## Notes

- [P] tasks = different files, no dependencies on incomplete tasks
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Dapr sidecar must be running for event features to work
- Commit after each phase completion
- Stop at any checkpoint to validate story independently
- Local testing with Redpanda before cloud deployment
- GitHub secrets must be configured before CI/CD will work

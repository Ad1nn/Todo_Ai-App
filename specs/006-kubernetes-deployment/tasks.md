# Tasks: Kubernetes Deployment

**Input**: Design documents from `/specs/006-kubernetes-deployment/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/

**Tests**: Not explicitly requested in specification. Tasks focus on validation and documentation.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Helm chart**: `helm/todo-app/`
- **Backend**: `backend/`
- **Frontend**: `frontend/`
- **Scripts**: `scripts/`
- **Docs**: `docs/`

---

## Phase 1: Setup (Prerequisites Validation)

**Purpose**: Verify development environment and existing infrastructure

- [x] T001 Verify Docker Desktop is running with `docker version`
- [x] T002 Verify Kubernetes is enabled with `kubectl cluster-info`
- [x] T003 Verify Helm is installed with `helm version`
- [x] T004 [P] Validate backend Dockerfile syntax with `docker build --check` in backend/Dockerfile
- [x] T005 [P] Validate frontend Dockerfile syntax with `docker build --check` in frontend/Dockerfile
- [x] T006 Validate Helm chart with `helm lint ./helm/todo-app`

**Checkpoint**: All prerequisites verified - image building can begin

---

## Phase 2: Foundational (Helm Chart Validation)

**Purpose**: Ensure Helm chart templates render correctly before deployment

**⚠️ CRITICAL**: Chart must be valid before any deployment tasks

- [x] T007 Run `helm template ./helm/todo-app` to verify template rendering
- [x] T008 [P] Review backend-deployment.yaml template output for correctness
- [x] T009 [P] Review frontend-deployment.yaml template output for correctness
- [x] T010 [P] Review secrets.yaml template output for proper secret structure
- [x] T011 Verify NOTES.txt renders with post-install instructions

**Checkpoint**: Helm chart validated - user story implementation can begin

---

## Phase 3: User Story 2 - Build Production-Ready Container Images (Priority: P1) 🎯 MVP

**Goal**: Build optimized Docker images for backend and frontend that pass size and security requirements

**Independent Test**: Run `docker build` for each service and verify image sizes are under limits (500MB backend, 300MB frontend)

### Implementation for User Story 2

- [x] T012 [P] [US2] Build backend Docker image with `docker build -t todo-backend:latest ./backend`
- [x] T013 [P] [US2] Build frontend Docker image with `docker build -t todo-frontend:latest ./frontend`
- [x] T014 [US2] Verify backend image size is under 500MB with `docker images todo-backend` (434MB ✓)
- [x] T015 [US2] Verify frontend image size is under 300MB with `docker images todo-frontend` (104MB ✓)
- [x] T016 [P] [US2] Test backend image standalone with `docker run -p 8000:8000 todo-backend` and curl /health
- [x] T017 [P] [US2] Test frontend image standalone with `docker run -p 3000:3000 todo-frontend` and verify page loads
- [x] T018 [US2] Verify backend runs as non-root user with `docker run todo-backend id` (appuser:1000 ✓)
- [x] T019 [US2] Verify frontend runs as non-root user with `docker run todo-frontend id` (nextjs:1001 ✓)

**Checkpoint**: Both images built, sized correctly, and running as non-root users

---

## Phase 4: User Story 1 - Deploy Application to Local Cluster (Priority: P1) 🎯 MVP

**Goal**: Deploy complete application to Kubernetes with single helm install command

**Independent Test**: Run helm install and verify pods reach Running state, application accessible via NodePort

**Depends on**: User Story 2 (images must be built first)

### Implementation for User Story 1

- [x] T020 [US1] Create todo-app namespace with `kubectl create namespace todo-app`
- [x] T021 [US1] Deploy application with `helm install todo-app ./helm/todo-app --namespace todo-app --set backend.image.pullPolicy=Never --set frontend.image.pullPolicy=Never --set secrets.databaseUrl="$DATABASE_URL" --set secrets.jwtSecret="$JWT_SECRET" --set secrets.openaiApiKey="$OPENAI_API_KEY"`
- [x] T022 [US1] Verify backend pod reaches Running state with `kubectl get pods -n todo-app -l app=todo-app-backend`
- [x] T023 [US1] Verify frontend pod reaches Running state with `kubectl get pods -n todo-app -l app=todo-app-frontend`
- [x] T024 [US1] Verify backend health probe passes with `kubectl describe pod -n todo-app -l app=todo-app-backend`
- [x] T025 [US1] Verify frontend health probe passes with `kubectl describe pod -n todo-app -l app=todo-app-frontend`
- [x] T026 [US1] Access application via NodePort at http://localhost:30000 and verify login page loads (HTTP 200 ✓)
- [x] T027 [US1] Alternatively test with port-forward `kubectl port-forward svc/todo-app-frontend 3000:3000 -n todo-app`

**Checkpoint**: Application deployed and accessible - core deployment story complete

---

## Phase 5: User Story 3 - Configure Application Secrets Securely (Priority: P2)

**Goal**: Verify secrets are properly handled - passed via --set flags, stored in K8s Secrets, never in values.yaml

**Independent Test**: Inspect Secret object and verify values are base64 encoded, values.yaml has empty placeholders

### Implementation for User Story 3

- [ ] T028 [US3] Verify secrets.yaml template creates proper Secret structure in helm/todo-app/templates/secrets.yaml
- [ ] T029 [US3] Verify values.yaml has empty secret placeholders with `grep -A3 "secrets:" helm/todo-app/values.yaml`
- [ ] T030 [US3] Inspect deployed Secret with `kubectl get secret todo-app-secrets -n todo-app -o yaml`
- [ ] T031 [US3] Verify SECRET values are base64 encoded (not plaintext)
- [ ] T032 [US3] Verify backend pod has DATABASE_URL env var from Secret with `kubectl exec -n todo-app deploy/todo-app-backend -- env | grep DATABASE`
- [ ] T033 [US3] Test application connects to database by creating a task via the UI

**Checkpoint**: Secrets properly secured and application functional with real database

---

## Phase 6: User Story 4 - Scale and Update Deployments (Priority: P2)

**Goal**: Test Kubernetes scaling and rolling update capabilities

**Independent Test**: Scale replicas, perform upgrade, perform rollback - all without downtime

### Implementation for User Story 4

- [ ] T034 [US4] Scale backend to 3 replicas with `helm upgrade todo-app ./helm/todo-app -n todo-app --reuse-values --set backend.replicaCount=3`
- [ ] T035 [US4] Verify 3 backend pods running with `kubectl get pods -n todo-app -l app=todo-app-backend`
- [ ] T036 [US4] Verify application still accessible during scaling
- [ ] T037 [US4] Perform rolling update by restarting deployment `kubectl rollout restart deployment/todo-app-backend -n todo-app`
- [ ] T038 [US4] Watch rolling update progress with `kubectl rollout status deployment/todo-app-backend -n todo-app`
- [ ] T039 [US4] Verify zero downtime during rolling update (continuous curl to health endpoint)
- [ ] T040 [US4] Test rollback with `helm rollback todo-app 1 -n todo-app`
- [ ] T041 [US4] Verify rollback completes and pods healthy

**Checkpoint**: Scaling and updates work correctly - production-like operations validated

---

## Phase 7: User Story 5 - Monitor Application Health (Priority: P3)

**Goal**: Document and validate observability commands for troubleshooting

**Independent Test**: Run kubectl commands to view logs, describe pods, check events

### Implementation for User Story 5

- [ ] T042 [US5] View backend logs with `kubectl logs -l app=todo-app-backend -n todo-app --tail=50`
- [ ] T043 [US5] View frontend logs with `kubectl logs -l app=todo-app-frontend -n todo-app --tail=50`
- [ ] T044 [US5] Describe backend pod with `kubectl describe pod -l app=todo-app-backend -n todo-app`
- [ ] T045 [US5] View cluster events with `kubectl get events -n todo-app --sort-by='.lastTimestamp'`
- [ ] T046 [US5] Check resource usage with `kubectl top pods -n todo-app` (requires metrics-server)
- [ ] T047 [US5] Document troubleshooting commands in docs/phase4-kubernetes.md troubleshooting section

**Checkpoint**: Observability validated - developers can troubleshoot issues

---

## Phase 8: Polish & Documentation

**Purpose**: Complete documentation and create automation script

- [ ] T048 [P] Create deployment automation script in scripts/deploy-local.sh
- [ ] T049 [P] Update quickstart.md with validated commands in specs/006-kubernetes-deployment/quickstart.md
- [ ] T050 Add troubleshooting section to docs/phase4-kubernetes.md
- [ ] T051 [P] Create environment variable template in scripts/env.template
- [ ] T052 Run full deployment from scratch to validate quickstart.md
- [ ] T053 Clean up with `helm uninstall todo-app -n todo-app && kubectl delete namespace todo-app`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies - verify environment first
- **Phase 2 (Foundational)**: Depends on Phase 1 - validate chart before building
- **Phase 3 (US2 - Build Images)**: Depends on Phase 2 - build images before deployment
- **Phase 4 (US1 - Deploy)**: Depends on Phase 3 - images must exist
- **Phase 5 (US3 - Secrets)**: Depends on Phase 4 - application must be deployed
- **Phase 6 (US4 - Scale/Update)**: Depends on Phase 4 - application must be deployed
- **Phase 7 (US5 - Monitor)**: Depends on Phase 4 - application must be deployed
- **Phase 8 (Polish)**: Depends on all user stories complete

### User Story Dependencies

```
Phase 1 (Setup)
    ↓
Phase 2 (Foundational)
    ↓
Phase 3 (US2 - Build Images) ──────────────────────────────────┐
    ↓                                                           │
Phase 4 (US1 - Deploy to K8s) ─────────────────────────────────┤
    ├──────────────────────┬───────────────────┐               │
    ↓                      ↓                   ↓               │
Phase 5 (US3)         Phase 6 (US4)       Phase 7 (US5)        │
(Secrets)             (Scale/Update)      (Monitor)            │
    └──────────────────────┴───────────────────┘               │
                           ↓                                    │
                    Phase 8 (Polish) ◄─────────────────────────┘
```

### Parallel Opportunities

**Within Phase 1**:
- T004, T005 can run in parallel (different Dockerfiles)

**Within Phase 2**:
- T008, T009, T010 can run in parallel (reviewing different templates)

**Within Phase 3 (US2)**:
- T012, T013 can run in parallel (different images)
- T016, T017 can run in parallel (different containers)

**After Phase 4**:
- Phases 5, 6, 7 can run in parallel (independent validation)

**Within Phase 8**:
- T048, T049, T051 can run in parallel (different files)

---

## Parallel Example: User Story 2

```bash
# Build both images in parallel:
docker build -t todo-backend:latest ./backend &
docker build -t todo-frontend:latest ./frontend &
wait

# Test both images in parallel:
docker run -d -p 8000:8000 --name backend-test todo-backend
docker run -d -p 3000:3000 --name frontend-test todo-frontend

# Verify both respond:
curl http://localhost:8000/health
curl http://localhost:3000

# Cleanup:
docker stop backend-test frontend-test
docker rm backend-test frontend-test
```

---

## Implementation Strategy

### MVP First (User Stories 1 + 2)

1. Complete Phase 1: Setup (verify environment)
2. Complete Phase 2: Foundational (validate chart)
3. Complete Phase 3: User Story 2 (build images)
4. Complete Phase 4: User Story 1 (deploy to K8s)
5. **STOP and VALIDATE**: Application running in Kubernetes
6. Demo/deploy if ready - this is the MVP!

### Incremental Delivery

1. Phases 1-4 → MVP: Application deployed to K8s
2. Add Phase 5 (US3) → Secrets properly configured
3. Add Phase 6 (US4) → Scaling/updates validated
4. Add Phase 7 (US5) → Observability documented
5. Add Phase 8 → Automation and documentation complete

### Estimated Effort

| Phase | Tasks | Estimated Time |
|-------|-------|----------------|
| Phase 1: Setup | 6 | 10 minutes |
| Phase 2: Foundational | 5 | 15 minutes |
| Phase 3: US2 (Build) | 8 | 20 minutes |
| Phase 4: US1 (Deploy) | 8 | 15 minutes |
| Phase 5: US3 (Secrets) | 6 | 10 minutes |
| Phase 6: US4 (Scale) | 8 | 15 minutes |
| Phase 7: US5 (Monitor) | 6 | 10 minutes |
| Phase 8: Polish | 6 | 20 minutes |
| **Total** | **53** | **~2 hours** |

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Existing infrastructure (Dockerfiles, Helm charts) already pass constitution checks
- Focus is on validation, testing, and documentation
- Most tasks are verification/validation rather than new code
- Commit after each phase completion
- Stop at any checkpoint to validate story independently

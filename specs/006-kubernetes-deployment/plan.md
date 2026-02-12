# Implementation Plan: Kubernetes Deployment

**Branch**: `006-kubernetes-deployment` | **Date**: 2026-02-08 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/006-kubernetes-deployment/spec.md`

## Summary

Deploy the Todo application (backend + frontend) to a local Kubernetes cluster using Docker containerization and Helm charts. The infrastructure files (Dockerfiles, Helm charts) already exist and follow constitution principles. This phase focuses on validation, testing, and documentation of the deployment workflow.

## Technical Context

**Language/Version**: Python 3.13+ (backend), Node.js 22+ (frontend)
**Primary Dependencies**: Docker, Kubernetes (Docker Desktop), Helm 3.x, kubectl
**Storage**: External Neon PostgreSQL (not containerized)
**Testing**: Manual validation via kubectl, helm lint, docker build
**Target Platform**: Local Kubernetes (Docker Desktop or Minikube)
**Project Type**: Web application (monorepo with backend/ and frontend/)
**Performance Goals**: Pods ready within 60 seconds, images under 500MB/300MB
**Constraints**: Secrets via --set flags only, imagePullPolicy: Never for local builds
**Scale/Scope**: Single developer local deployment, 1 replica default

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Principle XI: Container & Orchestration (Phase 4+)

| Requirement | Status | Evidence |
|-------------|--------|----------|
| Dockerfile for each service | ✅ PASS | `backend/Dockerfile`, `frontend/Dockerfile` exist |
| Multi-stage builds | ✅ PASS | Both use builder → runtime stages |
| Slim base images | ✅ PASS | `python:3.13-slim-bookworm`, `node:22-slim` |
| Dependencies in separate layer | ✅ PASS | COPY pyproject.toml before src/, package.json before source |
| No dev dependencies in image | ✅ PASS | `--no-dev` flag, `npm ci` with build-only deps |
| Secrets not baked in | ✅ PASS | Environment variables used, no hardcoded values |
| EXPOSE directive | ✅ PASS | EXPOSE 8000 (backend), EXPOSE 3000 (frontend) |
| Helm chart structure | ✅ PASS | Chart.yaml, values.yaml, templates/ exist |
| Resource requests/limits | ✅ PASS | Defined in values.yaml |
| Liveness/readiness probes | ✅ PASS | HEALTHCHECK in Dockerfiles, probes in values.yaml |
| Services with correct types | ✅ PASS | ClusterIP (backend), NodePort (frontend) in values.yaml |
| Secrets in K8s Secret | ✅ PASS | secrets.yaml template exists |
| Non-root user | ✅ PASS | appuser (backend), nextjs (frontend) created |

### Other Principles Check

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Spec-Driven Development | ✅ PASS | Infrastructure created via prior specs |
| II. Clean Code | ✅ PASS | Dockerfiles well-documented with comments |
| VI. Simplicity First | ✅ PASS | Single Helm chart for both services |
| VIII. Security | ✅ PASS | Non-root users, secrets via env vars |

**GATE STATUS**: ✅ PASSED - No violations detected

## Project Structure

### Documentation (this feature)

```text
specs/006-kubernetes-deployment/
├── spec.md              # Feature specification
├── plan.md              # This file
├── research.md          # Phase 0: Existing infrastructure analysis
├── data-model.md        # Phase 1: Kubernetes resource definitions
├── quickstart.md        # Phase 1: Deployment guide
├── contracts/           # Phase 1: Helm value contracts
│   └── helm-values.md   # Required Helm --set values
└── checklists/
    └── requirements.md  # Quality checklist
```

### Source Code (repository root)

```text
# Existing infrastructure files
backend/
├── Dockerfile           # Multi-stage Python build
├── src/                 # Application code
└── pyproject.toml       # Dependencies

frontend/
├── Dockerfile           # Multi-stage Node.js build
├── src/                 # Application code
└── package.json         # Dependencies

helm/todo-app/
├── Chart.yaml           # Chart metadata (v0.1.0)
├── values.yaml          # Default configuration
├── .helmignore          # Ignored files
└── templates/
    ├── _helpers.tpl           # Template helpers
    ├── backend-deployment.yaml # Backend Deployment
    ├── backend-service.yaml    # Backend Service (ClusterIP)
    ├── frontend-deployment.yaml # Frontend Deployment
    ├── frontend-service.yaml   # Frontend Service (NodePort)
    ├── secrets.yaml            # Kubernetes Secret
    └── NOTES.txt               # Post-install instructions

# Deployment script (to be created)
scripts/
└── deploy-local.sh      # Automated local deployment
```

**Structure Decision**: Monorepo with separate backend/ and frontend/ directories. Single Helm chart manages both services.

## Complexity Tracking

> No violations - no complexity justification needed.

## Phase 0: Research Findings

### Existing Infrastructure Analysis

**Decision**: Use existing Dockerfiles and Helm charts as-is
**Rationale**: Files already exist and pass constitution checks
**Alternatives Considered**:
- Creating new charts: Rejected (existing charts are complete)
- Using Kustomize instead of Helm: Rejected (Helm already implemented)

### Local Kubernetes Options

**Decision**: Support Docker Desktop Kubernetes (primary) and Minikube (fallback)
**Rationale**: Docker Desktop K8s is simpler for developers already using Docker
**Alternatives Considered**:
- Kind (Kubernetes in Docker): Good option but adds complexity
- K3s: Lightweight but requires separate installation

### Image Build Strategy

**Decision**: Build images locally with docker build, use imagePullPolicy: Never
**Rationale**: Simpler than setting up local registry for development
**Alternatives Considered**:
- Local registry: Adds complexity, not needed for single-developer use
- Minikube docker-env: Minikube-specific, not portable

### Secret Management

**Decision**: Pass secrets via Helm --set flags at install time
**Rationale**: Simple, secure for local development, no files to commit
**Alternatives Considered**:
- External Secrets Operator: Overkill for local dev
- Sealed Secrets: Requires additional tooling
- .env file with envsubst: Less secure, files could be committed

## Phase 1: Design Artifacts

### Data Model: Kubernetes Resources

See `data-model.md` for complete resource definitions.

**Key Resources**:
- **Deployment (backend)**: 1 replica, python:3.13-slim-bookworm, port 8000
- **Deployment (frontend)**: 1 replica, node:22-slim, port 3000
- **Service (backend)**: ClusterIP type, port 8000
- **Service (frontend)**: NodePort type, port 3000, nodePort 30000
- **Secret**: DATABASE_URL, JWT_SECRET, OPENAI_API_KEY

### API Contracts: Helm Values

See `contracts/helm-values.md` for complete value schema.

**Required Values (--set)**:
```yaml
secrets.databaseUrl: "postgresql://..."   # Required
secrets.jwtSecret: "your-jwt-secret"      # Required
secrets.openaiApiKey: "sk-..."            # Required for AI features
```

**Optional Values**:
```yaml
backend.replicaCount: 1                   # Default: 1
frontend.replicaCount: 1                  # Default: 1
backend.image.pullPolicy: Never           # Required for local images
frontend.image.pullPolicy: Never          # Required for local images
```

### Quickstart Guide

See `quickstart.md` for complete deployment guide.

**Quick Deploy Commands**:
```bash
# 1. Build images
docker build -t todo-backend:latest ./backend
docker build -t todo-frontend:latest ./frontend

# 2. Create namespace
kubectl create namespace todo-app

# 3. Deploy with Helm
helm install todo-app ./helm/todo-app \
  --namespace todo-app \
  --set secrets.databaseUrl="$DATABASE_URL" \
  --set secrets.jwtSecret="$JWT_SECRET" \
  --set secrets.openaiApiKey="$OPENAI_API_KEY" \
  --set backend.image.pullPolicy=Never \
  --set frontend.image.pullPolicy=Never

# 4. Access application
kubectl port-forward svc/todo-app-frontend 3000:3000 -n todo-app
```

## Deployment Validation Checklist

- [ ] `docker build ./backend` succeeds
- [ ] `docker build ./frontend` succeeds
- [ ] `helm lint ./helm/todo-app` passes
- [ ] `helm install` creates pods
- [ ] Backend pod reaches Ready state
- [ ] Frontend pod reaches Ready state
- [ ] Application accessible via port-forward
- [ ] Health endpoints respond
- [ ] `helm upgrade` performs rolling update
- [ ] `helm rollback` restores previous version

## Risk Analysis

| Risk | Impact | Mitigation |
|------|--------|------------|
| Kubernetes not running | Deploy fails | Check with `kubectl cluster-info` first |
| Image build fails | Deploy blocked | Validate Dockerfiles work standalone |
| Database unreachable | App unhealthy | Verify DATABASE_URL connectivity first |
| Resource limits too low | Pod killed | Monitor with `kubectl top pods` |

## Next Steps

1. Run `/sp.tasks` to generate implementation tasks
2. Execute tasks to validate/enhance existing infrastructure
3. Create deployment automation script
4. Update documentation with troubleshooting guide

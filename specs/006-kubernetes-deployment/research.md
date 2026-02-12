# Research: Kubernetes Deployment

**Feature**: 006-kubernetes-deployment
**Date**: 2026-02-08

## Summary

This research documents the analysis of existing infrastructure and decisions made for the Kubernetes deployment phase.

## Existing Infrastructure Analysis

### Decision: Use Existing Dockerfiles and Helm Charts

**Rationale**: The repository already contains well-structured Dockerfiles and Helm charts that pass all constitution checks.

**Evidence**:
- `backend/Dockerfile`: Multi-stage build, slim base image, non-root user
- `frontend/Dockerfile`: Multi-stage build, standalone Next.js output
- `helm/todo-app/`: Complete chart with deployments, services, secrets

**Alternatives Considered**:
| Alternative | Why Rejected |
|-------------|--------------|
| Create new charts | Existing charts are complete and well-documented |
| Use Kustomize | Helm already implemented, more feature-rich for this use case |
| Use Docker Compose | Doesn't provide Kubernetes-native features (probes, scaling) |

---

## Local Kubernetes Environment

### Decision: Docker Desktop Kubernetes (Primary) with Minikube Fallback

**Rationale**: Docker Desktop Kubernetes is the simplest option for developers already using Docker. It's enabled with a single checkbox in Docker Desktop settings.

**Comparison**:
| Option | Pros | Cons |
|--------|------|------|
| Docker Desktop K8s | Simplest setup, integrated with Docker | Windows/Mac only, resource usage |
| Minikube | Cross-platform, configurable | Requires separate install, more setup |
| Kind | Fast, uses containers | Less intuitive, limited documentation |
| K3s | Lightweight | Requires Linux or WSL2, not Mac-native |

**Decision**: Support both Docker Desktop K8s and Minikube. Documentation prioritizes Docker Desktop K8s.

---

## Image Build Strategy

### Decision: Local Docker Build with imagePullPolicy: Never

**Rationale**: Building images locally and using `imagePullPolicy: Never` is the simplest approach for single-developer local development.

**Alternatives Considered**:
| Alternative | Why Rejected |
|-------------|--------------|
| Local Docker registry | Adds complexity (running registry container) |
| Minikube docker-env | Only works with Minikube, not portable |
| Push to Docker Hub | Requires account, adds network latency |

**Implementation**:
```bash
# Build images
docker build -t todo-backend:latest ./backend
docker build -t todo-frontend:latest ./frontend

# Deploy with Never pull policy
helm install todo-app ./helm/todo-app \
  --set backend.image.pullPolicy=Never \
  --set frontend.image.pullPolicy=Never
```

---

## Secret Management

### Decision: Pass Secrets via Helm --set Flags

**Rationale**: Simple, secure for local development, and ensures secrets are never committed to version control.

**Alternatives Considered**:
| Alternative | Why Rejected |
|-------------|--------------|
| External Secrets Operator | Overkill for local development |
| Sealed Secrets | Requires additional tooling and setup |
| .env file with envsubst | Files could accidentally be committed |
| Values file with secrets | Would require gitignoring, easy to miss |

**Required Secrets**:
| Secret | Description | Required |
|--------|-------------|----------|
| `secrets.databaseUrl` | Neon PostgreSQL connection string | Yes |
| `secrets.jwtSecret` | JWT signing secret | Yes |
| `secrets.openaiApiKey` | OpenAI API key | Yes (for AI features) |

---

## Health Check Strategy

### Decision: HTTP Probes for Both Services

**Rationale**: Both services expose HTTP endpoints suitable for Kubernetes probes.

**Implementation**:
| Service | Endpoint | Probe Type |
|---------|----------|------------|
| Backend | `/health` | HTTP GET, port 8000 |
| Frontend | `/` | HTTP GET, port 3000 |

**Probe Configuration**:
```yaml
livenessProbe:
  httpGet:
    path: /health  # or / for frontend
    port: 8000     # or 3000 for frontend
  initialDelaySeconds: 10
  periodSeconds: 30
  timeoutSeconds: 5
  failureThreshold: 3

readinessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 5
  periodSeconds: 10
  timeoutSeconds: 5
  failureThreshold: 3
```

---

## Resource Allocation

### Decision: Conservative Defaults with Override Capability

**Rationale**: Start with conservative resource limits that work on most developer machines, allow override via values.

**Default Resources**:
| Service | CPU Request | CPU Limit | Memory Request | Memory Limit |
|---------|-------------|-----------|----------------|--------------|
| Backend | 100m | 500m | 128Mi | 512Mi |
| Frontend | 100m | 300m | 128Mi | 256Mi |

**Override Example**:
```bash
helm install todo-app ./helm/todo-app \
  --set backend.resources.limits.memory=1Gi \
  --set backend.resources.limits.cpu=1
```

---

## Networking Strategy

### Decision: ClusterIP for Backend, NodePort for Frontend

**Rationale**:
- Backend only needs internal access (frontend proxies to it)
- Frontend needs external access for browser connections
- NodePort is simpler than LoadBalancer for local development

**Port Assignments**:
| Service | Type | Port | NodePort | Access |
|---------|------|------|----------|--------|
| Backend | ClusterIP | 8000 | N/A | Internal only |
| Frontend | NodePort | 3000 | 30000 | `http://localhost:30000` |

**Alternative Access** (port-forward):
```bash
kubectl port-forward svc/todo-app-frontend 3000:3000 -n todo-app
```

---

## Conclusion

All research questions have been resolved. The existing infrastructure is well-suited for the deployment requirements. Key decisions:

1. **Use existing Dockerfiles and Helm charts** - Already complete and compliant
2. **Support Docker Desktop K8s and Minikube** - Cover most developer environments
3. **Build locally with imagePullPolicy: Never** - Simplest for local dev
4. **Pass secrets via --set flags** - Secure, no files to commit
5. **HTTP probes for health checks** - Both services support HTTP endpoints
6. **Conservative resource defaults** - Work on most machines, overridable
7. **NodePort for frontend access** - Simple external access without LoadBalancer

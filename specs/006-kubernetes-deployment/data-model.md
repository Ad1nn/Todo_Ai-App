# Data Model: Kubernetes Resources

**Feature**: 006-kubernetes-deployment
**Date**: 2026-02-08

## Overview

This document defines the Kubernetes resources deployed by the Todo application Helm chart.

## Resource Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                        NAMESPACE: todo-app                          │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                        SECRET                                │   │
│  │  Name: todo-app-secrets                                     │   │
│  │  Data: DATABASE_URL, JWT_SECRET, OPENAI_API_KEY            │   │
│  └─────────────────────────────────────────────────────────────┘   │
│              │                              │                        │
│              ▼                              ▼                        │
│  ┌─────────────────────┐      ┌─────────────────────┐              │
│  │     DEPLOYMENT      │      │     DEPLOYMENT      │              │
│  │  todo-app-backend   │      │  todo-app-frontend  │              │
│  │  ┌───────────────┐  │      │  ┌───────────────┐  │              │
│  │  │     POD       │  │      │  │     POD       │  │              │
│  │  │ todo-backend  │  │      │  │ todo-frontend │  │              │
│  │  │   :8000       │  │      │  │   :3000       │  │              │
│  │  └───────────────┘  │      │  └───────────────┘  │              │
│  └─────────────────────┘      └─────────────────────┘              │
│              │                              │                        │
│              ▼                              ▼                        │
│  ┌─────────────────────┐      ┌─────────────────────┐              │
│  │      SERVICE        │      │      SERVICE        │              │
│  │  todo-app-backend   │      │  todo-app-frontend  │              │
│  │  Type: ClusterIP    │      │  Type: NodePort     │              │
│  │  Port: 8000         │      │  Port: 3000         │              │
│  │  (internal only)    │      │  NodePort: 30000    │              │
│  └─────────────────────┘      └─────────────────────┘              │
│                                             │                        │
└─────────────────────────────────────────────│────────────────────────┘
                                              │
                                              ▼
                                    ┌─────────────────┐
                                    │    EXTERNAL     │
                                    │  localhost:30000│
                                    │  (browser)      │
                                    └─────────────────┘
```

## Resource Definitions

### 1. Namespace

| Field | Value |
|-------|-------|
| Name | `todo-app` |
| Purpose | Isolate Todo application resources |

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: todo-app
```

---

### 2. Secret

| Field | Value |
|-------|-------|
| Name | `todo-app-secrets` |
| Type | Opaque |

| Key | Description | Required |
|-----|-------------|----------|
| `DATABASE_URL` | PostgreSQL connection string | Yes |
| `JWT_SECRET` | JWT signing secret | Yes |
| `OPENAI_API_KEY` | OpenAI API key | Yes |

**Notes**:
- Values are base64 encoded by Kubernetes
- Passed via `--set secrets.*` flags at install time
- Never committed to version control

---

### 3. Backend Deployment

| Field | Value |
|-------|-------|
| Name | `todo-app-backend` |
| Replicas | 1 (configurable) |
| Image | `todo-backend:latest` |
| Port | 8000 |

**Container Spec**:
| Field | Value |
|-------|-------|
| Image Pull Policy | Never (local builds) |
| Security Context | Non-root (UID 1000) |
| Liveness Probe | GET /health:8000 |
| Readiness Probe | GET /health:8000 |

**Resources**:
| Type | CPU | Memory |
|------|-----|--------|
| Requests | 100m | 128Mi |
| Limits | 500m | 512Mi |

**Environment Variables**:
| Variable | Source |
|----------|--------|
| `DATABASE_URL` | Secret: todo-app-secrets |
| `JWT_SECRET` | Secret: todo-app-secrets |
| `OPENAI_API_KEY` | Secret: todo-app-secrets |
| `JWT_ALGORITHM` | ConfigMap (or inline: HS256) |

---

### 4. Backend Service

| Field | Value |
|-------|-------|
| Name | `todo-app-backend` |
| Type | ClusterIP |
| Port | 8000 |
| Target Port | 8000 |
| Selector | `app: todo-app-backend` |

**Notes**:
- ClusterIP = internal access only
- Frontend connects to `todo-app-backend:8000`

---

### 5. Frontend Deployment

| Field | Value |
|-------|-------|
| Name | `todo-app-frontend` |
| Replicas | 1 (configurable) |
| Image | `todo-frontend:latest` |
| Port | 3000 |

**Container Spec**:
| Field | Value |
|-------|-------|
| Image Pull Policy | Never (local builds) |
| Security Context | Non-root (UID 1001) |
| Liveness Probe | GET /:3000 |
| Readiness Probe | GET /:3000 |

**Resources**:
| Type | CPU | Memory |
|------|-----|--------|
| Requests | 100m | 128Mi |
| Limits | 300m | 256Mi |

**Environment Variables**:
| Variable | Value |
|----------|-------|
| `NODE_ENV` | production |
| `NEXT_PUBLIC_API_URL` | http://todo-app-backend:8000/api/v1 |

---

### 6. Frontend Service

| Field | Value |
|-------|-------|
| Name | `todo-app-frontend` |
| Type | NodePort |
| Port | 3000 |
| Target Port | 3000 |
| Node Port | 30000 |
| Selector | `app: todo-app-frontend` |

**Notes**:
- NodePort = external access via node IP
- Access at `http://localhost:30000`
- Alternative: use `kubectl port-forward`

---

## Labels and Selectors

All resources use consistent labeling:

```yaml
labels:
  app.kubernetes.io/name: todo-app
  app.kubernetes.io/instance: {{ .Release.Name }}
  app.kubernetes.io/component: backend  # or frontend
  app.kubernetes.io/managed-by: Helm
```

## Resource Dependencies

```
Secret ──────┬──────► Backend Deployment ──────► Backend Service
             │
             └──────► Frontend Deployment ─────► Frontend Service
```

**Order of Creation**:
1. Secret (no dependencies)
2. Backend Deployment (depends on Secret)
3. Backend Service (depends on Deployment)
4. Frontend Deployment (depends on Secret, Backend Service for API URL)
5. Frontend Service (depends on Deployment)

## Scaling Considerations

| Service | Min Replicas | Max Replicas | Notes |
|---------|--------------|--------------|-------|
| Backend | 1 | 10 | Stateless, scales horizontally |
| Frontend | 1 | 5 | SSR, moderate memory usage |

**To scale**:
```bash
# Scale backend to 3 replicas
helm upgrade todo-app ./helm/todo-app \
  --set backend.replicaCount=3
```

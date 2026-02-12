# Helm Values Contract

**Feature**: 006-kubernetes-deployment
**Chart**: `helm/todo-app`
**Date**: 2026-02-08

## Overview

This document defines the required and optional Helm values for deploying the Todo application.

## Required Values (--set)

These values MUST be provided at install time:

| Value Path | Type | Description | Example |
|------------|------|-------------|---------|
| `secrets.databaseUrl` | string | PostgreSQL connection string | `postgresql://user:pass@host:5432/db` |
| `secrets.jwtSecret` | string | JWT signing secret (min 32 chars) | `your-super-secret-jwt-key-here` |
| `secrets.openaiApiKey` | string | OpenAI API key | `sk-...` |

**Example Install Command**:
```bash
helm install todo-app ./helm/todo-app \
  --namespace todo-app \
  --set secrets.databaseUrl="postgresql://user:pass@host:5432/db" \
  --set secrets.jwtSecret="your-super-secret-jwt-key-here" \
  --set secrets.openaiApiKey="sk-your-openai-key"
```

---

## Required for Local Development

These values are required when using locally-built images:

| Value Path | Type | Default | Required Value |
|------------|------|---------|----------------|
| `backend.image.pullPolicy` | string | IfNotPresent | `Never` |
| `frontend.image.pullPolicy` | string | IfNotPresent | `Never` |

**Example**:
```bash
helm install todo-app ./helm/todo-app \
  --set backend.image.pullPolicy=Never \
  --set frontend.image.pullPolicy=Never \
  # ... other values
```

---

## Optional Values

### Backend Configuration

| Value Path | Type | Default | Description |
|------------|------|---------|-------------|
| `backend.replicaCount` | integer | 1 | Number of backend pod replicas |
| `backend.image.repository` | string | todo-backend | Docker image repository |
| `backend.image.tag` | string | latest | Docker image tag |
| `backend.image.pullPolicy` | string | IfNotPresent | Image pull policy |
| `backend.service.type` | string | ClusterIP | Kubernetes service type |
| `backend.service.port` | integer | 8000 | Service port |
| `backend.resources.requests.cpu` | string | 100m | CPU request |
| `backend.resources.requests.memory` | string | 128Mi | Memory request |
| `backend.resources.limits.cpu` | string | 500m | CPU limit |
| `backend.resources.limits.memory` | string | 512Mi | Memory limit |
| `backend.env.JWT_ALGORITHM` | string | HS256 | JWT algorithm |

### Frontend Configuration

| Value Path | Type | Default | Description |
|------------|------|---------|-------------|
| `frontend.replicaCount` | integer | 1 | Number of frontend pod replicas |
| `frontend.image.repository` | string | todo-frontend | Docker image repository |
| `frontend.image.tag` | string | latest | Docker image tag |
| `frontend.image.pullPolicy` | string | IfNotPresent | Image pull policy |
| `frontend.service.type` | string | NodePort | Kubernetes service type |
| `frontend.service.port` | integer | 3000 | Service port |
| `frontend.service.nodePort` | integer | 30000 | NodePort (external access) |
| `frontend.resources.requests.cpu` | string | 100m | CPU request |
| `frontend.resources.requests.memory` | string | 128Mi | Memory request |
| `frontend.resources.limits.cpu` | string | 300m | CPU limit |
| `frontend.resources.limits.memory` | string | 256Mi | Memory limit |
| `frontend.env.NODE_ENV` | string | production | Node environment |

### Probe Configuration

| Value Path | Type | Default | Description |
|------------|------|---------|-------------|
| `backend.livenessProbe.initialDelaySeconds` | integer | 10 | Delay before first probe |
| `backend.livenessProbe.periodSeconds` | integer | 30 | Probe interval |
| `backend.livenessProbe.timeoutSeconds` | integer | 5 | Probe timeout |
| `backend.livenessProbe.failureThreshold` | integer | 3 | Failures before restart |
| `backend.readinessProbe.initialDelaySeconds` | integer | 5 | Delay before first probe |
| `backend.readinessProbe.periodSeconds` | integer | 10 | Probe interval |

---

## Value Override Examples

### Scale Backend to 3 Replicas
```bash
helm upgrade todo-app ./helm/todo-app \
  --set backend.replicaCount=3
```

### Increase Memory Limit
```bash
helm upgrade todo-app ./helm/todo-app \
  --set backend.resources.limits.memory=1Gi
```

### Use Custom Image Tag
```bash
helm upgrade todo-app ./helm/todo-app \
  --set backend.image.tag=v1.2.3 \
  --set frontend.image.tag=v1.2.3
```

### Use Values File
```bash
# Create custom-values.yaml
cat <<EOF > custom-values.yaml
backend:
  replicaCount: 3
  resources:
    limits:
      memory: 1Gi
frontend:
  replicaCount: 2
EOF

# Install with values file
helm install todo-app ./helm/todo-app \
  -f custom-values.yaml \
  --set secrets.databaseUrl="..." \
  --set secrets.jwtSecret="..." \
  --set secrets.openaiApiKey="..."
```

---

## Validation Rules

| Rule | Validation |
|------|------------|
| `secrets.databaseUrl` | Must start with `postgresql://` |
| `secrets.jwtSecret` | Minimum 32 characters |
| `secrets.openaiApiKey` | Must start with `sk-` |
| `replicaCount` | Integer >= 1 |
| `resources.requests.*` | Must be <= limits |
| `nodePort` | Range 30000-32767 |

---

## Environment Variable Mapping

Values are mapped to pod environment variables:

| Value Path | Pod Env Var | Service |
|------------|-------------|---------|
| `secrets.databaseUrl` | `DATABASE_URL` | Backend |
| `secrets.jwtSecret` | `JWT_SECRET` | Backend |
| `secrets.openaiApiKey` | `OPENAI_API_KEY` | Backend |
| `backend.env.JWT_ALGORITHM` | `JWT_ALGORITHM` | Backend |
| `frontend.env.NODE_ENV` | `NODE_ENV` | Frontend |

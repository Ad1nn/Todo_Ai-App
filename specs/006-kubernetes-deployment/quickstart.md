# Quickstart: Local Kubernetes Deployment

**Feature**: 006-kubernetes-deployment
**Date**: 2026-02-08

## Prerequisites

Before deploying, ensure you have:

- [ ] **Docker Desktop** with Kubernetes enabled (Settings → Kubernetes → Enable)
- [ ] **kubectl** CLI installed (`kubectl version`)
- [ ] **Helm 3.x** installed (`helm version`)
- [ ] **Database URL** for Neon PostgreSQL
- [ ] **JWT Secret** (32+ character string)
- [ ] **OpenAI API Key** (starts with `sk-`)

## Quick Deploy (5 minutes)

### Step 1: Verify Kubernetes is Running

```bash
kubectl cluster-info
kubectl get nodes
```

Expected output shows `docker-desktop` node in `Ready` state.

### Step 2: Build Docker Images

```bash
# From project root
docker build -t todo-backend:latest ./backend
docker build -t todo-frontend:latest ./frontend
```

Verify images:
```bash
docker images | grep todo
```

### Step 3: Create Namespace

```bash
kubectl create namespace todo-app
```

### Step 4: Deploy with Helm

```bash
# Set your secrets (replace with actual values)
export DATABASE_URL="postgresql://user:pass@host:5432/dbname"
export JWT_SECRET="your-super-secret-jwt-key-minimum-32-chars"
export OPENAI_API_KEY="sk-your-openai-api-key"

# Install
helm install todo-app ./helm/todo-app \
  --namespace todo-app \
  --set secrets.databaseUrl="$DATABASE_URL" \
  --set secrets.jwtSecret="$JWT_SECRET" \
  --set secrets.openaiApiKey="$OPENAI_API_KEY" \
  --set backend.image.pullPolicy=Never \
  --set frontend.image.pullPolicy=Never
```

### Step 5: Verify Deployment

```bash
# Watch pods start
kubectl get pods -n todo-app -w

# Wait for both pods to show Running and 1/1 Ready
# Press Ctrl+C to stop watching
```

### Step 6: Access Application

**Option A: NodePort (recommended)**
```bash
# Frontend is exposed on port 30000
open http://localhost:30000
```

**Option B: Port Forward**
```bash
kubectl port-forward svc/todo-app-frontend 3000:3000 -n todo-app
# Then open http://localhost:3000
```

---

## Common Commands

### View Resources
```bash
# All resources in namespace
kubectl get all -n todo-app

# Pod details
kubectl describe pod -l app=todo-app-backend -n todo-app

# Logs
kubectl logs -l app=todo-app-backend -n todo-app --tail=100
kubectl logs -l app=todo-app-frontend -n todo-app --tail=100
```

### Update Deployment
```bash
# Rebuild images with changes
docker build -t todo-backend:latest ./backend
docker build -t todo-frontend:latest ./frontend

# Restart pods to pick up new images
kubectl rollout restart deployment/todo-app-backend -n todo-app
kubectl rollout restart deployment/todo-app-frontend -n todo-app
```

### Scale Replicas
```bash
helm upgrade todo-app ./helm/todo-app \
  --namespace todo-app \
  --reuse-values \
  --set backend.replicaCount=3
```

### Rollback
```bash
# See history
helm history todo-app -n todo-app

# Rollback to previous version
helm rollback todo-app 1 -n todo-app
```

### Uninstall
```bash
helm uninstall todo-app -n todo-app
kubectl delete namespace todo-app
```

---

## Troubleshooting

### Pods Stuck in Pending
```bash
kubectl describe pod -n todo-app
```
**Common causes**: Insufficient resources, node not ready

### Pods in CrashLoopBackOff
```bash
kubectl logs <pod-name> -n todo-app --previous
```
**Common causes**: Missing environment variables, database connection failed

### ImagePullBackOff
```bash
kubectl describe pod -n todo-app
```
**Fix**: Ensure `imagePullPolicy: Never` is set for local images

### Cannot Access Application
```bash
# Check service
kubectl get svc -n todo-app

# Check endpoints
kubectl get endpoints -n todo-app
```

### Check Health Probes
```bash
# Backend health
kubectl exec -it deploy/todo-app-backend -n todo-app -- curl localhost:8000/health

# Frontend health
kubectl exec -it deploy/todo-app-frontend -n todo-app -- curl localhost:3000
```

---

## Environment Variables Reference

### Backend Pod
| Variable | Source | Description |
|----------|--------|-------------|
| `DATABASE_URL` | Secret | PostgreSQL connection |
| `JWT_SECRET` | Secret | JWT signing key |
| `OPENAI_API_KEY` | Secret | OpenAI API access |
| `JWT_ALGORITHM` | Values | Default: HS256 |

### Frontend Pod
| Variable | Source | Description |
|----------|--------|-------------|
| `NODE_ENV` | Values | production |
| `NEXT_PUBLIC_API_URL` | Values | Backend API URL |

---

## Next Steps

1. **Verify functionality**: Login, create tasks, test AI chat
2. **Monitor resources**: `kubectl top pods -n todo-app`
3. **Set up CI/CD**: Automate builds and deployments
4. **Scale for production**: Increase replicas, add HPA

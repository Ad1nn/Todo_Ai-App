# Quickstart: Advanced Cloud Deployment (Phase 5)

**Feature**: 007-advanced-cloud-deployment
**Date**: 2026-02-09

## Prerequisites

Before starting Phase 5, ensure you have:

- [ ] Phase 4 Kubernetes deployment working locally
- [ ] 005-task-enhancements completed (due_date, priority, category)
- [ ] Docker Desktop running with Kubernetes enabled
- [ ] DigitalOcean account created (for cloud deployment later)

## Local Development Setup

### 1. Install Dapr CLI

```bash
# Linux/WSL
wget -q https://raw.githubusercontent.com/dapr/cli/master/install/install.sh -O - | /bin/bash

# Verify installation
dapr version
```

### 2. Initialize Dapr Locally

```bash
# Initialize Dapr with default containers
dapr init

# Verify Dapr is running
dapr status
docker ps  # Should see dapr_placement, dapr_redis, dapr_zipkin
```

### 3. Start Redpanda (Kafka-compatible)

```bash
# Start Redpanda container
docker run -d \
  --name redpanda \
  -p 9092:9092 \
  -p 9644:9644 \
  redpandadata/redpanda:latest \
  redpanda start \
  --overprovisioned \
  --smp 1 \
  --memory 1G \
  --reserve-memory 0M \
  --node-id 0 \
  --check=false

# Verify Redpanda is running
docker logs redpanda
```

### 4. Create Kafka Topics

```bash
# Create topics using rpk (Redpanda CLI)
docker exec -it redpanda rpk topic create todo.reminders --partitions 1
docker exec -it redpanda rpk topic create todo.audit --partitions 1

# List topics
docker exec -it redpanda rpk topic list
```

### 5. Setup Dapr Components

```bash
# Create components directory
mkdir -p backend/dapr/components

# Copy component files (from contracts/dapr-components.yaml)
# Split into individual files:
# - backend/dapr/components/pubsub.yaml
# - backend/dapr/components/cron-reminder.yaml
# - backend/dapr/components/subscriptions.yaml
```

### 6. Run Backend with Dapr

```bash
cd backend

# Run with Dapr sidecar
dapr run \
  --app-id todo-backend \
  --app-port 8000 \
  --dapr-http-port 3500 \
  --resources-path ./dapr/components \
  -- uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

### 7. Run Frontend (Separate Terminal)

```bash
cd frontend
npm run dev
```

### 8. Verify Event Flow

```bash
# Publish a test event
curl -X POST http://localhost:3500/v1.0/publish/todo-pubsub/todo.audit \
  -H "Content-Type: application/json" \
  -d '{"event_type": "test", "message": "Hello from Dapr"}'

# Check backend logs for event receipt
```

---

## Database Migration

```bash
cd backend

# Create migration
alembic revision --autogenerate -m "Add Phase 5 models"

# Review and edit migration file if needed
# backend/alembic/versions/xxx_add_phase_5_models.py

# Run migration
alembic upgrade head
```

---

## Testing Events Locally

### Test Reminder Event

```bash
# Manually trigger reminder check (simulates cron)
curl -X POST http://localhost:8000/events/cron/reminder-check

# Check notifications table
curl http://localhost:8000/api/v1/notifications \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Test Audit Event

```bash
# Create a task (should trigger audit event)
curl -X POST http://localhost:8000/api/v1/tasks \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "Test Task", "recurrence_rule": "daily"}'

# Check audit log
curl http://localhost:8000/api/v1/audit \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

---

## Cloud Deployment (DigitalOcean)

### 1. Setup DigitalOcean CLI

```bash
# Install doctl
sudo snap install doctl

# Authenticate
doctl auth init
# Enter your API token

# Verify
doctl account get
```

### 2. Create DOKS Cluster

```bash
# Create cluster
doctl kubernetes cluster create todo-cluster \
  --region nyc1 \
  --size s-2vcpu-4gb \
  --count 2 \
  --auto-upgrade

# Configure kubectl
doctl kubernetes cluster kubeconfig save todo-cluster

# Verify
kubectl get nodes
```

### 3. Create Container Registry

```bash
# Create registry
doctl registry create todo-registry

# Login to registry
doctl registry login

# Tag and push images
docker tag todo-backend:latest registry.digitalocean.com/todo-registry/todo-backend:latest
docker push registry.digitalocean.com/todo-registry/todo-backend:latest

docker tag todo-frontend:latest registry.digitalocean.com/todo-registry/todo-frontend:latest
docker push registry.digitalocean.com/todo-registry/todo-frontend:latest
```

### 4. Install Dapr on DOKS

```bash
# Add Dapr Helm repo
helm repo add dapr https://dapr.github.io/helm-charts/
helm repo update

# Install Dapr
helm install dapr dapr/dapr \
  --namespace dapr-system \
  --create-namespace \
  --set global.ha.enabled=true

# Verify
kubectl get pods -n dapr-system
```

### 5. Deploy Application

```bash
# Create namespace
kubectl create namespace todo-app-production

# Deploy with Helm
helm upgrade --install todo-app ./helm/todo-app \
  --namespace todo-app-production \
  -f helm/todo-app/values-production.yaml \
  --set backend.image.repository=registry.digitalocean.com/todo-registry/todo-backend \
  --set frontend.image.repository=registry.digitalocean.com/todo-registry/todo-frontend \
  --set secrets.databaseUrl="$DATABASE_URL" \
  --set secrets.jwtSecret="$JWT_SECRET" \
  --set secrets.openaiApiKey="$OPENAI_API_KEY"

# Verify
kubectl get pods -n todo-app-production
kubectl get svc -n todo-app-production
```

### 6. Setup GitHub Actions

Required secrets in GitHub repository settings:

| Secret | Description |
|--------|-------------|
| `DIGITALOCEAN_ACCESS_TOKEN` | DigitalOcean API token |
| `REGISTRY_NAME` | todo-registry |
| `CLUSTER_NAME` | todo-cluster |
| `DATABASE_URL` | Neon PostgreSQL URL |
| `JWT_SECRET` | JWT signing secret |
| `OPENAI_API_KEY` | OpenAI API key |

---

## Troubleshooting

### Dapr Not Receiving Events

```bash
# Check Dapr sidecar logs
dapr logs --app-id todo-backend

# Verify pub/sub component
dapr components list

# Test pub/sub directly
dapr publish --publish-app-id todo-backend --pubsub todo-pubsub --topic todo.audit --data '{"test": true}'
```

### Redpanda Connection Issues

```bash
# Check Redpanda is running
docker ps | grep redpanda

# Check Redpanda logs
docker logs redpanda

# Test connectivity
docker exec -it redpanda rpk cluster info
```

### DOKS Deployment Issues

```bash
# Check pod status
kubectl describe pod -n todo-app-production -l app=todo-app-backend

# Check Dapr sidecar injection
kubectl get pods -n todo-app-production -o jsonpath='{.items[*].spec.containers[*].name}'

# View logs
kubectl logs -n todo-app-production -l app=todo-app-backend -c todo-backend
kubectl logs -n todo-app-production -l app=todo-app-backend -c daprd
```

---

## Next Steps

1. Run `/sp.tasks` to generate implementation tasks
2. Implement recurring tasks feature (backend + frontend)
3. Implement notification system (backend + frontend)
4. Setup Dapr event flow
5. Implement audit logging
6. Setup GitHub Actions CI/CD
7. Deploy to DigitalOcean DOKS

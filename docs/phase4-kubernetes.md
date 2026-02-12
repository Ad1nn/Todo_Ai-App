# Phase 4: Local Kubernetes Deployment

This document teaches the fundamental concepts of containerization and Kubernetes while guiding you through deploying the Todo app.

---

## Table of Contents
1. [Docker Fundamentals](#docker-fundamentals)
2. [Kubernetes Concepts](#kubernetes-concepts)
3. [Helm Package Manager](#helm-package-manager)
4. [Deployment Guide](#deployment-guide)
5. [AI-Assisted Kubernetes (kubectl-ai & kagent)](#ai-assisted-kubernetes)

---

## Docker Fundamentals

### What Problem Does Docker Solve?

**The "Works on My Machine" Problem:**
```
Developer A: "It works on my machine!"
Developer B: "It crashes on mine..."
Server:      "I can't even start it..."
```

Each environment has different:
- Operating system versions
- Installed libraries and packages
- Configuration files
- Environment variables

### The Docker Solution

Docker **containerizes** your application - packaging it with ALL its dependencies into a standardized unit.

```
┌─────────────────────────────────────────────────────────┐
│                     CONTAINER                            │
├─────────────────────────────────────────────────────────┤
│  Your Application (e.g., FastAPI backend)               │
│  + Python 3.13                                          │
│  + All pip packages (fastapi, uvicorn, sqlmodel...)     │
│  + Configuration files                                   │
│  + Runtime settings                                      │
└─────────────────────────────────────────────────────────┘
         ↓ Runs identically on ↓
    [Laptop]  [Server]  [Cloud]  [Anywhere]
```

### Key Docker Concepts

| Concept | Description | Analogy |
|---------|-------------|---------|
| **Image** | Read-only template with instructions | Recipe |
| **Container** | Running instance of an image | Cooked meal |
| **Dockerfile** | Text file with build instructions | Recipe card |
| **Layer** | Each instruction creates a cacheable layer | Recipe step |
| **Registry** | Storage for images (Docker Hub, ECR, etc.) | Recipe book |

### Dockerfile Anatomy

```dockerfile
# Base image - like starting with a pre-installed OS
FROM python:3.13-slim

# Set working directory inside container
WORKDIR /app

# Copy dependency file (for layer caching)
COPY requirements.txt .

# Install dependencies
RUN pip install -r requirements.txt

# Copy application code
COPY . .

# Document the port (doesn't actually publish it)
EXPOSE 8000

# Command to run when container starts
CMD ["uvicorn", "main:app", "--host", "0.0.0.0"]
```

### Multi-Stage Builds

Our Dockerfiles use **multi-stage builds** to keep images small:

```dockerfile
# Stage 1: Build (large, has dev tools)
FROM node:22 AS builder
RUN npm install && npm run build

# Stage 2: Runtime (small, production only)
FROM node:22-slim AS runner
COPY --from=builder /app/dist ./dist
CMD ["node", "dist/server.js"]
```

Benefits:
- Smaller final images (no build tools)
- Faster deployments
- Smaller attack surface (security)

---

## Kubernetes Concepts

### Why Kubernetes?

Docker alone has limitations:
- ❓ Container crashed → Who restarts it?
- ❓ Need 10 instances → How to manage them?
- ❓ Update without downtime → How?
- ❓ Containers talk to each other → Networking?

**Kubernetes** (K8s) orchestrates containers:
- ✅ **Self-heals**: Automatically restarts failed containers
- ✅ **Scales**: Run multiple replicas based on load
- ✅ **Updates**: Rolling updates with zero downtime
- ✅ **Networks**: Built-in service discovery and load balancing

### Kubernetes Architecture

```
┌─────────────────────── CLUSTER ───────────────────────────┐
│                                                            │
│  ┌──────────── Control Plane ─────────────┐               │
│  │ API Server | Scheduler | Controller    │               │
│  └────────────────────────────────────────┘               │
│                        ↓                                   │
│  ┌─ Node 1 ──────────────┐  ┌─ Node 2 ──────────────┐    │
│  │ ┌─Pod─┐ ┌─Pod─┐       │  │ ┌─Pod─┐ ┌─Pod─┐       │    │
│  │ │     │ │     │       │  │ │     │ │     │       │    │
│  │ └─────┘ └─────┘       │  │ └─────┘ └─────┘       │    │
│  └───────────────────────┘  └───────────────────────┘    │
└───────────────────────────────────────────────────────────┘
```

### Core Objects

#### 1. Pod
The smallest deployable unit. Contains one or more containers.

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: my-app
spec:
  containers:
    - name: app
      image: my-app:1.0
      ports:
        - containerPort: 8000
```

#### 2. Deployment
Manages pods, handles scaling and updates.

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-app
spec:
  replicas: 3  # Run 3 instances
  selector:
    matchLabels:
      app: my-app
  template:
    spec:
      containers:
        - name: app
          image: my-app:1.0
```

#### 3. Service
Stable networking endpoint for pods.

```yaml
apiVersion: v1
kind: Service
metadata:
  name: my-app
spec:
  type: ClusterIP  # Internal only
  ports:
    - port: 80
      targetPort: 8000
  selector:
    app: my-app
```

Service Types:
- **ClusterIP**: Internal only (default)
- **NodePort**: Expose on each node's IP
- **LoadBalancer**: External load balancer (cloud)

#### 4. ConfigMap & Secret
Store configuration and sensitive data.

```yaml
# ConfigMap - non-sensitive config
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
data:
  LOG_LEVEL: "info"

---
# Secret - sensitive data
apiVersion: v1
kind: Secret
metadata:
  name: app-secrets
stringData:
  API_KEY: "super-secret"
```

---

## Helm Package Manager

### What is Helm?

Helm is the **package manager for Kubernetes** (like npm for Node.js).

| Helm Concept | Description |
|--------------|-------------|
| **Chart** | Package of K8s manifests |
| **Values** | Configurable parameters |
| **Release** | Instance of a chart in a cluster |
| **Repository** | Collection of charts |

### Chart Structure

```
todo-app/
├── Chart.yaml        # Chart metadata
├── values.yaml       # Default configuration
├── templates/        # Kubernetes manifests
│   ├── _helpers.tpl  # Reusable functions
│   ├── deployment.yaml
│   ├── service.yaml
│   ├── secrets.yaml
│   └── NOTES.txt     # Post-install notes
└── .helmignore       # Files to ignore
```

### Template Syntax

Helm uses Go templates:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ include "my-app.fullname" . }}
spec:
  replicas: {{ .Values.replicaCount }}
  template:
    spec:
      containers:
        - name: app
          image: "{{ .Values.image.repository }}:{{ .Values.image.tag }}"
```

With `values.yaml`:
```yaml
replicaCount: 3
image:
  repository: my-app
  tag: "1.0.0"
```

---

## Deployment Guide

### Prerequisites

Install the following tools:

1. **Docker** - [docs.docker.com/get-docker](https://docs.docker.com/get-docker/)
2. **Minikube** - Local Kubernetes cluster
   ```bash
   # macOS
   brew install minikube

   # Windows
   choco install minikube

   # Linux
   curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
   sudo install minikube-linux-amd64 /usr/local/bin/minikube
   ```
3. **Helm** - Package manager
   ```bash
   # macOS
   brew install helm

   # Windows
   choco install kubernetes-helm
   ```
4. **kubectl** - Kubernetes CLI
   ```bash
   # Usually comes with Docker Desktop
   # Or install separately
   brew install kubectl
   ```

### Quick Deploy

Use the automated script:

```bash
# Make script executable
chmod +x scripts/deploy-minikube.sh

# Run deployment
./scripts/deploy-minikube.sh
```

### Manual Deployment Steps

#### Step 1: Start Minikube
```bash
# Start with adequate resources
minikube start --driver=docker --cpus=4 --memory=8192

# Verify it's running
minikube status
```

#### Step 2: Configure Docker for Minikube
```bash
# This makes docker commands build inside Minikube
eval $(minikube docker-env)
```

#### Step 3: Build Images
```bash
# Build backend
docker build -t todo-backend:latest ./backend

# Build frontend
docker build -t todo-frontend:latest ./frontend \
  --build-arg NEXT_PUBLIC_API_URL=http://todo-app-backend:8000/api/v1
```

#### Step 4: Deploy with Helm
```bash
# Create namespace
kubectl create namespace todo-app

# Deploy
helm install todo-app ./helm/todo-app \
  --namespace todo-app \
  --set secrets.databaseUrl="your-database-url" \
  --set secrets.jwtSecret="your-jwt-secret" \
  --set secrets.openaiApiKey="your-openai-key" \
  --set backend.image.pullPolicy=Never \
  --set frontend.image.pullPolicy=Never
```

#### Step 5: Access the Application
```bash
# Get frontend URL
minikube service todo-app-frontend --url -n todo-app

# Or port-forward
kubectl port-forward svc/todo-app-frontend 3000:3000 -n todo-app
```

### Useful Commands

```bash
# View pods
kubectl get pods -n todo-app

# View logs
kubectl logs -f <pod-name> -n todo-app

# Describe pod (debugging)
kubectl describe pod <pod-name> -n todo-app

# Execute into container
kubectl exec -it <pod-name> -n todo-app -- /bin/sh

# Scale deployment
kubectl scale deployment todo-app-backend --replicas=3 -n todo-app

# View Helm releases
helm list -n todo-app

# Upgrade deployment
helm upgrade todo-app ./helm/todo-app -n todo-app

# Rollback
helm rollback todo-app 1 -n todo-app

# Uninstall
helm uninstall todo-app -n todo-app
```

---

## AI-Assisted Kubernetes

Phase 4 includes AI-powered Kubernetes tools.

### kubectl-ai

Natural language to kubectl commands:

```bash
# Install
brew install kubectl-ai

# Usage
kubectl-ai "show me all pods that are not running"
kubectl-ai "create a deployment with nginx and 3 replicas"
kubectl-ai "why is my pod crashing?"
```

### kagent

AI agent for Kubernetes operations:

```bash
# Install
pip install kagent

# Usage
kagent "diagnose why the todo-app-backend pod keeps restarting"
kagent "help me scale the application based on CPU usage"
```

### Docker AI (Gordon)

AI assistant for Docker:

```bash
# Enabled in Docker Desktop
docker ai "optimize this Dockerfile"
docker ai "why is my build slow?"
```

---

## Troubleshooting

### Common Issues

1. **ImagePullBackOff**
   - Cause: Can't find the image
   - Fix: Ensure `imagePullPolicy: Never` for local images

2. **CrashLoopBackOff**
   - Cause: Container keeps crashing
   - Fix: Check logs with `kubectl logs <pod>`

3. **Pending Pods**
   - Cause: Not enough resources
   - Fix: Increase Minikube resources or reduce requests

4. **Service Not Accessible**
   - Fix: Use `minikube tunnel` for LoadBalancer services

### Debug Commands

```bash
# See all resources
kubectl get all -n todo-app

# Check events
kubectl get events -n todo-app --sort-by='.lastTimestamp'

# Describe problematic pod
kubectl describe pod <pod-name> -n todo-app

# Check node resources
kubectl top nodes
kubectl top pods -n todo-app
```

---

## Summary

| Concept | Tool | Purpose |
|---------|------|---------|
| Containerization | Docker | Package apps with dependencies |
| Orchestration | Kubernetes | Manage containers at scale |
| Package Management | Helm | Template and deploy K8s apps |
| Local K8s | Minikube | Run K8s on your laptop |
| AI Assistance | kubectl-ai, kagent | Natural language K8s |

🎉 You now have the foundations to deploy containerized applications to Kubernetes!

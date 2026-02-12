#!/bin/bash
# =============================================================================
# Minikube Deployment Script
# =============================================================================
#
# LEARNING NOTES:
# This script automates the deployment of the Todo app to Minikube.
#
# Prerequisites:
#   - Docker installed and running
#   - Minikube installed (brew install minikube / choco install minikube)
#   - Helm installed (brew install helm / choco install kubernetes-helm)
#   - kubectl installed (comes with Docker Desktop or install separately)
#
# Usage:
#   ./scripts/deploy-minikube.sh
#
# =============================================================================

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print functions
info() { echo -e "${BLUE}ℹ️  $1${NC}"; }
success() { echo -e "${GREEN}✅ $1${NC}"; }
warn() { echo -e "${YELLOW}⚠️  $1${NC}"; }
error() { echo -e "${RED}❌ $1${NC}"; exit 1; }

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "
╔═══════════════════════════════════════════════════════════════╗
║       🚀 Todo App - Minikube Deployment                       ║
╚═══════════════════════════════════════════════════════════════╝
"

# -----------------------------------------------------------------------------
# Step 1: Check Prerequisites
# -----------------------------------------------------------------------------
info "Checking prerequisites..."

check_command() {
    if ! command -v "$1" &> /dev/null; then
        error "$1 is not installed. Please install it first."
    else
        success "$1 is installed"
    fi
}

check_command docker
check_command minikube
check_command helm
check_command kubectl

# -----------------------------------------------------------------------------
# Step 2: Start Minikube (if not running)
# -----------------------------------------------------------------------------
info "Checking Minikube status..."

if minikube status | grep -q "Running"; then
    success "Minikube is already running"
else
    info "Starting Minikube..."
    minikube start --driver=docker --cpus=4 --memory=8192
    success "Minikube started"
fi

# -----------------------------------------------------------------------------
# Step 3: Configure Docker to use Minikube's Docker daemon
# -----------------------------------------------------------------------------
info "Configuring Docker to use Minikube's daemon..."

# This makes our docker commands build images inside Minikube
# So we don't need to push to a registry
eval $(minikube docker-env)
success "Docker configured for Minikube"

# -----------------------------------------------------------------------------
# Step 4: Build Docker Images
# -----------------------------------------------------------------------------
info "Building Docker images (this may take a few minutes)..."

cd "$PROJECT_ROOT"

info "Building backend image..."
docker build -t todo-backend:latest ./backend
success "Backend image built"

info "Building frontend image..."
docker build -t todo-frontend:latest ./frontend --build-arg NEXT_PUBLIC_API_URL=http://todo-app-backend:8000/api/v1
success "Frontend image built"

# -----------------------------------------------------------------------------
# Step 5: Load Environment Variables
# -----------------------------------------------------------------------------
info "Loading environment variables..."

if [ -f "$PROJECT_ROOT/backend/.env" ]; then
    export $(grep -v '^#' "$PROJECT_ROOT/backend/.env" | xargs)
    success "Environment variables loaded from backend/.env"
else
    warn "No backend/.env file found. You'll need to provide secrets manually."
fi

# -----------------------------------------------------------------------------
# Step 6: Deploy with Helm
# -----------------------------------------------------------------------------
info "Deploying with Helm..."

# Create namespace if it doesn't exist
kubectl create namespace todo-app --dry-run=client -o yaml | kubectl apply -f -

# Install or upgrade the Helm release
helm upgrade --install todo-app ./helm/todo-app \
    --namespace todo-app \
    --set secrets.databaseUrl="${DATABASE_URL:-}" \
    --set secrets.jwtSecret="${JWT_SECRET:-super-secret-jwt-key}" \
    --set secrets.openaiApiKey="${OPENAI_API_KEY:-}" \
    --set backend.image.pullPolicy=Never \
    --set frontend.image.pullPolicy=Never \
    --wait \
    --timeout 5m

success "Helm deployment complete!"

# -----------------------------------------------------------------------------
# Step 7: Wait for Pods to be Ready
# -----------------------------------------------------------------------------
info "Waiting for pods to be ready..."

kubectl wait --for=condition=ready pod \
    -l app.kubernetes.io/instance=todo-app \
    --namespace todo-app \
    --timeout=120s

success "All pods are ready!"

# -----------------------------------------------------------------------------
# Step 8: Show Access Information
# -----------------------------------------------------------------------------
echo "
╔═══════════════════════════════════════════════════════════════╗
║       🎉 Deployment Complete!                                  ║
╚═══════════════════════════════════════════════════════════════╝
"

# Get the URL
FRONTEND_URL=$(minikube service todo-app-frontend --url -n todo-app 2>/dev/null || echo "Run: minikube service todo-app-frontend --url -n todo-app")

echo -e "
${GREEN}Frontend URL:${NC} $FRONTEND_URL

${BLUE}Useful Commands:${NC}
  # View pods
  kubectl get pods -n todo-app

  # View logs
  kubectl logs -f -l app.kubernetes.io/component=backend -n todo-app
  kubectl logs -f -l app.kubernetes.io/component=frontend -n todo-app

  # Access backend API docs
  kubectl port-forward svc/todo-app-backend 8000:8000 -n todo-app
  # Then open: http://localhost:8000/docs

  # Open Minikube dashboard
  minikube dashboard

  # Stop Minikube (preserves state)
  minikube stop

  # Delete everything
  helm uninstall todo-app -n todo-app
  minikube delete
"

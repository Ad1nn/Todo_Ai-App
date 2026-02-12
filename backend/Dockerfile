# =============================================================================
# Backend Dockerfile - Python FastAPI Application
# =============================================================================
#
# LEARNING NOTES:
# - Multi-stage builds reduce final image size (dev dependencies not included)
# - We use 'uv' (fast Python package manager) instead of pip for speed
# - Each RUN command creates a new layer (combine related commands)
# - Order matters: put rarely-changing layers first for cache efficiency
#
# =============================================================================

# -----------------------------------------------------------------------------
# Stage 1: Builder - Install dependencies in an isolated environment
# -----------------------------------------------------------------------------
# Why slim? It's smaller than full Python image (fewer vulnerabilities, faster pulls)
# Why bookworm? It's Debian 12, a stable and well-supported base
FROM python:3.13-slim-bookworm AS builder

# Install uv - a fast Python package manager written in Rust
# This is 10-100x faster than pip for dependency resolution
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Set working directory inside the container
# All subsequent commands will run from this directory
WORKDIR /app

# Copy dependency files first (for layer caching)
# If these files don't change, Docker reuses the cached layer
# README.md is needed by hatchling for package metadata
COPY pyproject.toml uv.lock README.md ./

# Install dependencies into a virtual environment
# --frozen: Use exact versions from uv.lock (reproducible builds)
# --no-dev: Skip development dependencies (smaller production image)
RUN uv sync --frozen --no-dev

# Copy the application source code
# This layer changes frequently, so it's placed last
COPY src/ ./src/
COPY alembic/ ./alembic/
COPY alembic.ini ./

# -----------------------------------------------------------------------------
# Stage 2: Runtime - Minimal image with just what we need to run
# -----------------------------------------------------------------------------
FROM python:3.13-slim-bookworm AS runtime

# Security: Create non-root user to run the application
# This limits damage if the container is compromised
RUN groupadd --gid 1000 appgroup && \
    useradd --uid 1000 --gid 1000 --shell /bin/bash appuser

WORKDIR /app

# Copy the virtual environment from builder stage
# This contains all our installed packages
COPY --from=builder /app/.venv /app/.venv

# Copy application code from builder stage
COPY --from=builder /app/src ./src
COPY --from=builder /app/alembic ./alembic
COPY --from=builder /app/alembic.ini ./

# Set environment variables
# PATH: Ensure we use the virtual environment's Python
# PYTHONUNBUFFERED: Print output immediately (important for logs)
# PYTHONDONTWRITEBYTECODE: Don't create .pyc files (smaller image)
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Document the port this service uses
# NOTE: This doesn't actually publish the port, it's documentation
EXPOSE 8000

# Change ownership to non-root user
RUN chown -R appuser:appgroup /app

# Switch to non-root user
USER appuser

# Health check - Kubernetes/Docker can use this to verify container is healthy
# Every 30s, check if /health endpoint responds
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

# Command to run when container starts
# Using uvicorn directly (no shell) for proper signal handling
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]

"""FastAPI application entry point."""

import os
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.config import settings

# Set OpenAI API key in environment for the Agents SDK
# Must be done before importing chat router which uses the agents module
if settings.openai_api_key:
    os.environ["OPENAI_API_KEY"] = settings.openai_api_key

from src.api.audit import router as audit_router
from src.api.auth import router as auth_router
from src.api.chat import router as chat_router
from src.api.events import router as events_router
from src.api.notifications import router as notifications_router
from src.api.tasks import router as tasks_router


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan handler."""
    # Startup
    yield
    # Shutdown


app = FastAPI(
    title="Todo API",
    description="Full-stack web todo application API with AI chat interface",
    version="2.0.0",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include API routers
app.include_router(auth_router, prefix="/api/v1")
app.include_router(tasks_router, prefix="/api/v1")
app.include_router(notifications_router, prefix="/api/v1")
app.include_router(audit_router, prefix="/api/v1")
app.include_router(chat_router, prefix="/api")

# Dapr event handlers (no auth required - called by Dapr sidecar)
app.include_router(events_router)


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy"}

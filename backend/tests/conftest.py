"""Pytest fixtures for backend tests."""

import asyncio
from collections.abc import AsyncGenerator, Generator
from typing import Any
from uuid import uuid4

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel

from src.api.deps import get_db
from src.main import app
from src.models.task import Task
from src.models.user import User

# Use in-memory SQLite for tests
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def engine():
    """Create async engine for tests."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest.fixture
async def db_session(engine) -> AsyncGenerator[AsyncSession, None]:
    """Create database session for tests."""
    async_session_maker = sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    async with async_session_maker() as session:
        yield session
        await session.rollback()


@pytest.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Create test client with database override."""

    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

    app.dependency_overrides.clear()


@pytest.fixture
def sample_user_data() -> dict[str, Any]:
    """Sample user data for testing."""
    return {
        "email": f"test-{uuid4().hex[:8]}@example.com",
        "password": "securepassword123",
    }


@pytest.fixture
async def test_user(db_session: AsyncSession, sample_user_data: dict[str, Any]) -> User:
    """Create a test user in the database."""
    from src.services.auth_service import AuthService

    auth_service = AuthService(db_session)
    user = await auth_service.register(
        email=sample_user_data["email"],
        password=sample_user_data["password"],
    )
    return user


@pytest.fixture
def sample_task_data() -> dict[str, Any]:
    """Sample task data for testing."""
    return {
        "title": "Test Task",
        "description": "This is a test task description",
    }


@pytest.fixture
async def test_task(
    db_session: AsyncSession, test_user: User, sample_task_data: dict[str, Any]
) -> Task:
    """Create a test task in the database."""
    task = Task(
        user_id=test_user.id,
        title=sample_task_data["title"],
        description=sample_task_data["description"],
    )
    db_session.add(task)
    await db_session.commit()
    await db_session.refresh(task)
    return task


@pytest.fixture
async def auth_headers(client: AsyncClient, sample_user_data: dict[str, Any]) -> dict[str, str]:
    """Get authentication headers for a test user."""
    # Register the user
    await client.post("/api/v1/auth/register", json=sample_user_data)

    # Login to get token
    response = await client.post("/api/v1/auth/login", json=sample_user_data)
    token = response.json()["access_token"]

    return {"Authorization": f"Bearer {token}"}

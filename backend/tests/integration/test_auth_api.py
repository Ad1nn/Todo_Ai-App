"""Integration tests for auth API endpoints."""

from uuid import uuid4

import pytest


class TestRegisterEndpoint:
    """Tests for POST /api/v1/auth/register."""

    @pytest.mark.asyncio
    async def test_register_success(self, client):
        """Successful registration returns user data."""
        email = f"test-{uuid4().hex[:8]}@example.com"
        response = await client.post(
            "/api/v1/auth/register",
            json={"email": email, "password": "securepassword123"}
        )

        assert response.status_code == 201
        data = response.json()
        assert data["email"] == email
        assert "id" in data
        assert "password" not in data
        assert "password_hash" not in data

    @pytest.mark.asyncio
    async def test_register_duplicate_email(self, client):
        """Duplicate email registration returns 400."""
        email = f"test-{uuid4().hex[:8]}@example.com"

        # Register first time
        await client.post(
            "/api/v1/auth/register",
            json={"email": email, "password": "securepassword123"}
        )

        # Try to register again
        response = await client.post(
            "/api/v1/auth/register",
            json={"email": email, "password": "differentpassword"}
        )

        assert response.status_code == 400
        assert "already registered" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_register_invalid_email(self, client):
        """Invalid email format returns 422."""
        response = await client.post(
            "/api/v1/auth/register",
            json={"email": "not-an-email", "password": "securepassword123"}
        )

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_register_short_password(self, client):
        """Password less than 8 characters returns 422."""
        response = await client.post(
            "/api/v1/auth/register",
            json={"email": "test@example.com", "password": "short"}
        )

        assert response.status_code == 422


class TestLoginEndpoint:
    """Tests for POST /api/v1/auth/login."""

    @pytest.mark.asyncio
    async def test_login_success(self, client):
        """Successful login returns access token."""
        email = f"test-{uuid4().hex[:8]}@example.com"
        password = "securepassword123"

        # Register first
        await client.post(
            "/api/v1/auth/register",
            json={"email": email, "password": password}
        )

        # Login
        response = await client.post(
            "/api/v1/auth/login",
            json={"email": email, "password": password}
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    @pytest.mark.asyncio
    async def test_login_invalid_email(self, client):
        """Login with non-existent email returns 401."""
        response = await client.post(
            "/api/v1/auth/login",
            json={"email": "nonexistent@example.com", "password": "anypassword"}
        )

        assert response.status_code == 401
        assert "invalid" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_login_invalid_password(self, client):
        """Login with wrong password returns 401."""
        email = f"test-{uuid4().hex[:8]}@example.com"

        # Register
        await client.post(
            "/api/v1/auth/register",
            json={"email": email, "password": "correctpassword"}
        )

        # Login with wrong password
        response = await client.post(
            "/api/v1/auth/login",
            json={"email": email, "password": "wrongpassword"}
        )

        assert response.status_code == 401


class TestMeEndpoint:
    """Tests for GET /api/v1/auth/me."""

    @pytest.mark.asyncio
    async def test_me_authenticated(self, client):
        """Authenticated request returns current user."""
        email = f"test-{uuid4().hex[:8]}@example.com"
        password = "securepassword123"

        # Register and login
        await client.post(
            "/api/v1/auth/register",
            json={"email": email, "password": password}
        )
        login_response = await client.post(
            "/api/v1/auth/login",
            json={"email": email, "password": password}
        )
        token = login_response.json()["access_token"]

        # Get current user
        response = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["email"] == email
        assert "id" in data

    @pytest.mark.asyncio
    async def test_me_unauthenticated(self, client):
        """Unauthenticated request returns 401."""
        response = await client.get("/api/v1/auth/me")

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_me_invalid_token(self, client):
        """Invalid token returns 401."""
        response = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer invalid-token"}
        )

        assert response.status_code == 401


class TestLogoutEndpoint:
    """Tests for POST /api/v1/auth/logout."""

    @pytest.mark.asyncio
    async def test_logout_success(self, client):
        """Logout returns success message."""
        email = f"test-{uuid4().hex[:8]}@example.com"
        password = "securepassword123"

        # Register and login
        await client.post(
            "/api/v1/auth/register",
            json={"email": email, "password": password}
        )
        login_response = await client.post(
            "/api/v1/auth/login",
            json={"email": email, "password": password}
        )
        token = login_response.json()["access_token"]

        # Logout
        response = await client.post(
            "/api/v1/auth/logout",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        assert "logged out" in response.json()["message"].lower()

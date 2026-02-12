"""Unit tests for AuthService."""

from unittest.mock import patch
from uuid import uuid4

import pytest

from src.services.auth_service import AuthService


class TestAuthServiceHashPassword:
    """Tests for password hashing."""

    def test_hash_password_returns_different_value(self):
        """Hash should differ from original password."""
        password = "testpassword123"
        hashed = AuthService.hash_password(password)
        assert hashed != password

    def test_hash_password_is_consistent_verifiable(self):
        """Hashed password should be verifiable."""
        password = "testpassword123"
        hashed = AuthService.hash_password(password)
        assert AuthService.verify_password(password, hashed) is True

    def test_hash_password_different_salts(self):
        """Same password should produce different hashes (salted)."""
        password = "testpassword123"
        hash1 = AuthService.hash_password(password)
        hash2 = AuthService.hash_password(password)
        assert hash1 != hash2

    def test_verify_password_wrong_password(self):
        """Wrong password should not verify."""
        password = "testpassword123"
        wrong_password = "wrongpassword"
        hashed = AuthService.hash_password(password)
        assert AuthService.verify_password(wrong_password, hashed) is False


class TestAuthServiceJWT:
    """Tests for JWT token creation and validation."""

    def test_create_access_token_returns_string(self):
        """Token should be a non-empty string."""
        user_id = uuid4()
        token = AuthService.create_access_token(user_id)
        assert isinstance(token, str)
        assert len(token) > 0

    def test_create_access_token_contains_user_id(self):
        """Token payload should contain the user ID."""
        user_id = uuid4()
        token = AuthService.create_access_token(user_id)
        payload = AuthService.verify_token(token)
        assert payload is not None
        assert payload["sub"] == str(user_id)

    def test_verify_token_invalid_token(self):
        """Invalid token should return None."""
        invalid_token = "invalid.token.here"
        payload = AuthService.verify_token(invalid_token)
        assert payload is None

    def test_verify_token_expired_token(self):
        """Expired token should return None."""
        user_id = uuid4()
        # Create token with negative expiration (already expired)
        with patch('src.services.auth_service.settings') as mock_settings:
            mock_settings.jwt_secret = "test-secret"
            mock_settings.jwt_algorithm = "HS256"
            mock_settings.jwt_expiration_hours = -1  # Expired
            token = AuthService.create_access_token(user_id)
            payload = AuthService.verify_token(token)
            assert payload is None


class TestAuthServiceRegister:
    """Tests for user registration."""

    @pytest.mark.asyncio
    async def test_register_creates_user(self, db_session):
        """Register should create a new user."""
        auth_service = AuthService(db_session)
        email = f"test-{uuid4().hex[:8]}@example.com"
        password = "securepassword123"

        user = await auth_service.register(email=email, password=password)

        assert user is not None
        assert user.email == email
        assert user.password_hash != password
        assert user.id is not None

    @pytest.mark.asyncio
    async def test_register_duplicate_email_raises(self, db_session):
        """Register with duplicate email should raise error."""
        auth_service = AuthService(db_session)
        email = f"test-{uuid4().hex[:8]}@example.com"
        password = "securepassword123"

        await auth_service.register(email=email, password=password)

        with pytest.raises(ValueError, match="already registered"):
            await auth_service.register(email=email, password=password)


class TestAuthServiceAuthenticate:
    """Tests for user authentication."""

    @pytest.mark.asyncio
    async def test_authenticate_valid_credentials(self, db_session):
        """Authenticate with valid credentials should return user."""
        auth_service = AuthService(db_session)
        email = f"test-{uuid4().hex[:8]}@example.com"
        password = "securepassword123"

        await auth_service.register(email=email, password=password)
        user = await auth_service.authenticate(email=email, password=password)

        assert user is not None
        assert user.email == email

    @pytest.mark.asyncio
    async def test_authenticate_invalid_email(self, db_session):
        """Authenticate with invalid email should return None."""
        auth_service = AuthService(db_session)

        user = await auth_service.authenticate(
            email="nonexistent@example.com",
            password="somepassword"
        )

        assert user is None

    @pytest.mark.asyncio
    async def test_authenticate_invalid_password(self, db_session):
        """Authenticate with invalid password should return None."""
        auth_service = AuthService(db_session)
        email = f"test-{uuid4().hex[:8]}@example.com"
        password = "securepassword123"

        await auth_service.register(email=email, password=password)
        user = await auth_service.authenticate(email=email, password="wrongpassword")

        assert user is None

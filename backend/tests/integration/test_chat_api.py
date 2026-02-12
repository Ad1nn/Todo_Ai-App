"""Integration tests for chat API endpoints."""

from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.user import User
from src.services.auth_service import AuthService


@pytest.fixture
async def user_a(db_session: AsyncSession) -> User:
    """Create test user A."""
    auth_service = AuthService(db_session)
    user = await auth_service.register(
        email=f"user-a-{uuid4().hex[:8]}@example.com",
        password="password123",
    )
    return user


@pytest.fixture
async def user_b(db_session: AsyncSession) -> User:
    """Create test user B."""
    auth_service = AuthService(db_session)
    user = await auth_service.register(
        email=f"user-b-{uuid4().hex[:8]}@example.com",
        password="password123",
    )
    return user


@pytest.fixture
async def auth_headers_a(client: AsyncClient) -> dict[str, str]:
    """Get auth headers for user A."""
    user_data = {
        "email": f"user-a-{uuid4().hex[:8]}@example.com",
        "password": "password123",
    }
    await client.post("/api/v1/auth/register", json=user_data)
    response = await client.post("/api/v1/auth/login", json=user_data)
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
async def auth_headers_b(client: AsyncClient) -> dict[str, str]:
    """Get auth headers for user B."""
    user_data = {
        "email": f"user-b-{uuid4().hex[:8]}@example.com",
        "password": "password123",
    }
    await client.post("/api/v1/auth/register", json=user_data)
    response = await client.post("/api/v1/auth/login", json=user_data)
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def create_mock_agent_result(response_text: str, tool_calls: list[dict] | None = None):
    """Create a mock agent run result."""
    mock_result = MagicMock()
    mock_result.final_output = response_text
    mock_result.new_items = []

    if tool_calls:
        for tc in tool_calls:
            mock_item = MagicMock()
            mock_item.call = MagicMock()
            mock_item.call.name = tc.get("tool", "unknown")
            mock_item.call.arguments = tc.get("parameters", {})
            mock_item.output = tc.get("result", {})
            mock_result.new_items.append(mock_item)

    return mock_result


class TestChatEndpoint:
    """Tests for POST /api/chat/{user_id} endpoint."""

    @patch("src.services.chat_service.Runner.run")
    async def test_send_message_creates_conversation(
        self,
        mock_run: AsyncMock,
        client: AsyncClient,
        auth_headers_a: dict[str, str],
    ) -> None:
        """Test that sending a message creates a new conversation."""
        mock_run.return_value = create_mock_agent_result(
            "I've added 'Buy groceries' to your tasks."
        )

        # Get user ID from me endpoint
        me_response = await client.get("/api/v1/auth/me", headers=auth_headers_a)
        user_id = me_response.json()["id"]

        response = await client.post(
            f"/api/chat/{user_id}",
            json={"message": "Add a task to buy groceries"},
            headers=auth_headers_a,
        )

        assert response.status_code == 200
        data = response.json()
        assert "conversation_id" in data
        assert data["response"] == "I've added 'Buy groceries' to your tasks."
        assert isinstance(data["tool_calls"], list)

    @patch("src.services.chat_service.Runner.run")
    async def test_send_message_continues_conversation(
        self,
        mock_run: AsyncMock,
        client: AsyncClient,
        auth_headers_a: dict[str, str],
    ) -> None:
        """Test continuing an existing conversation."""
        mock_run.return_value = create_mock_agent_result("Task added!")

        me_response = await client.get("/api/v1/auth/me", headers=auth_headers_a)
        user_id = me_response.json()["id"]

        # First message creates conversation
        response1 = await client.post(
            f"/api/chat/{user_id}",
            json={"message": "Add task 1"},
            headers=auth_headers_a,
        )
        conversation_id = response1.json()["conversation_id"]

        # Second message continues conversation
        mock_run.return_value = create_mock_agent_result("Second task added!")
        response2 = await client.post(
            f"/api/chat/{user_id}",
            json={"message": "Add task 2", "conversation_id": conversation_id},
            headers=auth_headers_a,
        )

        assert response2.status_code == 200
        assert response2.json()["conversation_id"] == conversation_id

    async def test_send_message_unauthorized(self, client: AsyncClient) -> None:
        """Test that unauthorized requests are rejected."""
        fake_user_id = str(uuid4())
        response = await client.post(
            f"/api/chat/{fake_user_id}",
            json={"message": "Hello"},
        )

        assert response.status_code == 401

    @patch("src.services.chat_service.Runner.run")
    async def test_send_message_wrong_user_id(
        self,
        mock_run: AsyncMock,
        client: AsyncClient,
        auth_headers_a: dict[str, str],
    ) -> None:
        """Test that using wrong user_id in path is rejected."""
        wrong_user_id = str(uuid4())

        response = await client.post(
            f"/api/chat/{wrong_user_id}",
            json={"message": "Hello"},
            headers=auth_headers_a,
        )

        assert response.status_code == 401
        assert "does not match" in response.json()["detail"]

    async def test_send_empty_message_fails(
        self,
        client: AsyncClient,
        auth_headers_a: dict[str, str],
    ) -> None:
        """Test that empty message is rejected."""
        me_response = await client.get("/api/v1/auth/me", headers=auth_headers_a)
        user_id = me_response.json()["id"]

        response = await client.post(
            f"/api/chat/{user_id}",
            json={"message": ""},
            headers=auth_headers_a,
        )

        assert response.status_code == 422  # Validation error

    @patch("src.services.chat_service.Runner.run")
    async def test_conversation_not_found(
        self,
        mock_run: AsyncMock,
        client: AsyncClient,
        auth_headers_a: dict[str, str],
    ) -> None:
        """Test error when conversation_id doesn't exist."""
        me_response = await client.get("/api/v1/auth/me", headers=auth_headers_a)
        user_id = me_response.json()["id"]
        fake_conversation_id = str(uuid4())

        response = await client.post(
            f"/api/chat/{user_id}",
            json={"message": "Hello", "conversation_id": fake_conversation_id},
            headers=auth_headers_a,
        )

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()


class TestConversationIsolation:
    """Tests for user isolation in chat conversations."""

    @patch("src.services.chat_service.Runner.run")
    async def test_user_cannot_access_other_users_conversation(
        self,
        mock_run: AsyncMock,
        client: AsyncClient,
        auth_headers_a: dict[str, str],
        auth_headers_b: dict[str, str],
    ) -> None:
        """Test that user B cannot access user A's conversation."""
        mock_run.return_value = create_mock_agent_result("Task added!")

        # User A creates a conversation
        me_a = await client.get("/api/v1/auth/me", headers=auth_headers_a)
        user_a_id = me_a.json()["id"]

        response = await client.post(
            f"/api/chat/{user_a_id}",
            json={"message": "Add my secret task"},
            headers=auth_headers_a,
        )
        conversation_id = response.json()["conversation_id"]

        # User B tries to access that conversation
        me_b = await client.get("/api/v1/auth/me", headers=auth_headers_b)
        user_b_id = me_b.json()["id"]

        response = await client.post(
            f"/api/chat/{user_b_id}",
            json={"message": "Hello", "conversation_id": conversation_id},
            headers=auth_headers_b,
        )

        assert response.status_code == 404


class TestListConversations:
    """Tests for GET /api/chat/{user_id}/conversations endpoint."""

    @patch("src.services.chat_service.Runner.run")
    async def test_list_conversations(
        self,
        mock_run: AsyncMock,
        client: AsyncClient,
        auth_headers_a: dict[str, str],
    ) -> None:
        """Test listing user conversations."""
        mock_run.return_value = create_mock_agent_result("Done!")

        me = await client.get("/api/v1/auth/me", headers=auth_headers_a)
        user_id = me.json()["id"]

        # Create two conversations
        await client.post(
            f"/api/chat/{user_id}",
            json={"message": "First conversation"},
            headers=auth_headers_a,
        )
        await client.post(
            f"/api/chat/{user_id}",
            json={"message": "Second conversation"},
            headers=auth_headers_a,
        )

        response = await client.get(
            f"/api/chat/{user_id}/conversations",
            headers=auth_headers_a,
        )

        assert response.status_code == 200
        conversations = response.json()
        assert len(conversations) == 2
        assert all("id" in c for c in conversations)
        assert all("created_at" in c for c in conversations)

    async def test_list_conversations_empty(
        self,
        client: AsyncClient,
        auth_headers_a: dict[str, str],
    ) -> None:
        """Test listing conversations when none exist."""
        me = await client.get("/api/v1/auth/me", headers=auth_headers_a)
        user_id = me.json()["id"]

        response = await client.get(
            f"/api/chat/{user_id}/conversations",
            headers=auth_headers_a,
        )

        assert response.status_code == 200
        assert response.json() == []

    @patch("src.services.chat_service.Runner.run")
    async def test_list_conversations_user_isolation(
        self,
        mock_run: AsyncMock,
        client: AsyncClient,
        auth_headers_a: dict[str, str],
        auth_headers_b: dict[str, str],
    ) -> None:
        """Test that users only see their own conversations."""
        mock_run.return_value = create_mock_agent_result("Done!")

        me_a = await client.get("/api/v1/auth/me", headers=auth_headers_a)
        user_a_id = me_a.json()["id"]

        me_b = await client.get("/api/v1/auth/me", headers=auth_headers_b)
        user_b_id = me_b.json()["id"]

        # User A creates 2 conversations
        await client.post(
            f"/api/chat/{user_a_id}",
            json={"message": "User A conv 1"},
            headers=auth_headers_a,
        )
        await client.post(
            f"/api/chat/{user_a_id}",
            json={"message": "User A conv 2"},
            headers=auth_headers_a,
        )

        # User B creates 1 conversation
        await client.post(
            f"/api/chat/{user_b_id}",
            json={"message": "User B conv"},
            headers=auth_headers_b,
        )

        # Check each user sees only their own
        convs_a = await client.get(
            f"/api/chat/{user_a_id}/conversations",
            headers=auth_headers_a,
        )
        convs_b = await client.get(
            f"/api/chat/{user_b_id}/conversations",
            headers=auth_headers_b,
        )

        assert len(convs_a.json()) == 2
        assert len(convs_b.json()) == 1


class TestGetConversationMessages:
    """Tests for GET /api/chat/{user_id}/conversations/{conversation_id} endpoint."""

    @patch("src.services.chat_service.Runner.run")
    async def test_get_conversation_messages(
        self,
        mock_run: AsyncMock,
        client: AsyncClient,
        auth_headers_a: dict[str, str],
    ) -> None:
        """Test getting messages from a conversation."""
        mock_run.return_value = create_mock_agent_result("I added your task!")

        me = await client.get("/api/v1/auth/me", headers=auth_headers_a)
        user_id = me.json()["id"]

        # Create conversation with a message
        response = await client.post(
            f"/api/chat/{user_id}",
            json={"message": "Add a task"},
            headers=auth_headers_a,
        )
        conversation_id = response.json()["conversation_id"]

        # Get messages
        response = await client.get(
            f"/api/chat/{user_id}/conversations/{conversation_id}",
            headers=auth_headers_a,
        )

        assert response.status_code == 200
        messages = response.json()
        assert len(messages) == 2  # User message + assistant response
        assert messages[0]["role"] == "user"
        assert messages[0]["content"] == "Add a task"
        assert messages[1]["role"] == "assistant"

    async def test_get_messages_conversation_not_found(
        self,
        client: AsyncClient,
        auth_headers_a: dict[str, str],
    ) -> None:
        """Test error when conversation doesn't exist."""
        me = await client.get("/api/v1/auth/me", headers=auth_headers_a)
        user_id = me.json()["id"]
        fake_conversation_id = str(uuid4())

        response = await client.get(
            f"/api/chat/{user_id}/conversations/{fake_conversation_id}",
            headers=auth_headers_a,
        )

        assert response.status_code == 404

    @patch("src.services.chat_service.Runner.run")
    async def test_get_messages_user_isolation(
        self,
        mock_run: AsyncMock,
        client: AsyncClient,
        auth_headers_a: dict[str, str],
        auth_headers_b: dict[str, str],
    ) -> None:
        """Test that user B cannot get user A's conversation messages."""
        mock_run.return_value = create_mock_agent_result("Secret response!")

        # User A creates conversation
        me_a = await client.get("/api/v1/auth/me", headers=auth_headers_a)
        user_a_id = me_a.json()["id"]

        response = await client.post(
            f"/api/chat/{user_a_id}",
            json={"message": "My secret message"},
            headers=auth_headers_a,
        )
        conversation_id = response.json()["conversation_id"]

        # User B tries to get messages
        me_b = await client.get("/api/v1/auth/me", headers=auth_headers_b)
        user_b_id = me_b.json()["id"]

        response = await client.get(
            f"/api/chat/{user_b_id}/conversations/{conversation_id}",
            headers=auth_headers_b,
        )

        assert response.status_code == 404


class TestConversationPersistence:
    """Tests for conversation persistence across requests."""

    @patch("src.services.chat_service.Runner.run")
    async def test_messages_persisted_in_conversation(
        self,
        mock_run: AsyncMock,
        client: AsyncClient,
        auth_headers_a: dict[str, str],
    ) -> None:
        """Test that messages are persisted and can be retrieved."""
        me = await client.get("/api/v1/auth/me", headers=auth_headers_a)
        user_id = me.json()["id"]

        # Send multiple messages in same conversation
        mock_run.return_value = create_mock_agent_result("Response 1")
        response1 = await client.post(
            f"/api/chat/{user_id}",
            json={"message": "Message 1"},
            headers=auth_headers_a,
        )
        conversation_id = response1.json()["conversation_id"]

        mock_run.return_value = create_mock_agent_result("Response 2")
        await client.post(
            f"/api/chat/{user_id}",
            json={"message": "Message 2", "conversation_id": conversation_id},
            headers=auth_headers_a,
        )

        mock_run.return_value = create_mock_agent_result("Response 3")
        await client.post(
            f"/api/chat/{user_id}",
            json={"message": "Message 3", "conversation_id": conversation_id},
            headers=auth_headers_a,
        )

        # Get all messages
        response = await client.get(
            f"/api/chat/{user_id}/conversations/{conversation_id}",
            headers=auth_headers_a,
        )

        messages = response.json()
        assert len(messages) == 6  # 3 user messages + 3 assistant responses

        # Verify order (chronological)
        user_messages = [m for m in messages if m["role"] == "user"]
        assert user_messages[0]["content"] == "Message 1"
        assert user_messages[1]["content"] == "Message 2"
        assert user_messages[2]["content"] == "Message 3"

    @patch("src.services.chat_service.Runner.run")
    async def test_conversation_history_loaded_for_context(
        self,
        mock_run: AsyncMock,
        client: AsyncClient,
        auth_headers_a: dict[str, str],
    ) -> None:
        """Test that conversation history is passed to agent for context."""
        me = await client.get("/api/v1/auth/me", headers=auth_headers_a)
        user_id = me.json()["id"]

        # First message
        mock_run.return_value = create_mock_agent_result("I created task 'Buy milk'")
        response1 = await client.post(
            f"/api/chat/{user_id}",
            json={"message": "Add task to buy milk"},
            headers=auth_headers_a,
        )
        conversation_id = response1.json()["conversation_id"]

        # Capture the messages passed to runner on second call
        captured_messages = []

        def capture_messages(*args, **kwargs):
            captured_messages.extend(kwargs.get("messages", []))
            return create_mock_agent_result("Marked as done!")

        mock_run.side_effect = capture_messages

        # Second message should include history
        await client.post(
            f"/api/chat/{user_id}",
            json={"message": "Mark it as done", "conversation_id": conversation_id},
            headers=auth_headers_a,
        )

        # Verify history was passed
        assert len(captured_messages) >= 3  # At least: user1, assistant1, user2
        roles = [m["role"] for m in captured_messages]
        assert "user" in roles
        assert "assistant" in roles

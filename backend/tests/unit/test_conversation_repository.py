"""Unit tests for ConversationRepository with user isolation."""

from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.message import MessageRole
from src.models.user import User
from src.repositories.conversation_repository import ConversationRepository
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
def repo(db_session: AsyncSession) -> ConversationRepository:
    """Create conversation repository."""
    return ConversationRepository(db_session)


class TestCreateConversation:
    """Tests for conversation creation."""

    async def test_create_conversation_success(
        self, repo: ConversationRepository, user_a: User
    ) -> None:
        """Test creating a conversation."""
        conversation = await repo.create_conversation(user_a.id)

        assert conversation.id is not None
        assert conversation.user_id == user_a.id
        assert conversation.created_at is not None
        assert conversation.updated_at is not None

    async def test_create_multiple_conversations(
        self, repo: ConversationRepository, user_a: User
    ) -> None:
        """Test creating multiple conversations for same user."""
        conv1 = await repo.create_conversation(user_a.id)
        conv2 = await repo.create_conversation(user_a.id)

        assert conv1.id != conv2.id
        conversations = await repo.list_user_conversations(user_a.id)
        assert len(conversations) == 2


class TestGetConversation:
    """Tests for retrieving conversations."""

    async def test_get_conversation_success(
        self, repo: ConversationRepository, user_a: User
    ) -> None:
        """Test getting own conversation."""
        created = await repo.create_conversation(user_a.id)
        retrieved = await repo.get_conversation(created.id, user_a.id)

        assert retrieved is not None
        assert retrieved.id == created.id

    async def test_get_conversation_not_found(
        self, repo: ConversationRepository, user_a: User
    ) -> None:
        """Test getting non-existent conversation."""
        fake_id = uuid4()
        result = await repo.get_conversation(fake_id, user_a.id)

        assert result is None

    async def test_get_conversation_user_isolation(
        self, repo: ConversationRepository, user_a: User, user_b: User
    ) -> None:
        """Test that user B cannot access user A's conversation."""
        conv_a = await repo.create_conversation(user_a.id)

        # User A can access
        result_a = await repo.get_conversation(conv_a.id, user_a.id)
        assert result_a is not None

        # User B cannot access
        result_b = await repo.get_conversation(conv_a.id, user_b.id)
        assert result_b is None


class TestListUserConversations:
    """Tests for listing user conversations."""

    async def test_list_conversations_empty(
        self, repo: ConversationRepository, user_a: User
    ) -> None:
        """Test listing when no conversations exist."""
        conversations = await repo.list_user_conversations(user_a.id)
        assert conversations == []

    async def test_list_conversations_ordered_by_updated_at(
        self, repo: ConversationRepository, user_a: User
    ) -> None:
        """Test conversations are ordered by updated_at descending."""
        conv1 = await repo.create_conversation(user_a.id)
        conv2 = await repo.create_conversation(user_a.id)

        # Add message to conv1 to update its timestamp
        await repo.add_message(conv1.id, user_a.id, MessageRole.user, "Hello")

        conversations = await repo.list_user_conversations(user_a.id)

        # conv1 should be first (most recently updated)
        assert conversations[0].id == conv1.id
        assert conversations[1].id == conv2.id

    async def test_list_conversations_respects_limit(
        self, repo: ConversationRepository, user_a: User
    ) -> None:
        """Test that limit parameter works."""
        for _ in range(5):
            await repo.create_conversation(user_a.id)

        conversations = await repo.list_user_conversations(user_a.id, limit=3)
        assert len(conversations) == 3

    async def test_list_conversations_user_isolation(
        self, repo: ConversationRepository, user_a: User, user_b: User
    ) -> None:
        """Test that users only see their own conversations."""
        await repo.create_conversation(user_a.id)
        await repo.create_conversation(user_a.id)
        await repo.create_conversation(user_b.id)

        convs_a = await repo.list_user_conversations(user_a.id)
        convs_b = await repo.list_user_conversations(user_b.id)

        assert len(convs_a) == 2
        assert len(convs_b) == 1
        assert all(c.user_id == user_a.id for c in convs_a)
        assert all(c.user_id == user_b.id for c in convs_b)


class TestAddMessage:
    """Tests for adding messages to conversations."""

    async def test_add_message_success(
        self, repo: ConversationRepository, user_a: User
    ) -> None:
        """Test adding a message to conversation."""
        conv = await repo.create_conversation(user_a.id)
        message = await repo.add_message(
            conv.id, user_a.id, MessageRole.user, "Hello, assistant!"
        )

        assert message.id is not None
        assert message.conversation_id == conv.id
        assert message.user_id == user_a.id
        assert message.role == MessageRole.user
        assert message.content == "Hello, assistant!"
        assert message.tool_calls is None

    async def test_add_message_with_tool_calls(
        self, repo: ConversationRepository, user_a: User
    ) -> None:
        """Test adding a message with tool calls."""
        conv = await repo.create_conversation(user_a.id)
        tool_calls_json = '[{"tool": "add_task", "result": "success"}]'
        message = await repo.add_message(
            conv.id,
            user_a.id,
            MessageRole.assistant,
            "I added your task.",
            tool_calls=tool_calls_json,
        )

        assert message.tool_calls == tool_calls_json

    async def test_add_message_updates_conversation_timestamp(
        self, repo: ConversationRepository, user_a: User
    ) -> None:
        """Test that adding message updates conversation's updated_at."""
        conv = await repo.create_conversation(user_a.id)
        original_updated_at = conv.updated_at

        await repo.add_message(conv.id, user_a.id, MessageRole.user, "Hello!")

        # Refresh conversation
        updated_conv = await repo.get_conversation(conv.id, user_a.id)
        assert updated_conv.updated_at >= original_updated_at

    async def test_add_message_wrong_user_fails(
        self, repo: ConversationRepository, user_a: User, user_b: User
    ) -> None:
        """Test that user B cannot add message to user A's conversation."""
        conv_a = await repo.create_conversation(user_a.id)

        with pytest.raises(ValueError, match="access denied"):
            await repo.add_message(
                conv_a.id, user_b.id, MessageRole.user, "Hacked!"
            )

    async def test_add_message_nonexistent_conversation_fails(
        self, repo: ConversationRepository, user_a: User
    ) -> None:
        """Test that adding message to non-existent conversation fails."""
        fake_conv_id = uuid4()

        with pytest.raises(ValueError, match="not found"):
            await repo.add_message(
                fake_conv_id, user_a.id, MessageRole.user, "Hello"
            )


class TestGetConversationMessages:
    """Tests for retrieving conversation messages."""

    async def test_get_messages_empty(
        self, repo: ConversationRepository, user_a: User
    ) -> None:
        """Test getting messages from empty conversation."""
        conv = await repo.create_conversation(user_a.id)
        messages = await repo.get_conversation_messages(conv.id, user_a.id)
        assert messages == []

    async def test_get_messages_chronological_order(
        self, repo: ConversationRepository, user_a: User
    ) -> None:
        """Test that messages are returned in chronological order."""
        conv = await repo.create_conversation(user_a.id)

        await repo.add_message(conv.id, user_a.id, MessageRole.user, "First")
        await repo.add_message(conv.id, user_a.id, MessageRole.assistant, "Second")
        await repo.add_message(conv.id, user_a.id, MessageRole.user, "Third")

        messages = await repo.get_conversation_messages(conv.id, user_a.id)

        assert len(messages) == 3
        assert messages[0].content == "First"
        assert messages[1].content == "Second"
        assert messages[2].content == "Third"

    async def test_get_messages_respects_limit(
        self, repo: ConversationRepository, user_a: User
    ) -> None:
        """Test that limit parameter returns most recent messages."""
        conv = await repo.create_conversation(user_a.id)

        for i in range(10):
            await repo.add_message(conv.id, user_a.id, MessageRole.user, f"Message {i}")

        messages = await repo.get_conversation_messages(conv.id, user_a.id, limit=5)

        # Should get last 5 messages (5-9) in chronological order
        assert len(messages) == 5
        assert messages[0].content == "Message 5"
        assert messages[4].content == "Message 9"

    async def test_get_messages_user_isolation(
        self, repo: ConversationRepository, user_a: User, user_b: User
    ) -> None:
        """Test that user B cannot get user A's conversation messages."""
        conv_a = await repo.create_conversation(user_a.id)
        await repo.add_message(conv_a.id, user_a.id, MessageRole.user, "Secret message")

        # User B should get empty list (conversation doesn't exist for them)
        messages = await repo.get_conversation_messages(conv_a.id, user_b.id)
        assert messages == []


class TestDeleteConversation:
    """Tests for deleting conversations."""

    async def test_delete_conversation_success(
        self, repo: ConversationRepository, user_a: User
    ) -> None:
        """Test successful conversation deletion."""
        conv = await repo.create_conversation(user_a.id)
        await repo.add_message(conv.id, user_a.id, MessageRole.user, "Hello")

        result = await repo.delete_conversation(conv.id, user_a.id)

        assert result is True
        # Verify conversation is gone
        retrieved = await repo.get_conversation(conv.id, user_a.id)
        assert retrieved is None

    async def test_delete_conversation_not_found(
        self, repo: ConversationRepository, user_a: User
    ) -> None:
        """Test deleting non-existent conversation."""
        fake_id = uuid4()
        result = await repo.delete_conversation(fake_id, user_a.id)
        assert result is False

    async def test_delete_conversation_user_isolation(
        self, repo: ConversationRepository, user_a: User, user_b: User
    ) -> None:
        """Test that user B cannot delete user A's conversation."""
        conv_a = await repo.create_conversation(user_a.id)

        result = await repo.delete_conversation(conv_a.id, user_b.id)

        assert result is False
        # Verify conversation still exists for user A
        retrieved = await repo.get_conversation(conv_a.id, user_a.id)
        assert retrieved is not None

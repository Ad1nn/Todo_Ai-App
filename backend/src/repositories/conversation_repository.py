"""Conversation repository for database operations."""

from datetime import datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models.conversation import Conversation
from src.models.message import Message, MessageRole


class ConversationRepository:
    """Repository for Conversation and Message database operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_conversation(self, user_id: UUID) -> Conversation:
        """Create a new conversation for a user."""
        conversation = Conversation(user_id=user_id)
        self.session.add(conversation)
        await self.session.flush()
        await self.session.refresh(conversation)
        return conversation

    async def get_conversation(self, conversation_id: UUID, user_id: UUID) -> Conversation | None:
        """Get conversation by ID with user isolation check."""
        result = await self.session.execute(
            select(Conversation)
            .where(Conversation.id == conversation_id)
            .where(Conversation.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_conversation_with_messages(
        self, conversation_id: UUID, user_id: UUID
    ) -> Conversation | None:
        """Get conversation with messages loaded (eager loading)."""
        result = await self.session.execute(
            select(Conversation)
            .where(Conversation.id == conversation_id)
            .where(Conversation.user_id == user_id)
            .options(selectinload(Conversation.messages))
        )
        return result.scalar_one_or_none()

    async def list_user_conversations(self, user_id: UUID, limit: int = 10) -> list[Conversation]:
        """List user's most recent conversations."""
        result = await self.session.execute(
            select(Conversation)
            .where(Conversation.user_id == user_id)
            .order_by(Conversation.updated_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_conversation_messages(
        self, conversation_id: UUID, user_id: UUID, limit: int = 20
    ) -> list[Message]:
        """
        Get last N messages from conversation with user isolation.
        Returns messages in chronological order (oldest first).
        """
        result = await self.session.execute(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .where(Message.user_id == user_id)
            .order_by(Message.created_at.desc())
            .limit(limit)
        )
        messages = list(result.scalars().all())
        # Reverse to get chronological order
        return messages[::-1]

    async def add_message(
        self,
        conversation_id: UUID,
        user_id: UUID,
        role: MessageRole,
        content: str,
        tool_calls: str | None = None,
    ) -> Message:
        """Add a message to a conversation."""
        # Validate conversation ownership
        conversation = await self.get_conversation(conversation_id, user_id)
        if not conversation:
            raise ValueError("Conversation not found or access denied")

        message = Message(
            user_id=user_id,
            conversation_id=conversation_id,
            role=role,
            content=content,
            tool_calls=tool_calls,
        )
        self.session.add(message)

        # Update conversation's updated_at timestamp
        conversation.updated_at = datetime.utcnow()
        self.session.add(conversation)

        await self.session.flush()
        await self.session.refresh(message)
        return message

    async def delete_conversation(self, conversation_id: UUID, user_id: UUID) -> bool:
        """Delete a conversation (cascade deletes messages)."""
        conversation = await self.get_conversation(conversation_id, user_id)
        if not conversation:
            return False

        await self.session.delete(conversation)
        await self.session.flush()
        return True

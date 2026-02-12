"""Message model definitions for chat history."""

from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from src.models.conversation import Conversation
    from src.models.user import User


class MessageRole(str, Enum):
    """Message role enum for chat messages."""

    user = "user"
    assistant = "assistant"


class Message(SQLModel, table=True):
    """Message database model for individual chat messages."""

    __tablename__ = "message"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="user.id", index=True, nullable=False)
    conversation_id: UUID = Field(foreign_key="conversation.id", index=True, nullable=False)
    role: MessageRole = Field(nullable=False)
    content: str = Field(max_length=10000, nullable=False)
    tool_calls: str | None = Field(default=None, max_length=5000)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    # Relationships
    conversation: "Conversation" = Relationship(back_populates="messages")
    user: "User" = Relationship(back_populates="messages")


class MessageCreate(SQLModel):
    """Schema for creating a new message."""

    role: MessageRole
    content: str = Field(min_length=1, max_length=10000)
    tool_calls: str | None = None


class MessagePublic(SQLModel):
    """Public message data."""

    id: UUID
    role: MessageRole
    content: str
    tool_calls: str | None
    created_at: datetime

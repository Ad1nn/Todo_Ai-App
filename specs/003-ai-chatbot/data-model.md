# Data Model: AI-Powered Chatbot for Task Management

**Feature**: 003-ai-chatbot
**Date**: 2026-01-23
**Purpose**: Define database entities and relationships for Phase 3

## Overview

Phase 3 adds two new entities to support conversation persistence:
- **Conversation**: Chat session container
- **Message**: Individual messages within conversations

These entities integrate with existing Phase 2 entities:
- **User** (from Phase 2): Owns conversations and messages
- **Task** (from Phase 2): Referenced by MCP tools via agent

## Entity Definitions

### Conversation

**Purpose**: Represents a chat conversation session between user and AI assistant

**SQLModel Definition**:
```python
from sqlmodel import Field, SQLModel, Relationship
from datetime import datetime
from uuid import UUID, uuid4

class Conversation(SQLModel, table=True):
    """Chat conversation session."""

    __tablename__ = "conversations"

    # Primary Key
    id: UUID = Field(default_factory=uuid4, primary_key=True)

    # Foreign Keys
    user_id: UUID = Field(foreign_key="users.id", nullable=False, index=True)

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    # Relationships
    messages: list["Message"] = Relationship(back_populates="conversation", cascade_delete=True)
    user: "User" = Relationship(back_populates="conversations")
```

**Attributes**:
- `id` (UUID): Unique identifier, primary key
- `user_id` (UUID): Foreign key to users table (NOT NULL, INDEXED)
- `created_at` (datetime): Conversation creation timestamp (UTC)
- `updated_at` (datetime): Last message timestamp (UTC)

**Relationships**:
- **Has many** Messages (1:N) - cascade delete
- **Belongs to** User (N:1)

**Indexes**:
- Primary: `id`
- Foreign key: `user_id` (for user isolation queries)
- Composite: `(user_id, updated_at DESC)` for "recent conversations" query

**Validation Rules**:
- `user_id` must reference existing user
- `created_at` cannot be in the future
- `updated_at` >= `created_at`

**State Transitions**: None (conversations don't have state beyond active/deleted)

---

### Message

**Purpose**: Represents a single message (user or assistant) within a conversation

**SQLModel Definition**:
```python
from enum import Enum

class MessageRole(str, Enum):
    """Message role enum."""
    USER = "user"
    ASSISTANT = "assistant"

class Message(SQLModel, table=True):
    """Individual message in a conversation."""

    __tablename__ = "messages"

    # Primary Key
    id: UUID = Field(default_factory=uuid4, primary_key=True)

    # Foreign Keys
    user_id: UUID = Field(foreign_key="users.id", nullable=False, index=True)
    conversation_id: UUID = Field(foreign_key="conversations.id", nullable=False, index=True)

    # Message Data
    role: MessageRole = Field(nullable=False)
    content: str = Field(nullable=False, max_length=10000)

    # Metadata (optional)
    tool_calls: str | None = Field(default=None, max_length=5000)  # JSON array of tool calls

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    # Relationships
    conversation: Conversation = Relationship(back_populates="messages")
    user: "User" = Relationship(back_populates="messages")
```

**Attributes**:
- `id` (UUID): Unique identifier, primary key
- `user_id` (UUID): Foreign key to users table (NOT NULL, INDEXED) - for user isolation
- `conversation_id` (UUID): Foreign key to conversations table (NOT NULL, INDEXED)
- `role` (MessageRole enum): Either "user" or "assistant"
- `content` (str): Message text (max 10,000 characters)
- `tool_calls` (str | None): JSON array of tool calls made by agent (nullable, max 5,000 characters)
- `created_at` (datetime): Message timestamp (UTC)

**Relationships**:
- **Belongs to** Conversation (N:1)
- **Belongs to** User (N:1)

**Indexes**:
- Primary: `id`
- Foreign key: `user_id` (for user isolation queries)
- Foreign key: `conversation_id` (for conversation history queries)
- Composite: `(conversation_id, created_at ASC)` for chronological message retrieval

**Validation Rules**:
- `user_id` must reference existing user
- `conversation_id` must reference existing conversation
- `conversation.user_id` must match `message.user_id` (consistency check)
- `role` must be "user" or "assistant"
- `content` cannot be empty (min 1 character)
- `content` max 10,000 characters (prevents abuse)
- `tool_calls` is valid JSON array or NULL
- `created_at` cannot be in the future

**State Transitions**: None (messages are immutable once created)

---

### Updated User Entity (Phase 2)

**Changes**: Add relationships to Conversation and Message

```python
class User(SQLModel, table=True):
    """User entity (Phase 2 - updated for Phase 3)."""

    __tablename__ = "users"

    # ... existing Phase 2 fields ...

    # New Relationships (Phase 3)
    conversations: list[Conversation] = Relationship(back_populates="user", cascade_delete=True)
    messages: list[Message] = Relationship(back_populates="user", cascade_delete=True)
```

**Migration Impact**: No schema change, only code-level relationship addition

---

## Entity Relationships Diagram

```text
User (Phase 2)
├── id (UUID, PK)
├── email
├── name
└── tasks (1:N) [Phase 2]
    └── Conversation (1:N) [Phase 3]
        ├── id (UUID, PK)
        ├── user_id (FK → User.id)
        ├── created_at
        ├── updated_at
        └── messages (1:N)
            ├── Message
            │   ├── id (UUID, PK)
            │   ├── user_id (FK → User.id)
            │   ├── conversation_id (FK → Conversation.id)
            │   ├── role (enum: user|assistant)
            │   ├── content (TEXT)
            │   ├── tool_calls (JSON, nullable)
            │   └── created_at
            └── Message (continues...)

Task (Phase 2)
├── id (UUID, PK)
├── user_id (FK → User.id)
├── title
├── completed
└── ... [referenced by MCP tools, not directly by chat entities]
```

## Database Migration

### Migration: Add Conversation and Message Tables

**File**: `backend/alembic/versions/003_add_conversation_message.py`

**Up Migration**:
```sql
-- Create conversations table
CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Create index for user isolation
CREATE INDEX idx_conversations_user_id ON conversations(user_id);

-- Create index for recent conversations query
CREATE INDEX idx_conversations_user_updated ON conversations(user_id, updated_at DESC);

-- Create messages table
CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant')),
    content TEXT NOT NULL CHECK (LENGTH(content) > 0 AND LENGTH(content) <= 10000),
    tool_calls TEXT CHECK (tool_calls IS NULL OR LENGTH(tool_calls) <= 5000),
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Create indexes for message queries
CREATE INDEX idx_messages_user_id ON messages(user_id);
CREATE INDEX idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX idx_messages_conversation_created ON messages(conversation_id, created_at ASC);
```

**Down Migration**:
```sql
-- Drop tables in reverse order (messages first due to foreign keys)
DROP TABLE IF EXISTS messages;
DROP TABLE IF EXISTS conversations;
```

**Validation**:
- Foreign key constraints enforced
- Check constraints on role and content length
- Indexes created for performance
- Cascade delete ensures orphan cleanup

## Query Patterns

### 1. Get Recent Conversations for User

```python
def get_user_conversations(user_id: UUID, limit: int = 10) -> list[Conversation]:
    """Get user's most recent conversations."""
    return session.exec(
        select(Conversation)
        .where(Conversation.user_id == user_id)
        .order_by(Conversation.updated_at.desc())
        .limit(limit)
    ).all()
```

**Index Used**: `idx_conversations_user_updated (user_id, updated_at DESC)`

---

### 2. Get Conversation History (Last N Messages)

```python
def get_conversation_messages(
    user_id: UUID,
    conversation_id: UUID,
    limit: int = 20
) -> list[Message]:
    """
    Get last N messages from conversation.
    Enforces user isolation.
    """
    return session.exec(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .where(Message.user_id == user_id)  # User isolation
        .order_by(Message.created_at.desc())
        .limit(limit)
    ).all()[::-1]  # Reverse to chronological order
```

**Index Used**: `idx_messages_conversation_created (conversation_id, created_at ASC)`

**Performance**: O(log N) with index, returns last 20 messages in <10ms

---

### 3. Create New Message

```python
def create_message(
    user_id: UUID,
    conversation_id: UUID,
    role: MessageRole,
    content: str,
    tool_calls: str | None = None
) -> Message:
    """Create new message in conversation."""
    # Validate conversation ownership
    conv = session.get(Conversation, conversation_id)
    if not conv or conv.user_id != user_id:
        raise ValueError("Conversation not found or access denied")

    message = Message(
        user_id=user_id,
        conversation_id=conversation_id,
        role=role,
        content=content,
        tool_calls=tool_calls
    )
    session.add(message)

    # Update conversation updated_at
    conv.updated_at = datetime.utcnow()
    session.add(conv)

    session.commit()
    session.refresh(message)
    return message
```

**Validation**: Enforces user isolation and conversation ownership

---

### 4. Create New Conversation

```python
def create_conversation(user_id: UUID) -> Conversation:
    """Create new conversation for user."""
    conversation = Conversation(user_id=user_id)
    session.add(conversation)
    session.commit()
    session.refresh(conversation)
    return conversation
```

---

## Data Access Layer

### Repository Pattern (Constitution Principle V)

**File**: `backend/src/repositories/conversation_repository.py`

```python
from typing import Protocol
from uuid import UUID

class ConversationRepository(Protocol):
    """Interface for conversation data access."""

    def create_conversation(self, user_id: UUID) -> Conversation: ...
    def get_conversation(self, user_id: UUID, conversation_id: UUID) -> Conversation | None: ...
    def get_user_conversations(self, user_id: UUID, limit: int) -> list[Conversation]: ...
    def add_message(self, message: Message) -> Message: ...
    def get_conversation_messages(self, user_id: UUID, conversation_id: UUID, limit: int) -> list[Message]: ...
```

**Implementation**: `backend/src/repositories/sqlmodel_conversation_repository.py`

**Benefits**:
- Abstracts database operations
- Enables testing with mock repositories
- Centralizes user isolation enforcement
- Follows Phase 2 repository pattern

---

## Data Integrity Constraints

### Foreign Key Constraints
- `conversations.user_id` → `users.id` (CASCADE DELETE)
- `messages.user_id` → `users.id` (CASCADE DELETE)
- `messages.conversation_id` → `conversations.id` (CASCADE DELETE)

### Check Constraints
- `messages.role` IN ('user', 'assistant')
- `messages.content` LENGTH > 0 AND LENGTH <= 10000
- `messages.tool_calls` IS NULL OR LENGTH <= 5000

### User Isolation Enforcement
- All queries filter by `user_id`
- Repository layer validates ownership before operations
- Agent cannot access conversations from other users

### Cascade Delete Behavior
- Delete user → delete all conversations → delete all messages
- Delete conversation → delete all messages
- Ensures no orphaned data

---

## Performance Considerations

### Index Strategy
1. **User Isolation**: `user_id` indexed on both tables for fast filtering
2. **Recent Conversations**: Composite index `(user_id, updated_at DESC)` for dashboard
3. **Message History**: Composite index `(conversation_id, created_at ASC)` for chat loading

### Expected Query Performance
- Get conversation messages (20 msgs): <10ms with index
- Create message: <5ms (single INSERT + UPDATE)
- Get recent conversations: <10ms with composite index

### Scaling Considerations
- Message table will grow largest (estimate 100 msgs/user over time)
- Conversation table relatively small (estimate 5-10 conversations/user)
- Indexes maintain O(log N) performance up to millions of rows
- Consider partitioning messages table by `created_at` if >10M rows

---

## Testing Data Models

### Unit Tests (Constitution Principle IV)

```python
def test_conversation_creation():
    """Test conversation entity creation."""
    user = create_test_user()
    conv = Conversation(user_id=user.id)
    session.add(conv)
    session.commit()

    assert conv.id is not None
    assert conv.user_id == user.id
    assert conv.created_at is not None
    assert conv.updated_at == conv.created_at

def test_message_user_isolation():
    """Test that messages enforce user isolation."""
    user_a = create_test_user(email="a@test.com")
    user_b = create_test_user(email="b@test.com")
    conv = create_test_conversation(user_id=user_a.id)

    # Try to create message with wrong user_id
    with pytest.raises(IntegrityError):
        message = Message(
            user_id=user_b.id,  # Wrong user!
            conversation_id=conv.id,
            role=MessageRole.USER,
            content="Test"
        )
        session.add(message)
        session.commit()

def test_cascade_delete():
    """Test cascade delete behavior."""
    user = create_test_user()
    conv = create_test_conversation(user_id=user.id)
    msg = create_test_message(conversation_id=conv.id, user_id=user.id)

    # Delete conversation
    session.delete(conv)
    session.commit()

    # Message should be deleted (cascade)
    assert session.get(Message, msg.id) is None
```

---

## Summary

**New Entities**: Conversation, Message
**Updated Entities**: User (add relationships)
**Total Tables**: 2 new (conversations, messages)
**Indexes**: 5 total (3 single-column, 2 composite)
**Foreign Keys**: 3 total (all with CASCADE DELETE)
**Validation**: Role enum, content length, user isolation

All entities follow:
- ✅ Constitution Principle V (Modular Architecture with repository pattern)
- ✅ Constitution Principle III (Type hints and SQLModel)
- ✅ Constitution Principle VIII (User isolation via user_id)
- ✅ Phase 3 requirements (conversation persistence, stateless design)

Ready to proceed to API Contract generation.

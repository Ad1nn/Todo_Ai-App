# Research: AI-Powered Chatbot for Task Management

**Feature**: 003-ai-chatbot
**Date**: 2026-01-23
**Purpose**: Resolve technical decisions and clarifications for Phase 3 implementation

## Technology Stack Decisions

### Decision 1: OpenAI Agents SDK vs Custom Agent Implementation

**Decision**: Use OpenAI Agents SDK

**Rationale**:
- Official SDK provides built-in tool calling and conversation management
- Reduces development time by using pre-built agent orchestration
- Handles common patterns like retry logic, error handling, and streaming
- Well-documented with Python support (openai-agents-sdk package)
- Aligns with constitution Principle IX (AI Agent Design) requirements

**Alternatives Considered**:
- **Custom agent with OpenAI API directly**: More control but significantly more code to maintain; no built-in tool management
- **LangChain Agents**: More complex abstraction layer; overkill for our simple tool-calling needs
- **Anthropic Claude with tool use**: Different API, would require migration if we want to use OpenAI models

**Implementation Notes**:
- Install: `uv add openai-agents-sdk`
- Agent configuration will be in `backend/src/agent/config.py`
- Tools will be registered via MCP SDK integration

### Decision 2: MCP SDK Integration Pattern

**Decision**: Use Official MCP SDK (Model Context Protocol) with FastAPI integration

**Rationale**:
- MCP provides standardized way to expose tools to AI agents
- Official Python SDK (mcp package) has FastAPI adapter
- Enables tool discovery and schema validation
- Follows constitution Principle IX mandate for MCP Server as separate module
- Tools are independently testable with mock data

**Alternatives Considered**:
- **Direct function calling**: No standardization; harder to document and discover tools
- **OpenAPI-based tool exposure**: More verbose; MCP is purpose-built for AI agents
- **Custom protocol**: Reinventing the wheel; MCP is industry standard

**Implementation Notes**:
- Install: `uv add mcp`
- MCP server will be in `backend/src/mcp/` module
- Tools: `add_task`, `list_tasks`, `complete_task`, `delete_task`, `update_task`
- Each tool enforces `user_id` parameter for isolation
- Tools return structured responses: `{task_id, status, data}`

### Decision 3: ChatKit UI Library

**Decision**: Use OpenAI ChatKit for React-based chat UI

**Rationale**:
- Pre-built chat components (message list, input field, loading states)
- TypeScript support with type-safe interfaces
- Responsive design for mobile/desktop
- Handles common patterns like message streaming, error display
- Maintained by OpenAI with Next.js compatibility

**Alternatives Considered**:
- **Custom chat UI**: More control but significant development time; need to handle edge cases
- **react-chat-widget**: Less feature-rich; not optimized for AI agents
- **ChatUI library**: Less mature ecosystem; limited documentation

**Implementation Notes**:
- Install: `npm install @openai/chatkit`
- Component will be in `frontend/src/components/ChatInterface.tsx`
- Requires domain allowlist configuration in environment variables
- Will proxy requests through Next.js API route to backend

### Decision 4: Conversation Storage Strategy

**Decision**: PostgreSQL with SQLModel for Conversation and Message entities

**Rationale**:
- Reuses existing Phase 2 database infrastructure (Neon PostgreSQL)
- SQLModel provides type-safe models with Pydantic validation
- Supports complex queries for conversation history retrieval
- ACID compliance ensures conversation consistency
- No additional database setup required

**Alternatives Considered**:
- **Redis for conversation cache**: Requires additional infrastructure; conversation history is permanent data
- **MongoDB for document storage**: Requires new database; overkill for simple relational data
- **In-memory storage**: Violates constitution requirement for persistence across restarts

**Implementation Notes**:
- Conversation table: `id (UUID PK), user_id (FK), created_at, updated_at`
- Message table: `id (UUID PK), user_id (FK), conversation_id (FK), role (enum), content (TEXT), created_at`
- Indexes on: `user_id`, `conversation_id`, `created_at`
- Foreign keys with CASCADE delete for data integrity

### Decision 5: Chat Endpoint Design

**Decision**: Stateless FastAPI endpoint at `POST /api/{user_id}/chat`

**Rationale**:
- Follows constitution Principle VII (Chat Endpoints) specification
- Stateless design enables horizontal scaling
- Request includes: `message` (required), `conversation_id` (optional)
- Response includes: `conversation_id`, `response`, `tool_calls` (array)
- Each request fetches conversation history from DB
- Follows Phase 2 authentication pattern (JWT token validation)

**Alternatives Considered**:
- **WebSocket-based chat**: Real-time but adds complexity; explicitly out of scope per spec
- **Server-Sent Events (SSE)**: Streaming responses but requires client-side complexity
- **Stateful session management**: Violates constitution stateless requirement

**Implementation Notes**:
- Endpoint in `backend/src/api/chat.py`
- Request validation with Pydantic models
- Conversation history limited to last 20 messages for context window management
- Error handling returns 500 with user-friendly messages (per constitution Principle VIII)

## Best Practices Research

### OpenAI Agents SDK Best Practices

**Tool Registration**:
```python
from openai_agents import Agent, Tool

# Each MCP tool becomes an OpenAI Agent tool
tools = [
    Tool(name="add_task", function=mcp.add_task, description="..."),
    Tool(name="list_tasks", function=mcp.list_tasks, description="..."),
    # ... other tools
]

agent = Agent(model="gpt-4", tools=tools, instructions="You are a task management assistant...")
```

**Error Handling**:
- Always wrap agent.run() in try/except
- Return structured errors to frontend
- Log tool call failures for debugging

**Context Management**:
- Pass conversation history as messages array
- Format: `[{"role": "user|assistant", "content": "..."}]`
- Limit to last 20 messages to avoid token limits

### MCP Server Best Practices

**Tool Function Signature**:
```python
from mcp import Tool

@Tool(name="add_task", description="Create a new task")
def add_task(user_id: str, title: str, due_date: str | None = None) -> dict:
    """
    Create task for user.

    Returns: {task_id: str, status: str, data: dict}
    """
    # Enforce user isolation
    # Validate inputs
    # Return structured response
```

**Security**:
- Always validate `user_id` matches authenticated user
- Sanitize inputs before database operations
- Use parameterized queries (SQLModel handles this)
- Never expose internal IDs or system details in error messages

### ChatKit Integration Best Practices

**Component Setup**:
```typescript
import { ChatInterface } from '@openai/chatkit';

<ChatInterface
  onSendMessage={handleSendMessage}
  messages={messages}
  loading={loading}
  error={error}
/>
```

**Message Format**:
- Array of `{id, role: 'user'|'assistant', content, timestamp}`
- Keep messages in React state
- Persist to backend on each exchange

**Error Handling**:
- Display user-friendly errors in chat UI
- Retry failed requests automatically (with exponential backoff)
- Show loading states during agent processing

## Integration Patterns

### Frontend → Backend Flow

1. **User sends message** in ChatKit UI
2. **Frontend** sends POST to `/api/{user_id}/chat` with JWT token
3. **Backend** validates token, extracts user_id
4. **Backend** loads conversation history from DB (last 20 messages)
5. **Backend** constructs messages array for agent
6. **Agent** processes with MCP tools (tool calls as needed)
7. **Backend** stores user message + assistant response in DB
8. **Backend** returns response with conversation_id and tool_calls
9. **Frontend** updates ChatKit UI with new messages

### Database Query Patterns

**Load Conversation History**:
```python
messages = session.exec(
    select(Message)
    .where(Message.conversation_id == conv_id)
    .where(Message.user_id == user_id)  # user isolation
    .order_by(Message.created_at.desc())
    .limit(20)
).all()
```

**Create New Message**:
```python
message = Message(
    user_id=user_id,
    conversation_id=conv_id,
    role=role,
    content=content
)
session.add(message)
session.commit()
```

## Performance Considerations

### Target Metrics (from spec SC-002)
- p95 latency: <2 seconds for chat responses
- Includes: DB query + agent processing + tool calls + response storage

### Optimization Strategies
1. **Database Indexes**: Index on `(user_id, conversation_id, created_at)` for fast history retrieval
2. **Connection Pooling**: Reuse DB connections across requests
3. **Async Operations**: Use FastAPI async endpoints with asyncio for I/O
4. **Message Limiting**: Cap conversation history at 20 messages to reduce context size
5. **Tool Call Batching**: Agent can make multiple tool calls in single turn (e.g., list_tasks then complete_task)

### Scalability Notes
- Stateless design enables horizontal scaling
- Each request is independent (no shared state)
- Database is bottleneck; Neon PostgreSQL auto-scales
- OpenAI API rate limits: monitor and implement backoff

## Security Considerations

### User Isolation (Constitution Principle VIII + IX)
- All MCP tools verify `user_id` matches JWT token
- Database queries always filter by `user_id`
- Agent cannot access other users' tasks
- Test with multiple user accounts

### Input Validation
- Validate message content (non-empty, max 5000 characters)
- Validate conversation_id format (UUID)
- Sanitize user input before passing to agent
- Agent responses validated before storing in DB

### API Key Security
- OPENAI_API_KEY stored in environment variables
- Never exposed to frontend
- Backend makes all OpenAI API calls
- Rotate keys periodically

## Testing Strategy

### MCP Tools Testing (Constitution Principle IV)
```python
def test_add_task_enforces_user_isolation():
    # Test that user A cannot create tasks for user B
    result = add_task(user_id="user_a", title="Task for user B")
    # Verify task is owned by user_a, not user_b
```

### Agent Behavior Testing
- Mock OpenAI responses for deterministic tests
- Test tool selection for various natural language inputs
- Test error handling (invalid tool params, tool failures)

### Conversation Persistence Testing
- Create conversation → restart server → verify history loads
- Test message ordering (chronological)
- Test conversation_id generation (new vs existing)

## Unresolved Clarifications

**NONE** - All technical decisions resolved above.

## Summary

All technology choices align with constitution v1.2.0:
- ✅ Principle IX: AI Agent Design (MCP tools, stateless, user isolation)
- ✅ Principle VII: Chat Endpoints (POST /api/{user_id}/chat)
- ✅ Principle VIII: Security (API keys, input validation, user isolation)
- ✅ Phase 3 Technology Stack (OpenAI Agents SDK, MCP SDK, ChatKit)

Ready to proceed to Phase 1: Data Model and API Contracts.

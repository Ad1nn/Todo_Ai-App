# Quickstart: AI-Powered Chatbot for Task Management

**Feature**: 003-ai-chatbot
**Branch**: `003-ai-chatbot`
**Date**: 2026-01-23

## Overview

This feature adds natural language chat capabilities to the Todo app, allowing users to manage tasks through conversational AI. The implementation uses OpenAI Agents SDK for agent orchestration, MCP SDK for tool exposure, and ChatKit for the frontend UI.

## Prerequisites

Before starting implementation, ensure:

- [x] Phase 2 backend and frontend are functional
- [x] Better Auth JWT authentication is working
- [x] PostgreSQL database (Neon) is accessible
- [x] Python 3.13+ and UV package manager installed
- [x] Node.js 20+ and npm/pnpm installed
- [x] OpenAI API key obtained (sign up at platform.openai.com)

## Environment Setup

### 1. Install Backend Dependencies

```bash
cd backend

# Install OpenAI Agents SDK
uv add openai-agents-sdk

# Install MCP SDK
uv add mcp

# Install OpenAI Python SDK (required by agents SDK)
uv add openai

# Verify installations
uv pip list | grep -E "(openai|mcp)"
```

### 2. Install Frontend Dependencies

```bash
cd frontend

# Install ChatKit
npm install @openai/chatkit

# Verify installation
npm list @openai/chatkit
```

### 3. Configure Environment Variables

Add to `backend/.env`:

```env
# OpenAI API Configuration
OPENAI_API_KEY=sk-proj-...your-key-here...
OPENAI_MODEL=gpt-4  # or gpt-4-turbo, gpt-3.5-turbo

# ChatKit Domain Allowlist (comma-separated)
CHATKIT_ALLOWED_DOMAINS=localhost:3000,your-production-domain.com
```

### 4. Database Migration

```bash
cd backend

# Create migration for Conversation and Message tables
alembic revision -m "Add conversation and message tables"

# Edit the migration file to include:
# - conversations table (id, user_id, created_at, updated_at)
# - messages table (id, user_id, conversation_id, role, content, tool_calls, created_at)
# - Indexes for user isolation and performance

# Run migration
alembic upgrade head

# Verify tables created
psql $DATABASE_URL -c "\dt conversations messages"
```

## Development Order

Follow this sequence to build the feature incrementally:

### Phase 1: Database Layer (Test-First)

**Files to create**:
- `backend/src/models/conversation.py` - Conversation SQLModel
- `backend/src/models/message.py` - Message SQLModel
- `backend/src/repositories/conversation_repository.py` - Interface
- `backend/src/repositories/sqlmodel_conversation_repository.py` - Implementation
- `backend/tests/test_conversation_models.py` - Model tests
- `backend/tests/test_conversation_repository.py` - Repository tests

**Tests to write first**:
```python
# Test conversation creation
# Test message creation
# Test user isolation (user A cannot access user B's conversations)
# Test cascade delete (delete conversation deletes messages)
# Test conversation history retrieval (last 20 messages)
```

**Run tests**:
```bash
cd backend
pytest tests/test_conversation_models.py -v
pytest tests/test_conversation_repository.py -v
```

### Phase 2: MCP Tools (Test-First)

**Files to create**:
- `backend/src/mcp/tools.py` - MCP tool implementations
- `backend/src/mcp/server.py` - MCP server configuration
- `backend/tests/test_mcp_tools.py` - Tool tests

**MCP Tools to implement**:
1. `add_task(user_id, title, due_date?) -> {task_id, status, data}`
2. `list_tasks(user_id, completed?) -> {status, tasks[]}`
3. `complete_task(user_id, task_id) -> {task_id, status, data}`
4. `delete_task(user_id, task_id) -> {task_id, status}`
5. `update_task(user_id, task_id, title?, due_date?) -> {task_id, status, data}`

**Tests to write first**:
```python
# Test each tool with valid inputs
# Test user isolation (user A cannot modify user B's tasks)
# Test error cases (task not found, invalid parameters)
# Test structured error responses (user-friendly messages)
```

**Run tests**:
```bash
cd backend
pytest tests/test_mcp_tools.py -v
```

### Phase 3: Agent Configuration (Test-First with Mocks)

**Files to create**:
- `backend/src/agent/config.py` - Agent setup with OpenAI Agents SDK
- `backend/src/agent/prompts.py` - System prompts and instructions
- `backend/tests/test_agent_config.py` - Agent tests (mocked OpenAI API)

**Agent configuration**:
```python
from openai_agents import Agent, Tool

# Register MCP tools as agent tools
tools = [
    Tool(name="add_task", function=mcp.add_task, description="..."),
    Tool(name="list_tasks", function=mcp.list_tasks, description="..."),
    # ... other tools
]

# Create agent with instructions
agent = Agent(
    model="gpt-4",
    tools=tools,
    instructions="You are a helpful task management assistant..."
)
```

**Tests to write first** (with mocked OpenAI responses):
```python
# Test tool selection for "add task" intent
# Test tool selection for "show tasks" intent
# Test conversation context handling
# Test error handling (OpenAI API failure)
```

**Run tests**:
```bash
cd backend
pytest tests/test_agent_config.py -v
```

### Phase 4: Chat Endpoint (Test-First)

**Files to create**:
- `backend/src/api/chat.py` - FastAPI chat endpoint
- `backend/src/services/chat_service.py` - Chat business logic
- `backend/tests/test_chat_endpoint.py` - Endpoint tests

**Endpoint structure**:
```python
@router.post("/api/{user_id}/chat")
async def send_message(
    user_id: UUID,
    request: ChatRequest,
    current_user: User = Depends(get_current_user)
):
    # 1. Validate user_id matches JWT token
    # 2. Load conversation history (or create new)
    # 3. Call agent with conversation context
    # 4. Store user message and assistant response
    # 5. Return ChatResponse
```

**Tests to write first**:
```python
# Test new conversation creation
# Test existing conversation continuation
# Test user_id validation (JWT token match)
# Test conversation history loading
# Test message persistence
# Test error handling (OpenAI API down, invalid conversation_id)
```

**Run tests**:
```bash
cd backend
pytest tests/test_chat_endpoint.py -v
```

### Phase 5: Frontend ChatKit Integration

**Files to create**:
- `frontend/src/components/ChatInterface.tsx` - ChatKit wrapper
- `frontend/src/app/chat/page.tsx` - Chat page
- `frontend/src/services/chatService.ts` - API client
- `frontend/src/hooks/useChat.ts` - Chat state management

**Component structure**:
```typescript
import { ChatInterface } from '@openai/chatkit';

export default function ChatPage() {
  const { messages, sendMessage, loading, error } = useChat();

  return (
    <ChatInterface
      messages={messages}
      onSendMessage={sendMessage}
      loading={loading}
      error={error}
    />
  );
}
```

**Tests to write**:
```typescript
// Test message sending
// Test message display
// Test loading states
// Test error display
// Test JWT token inclusion in requests
```

**Run tests**:
```bash
cd frontend
npm test -- ChatInterface.test.tsx
```

## Running the Application

### 1. Start Backend

```bash
cd backend
uvicorn src.main:app --reload --port 8000
```

Backend will be available at http://localhost:8000

### 2. Start Frontend

```bash
cd frontend
npm run dev
```

Frontend will be available at http://localhost:3000

### 3. Access Chat Interface

Navigate to: http://localhost:3000/chat

## Testing the Feature

### Manual Testing Scenarios

**Scenario 1: Create Task**
1. Login to the application
2. Navigate to /chat
3. Type: "Remind me to buy groceries tomorrow"
4. Verify: Task appears in response and in task list

**Scenario 2: View Tasks**
1. Type: "What tasks do I have?"
2. Verify: List of pending tasks displayed

**Scenario 3: Complete Task**
1. Type: "Mark the groceries task as done"
2. Verify: Task marked complete in database and UI

**Scenario 4: Conversation Context**
1. Type: "Show my tasks"
2. Type: "Complete the first one"
3. Verify: Agent remembers context and completes correct task

**Scenario 5: Error Handling**
1. Type: "Complete task 12345" (invalid ID)
2. Verify: User-friendly error message displayed

### Automated Testing

Run full test suite:

```bash
# Backend tests
cd backend
pytest -v --cov=src --cov-report=term-missing

# Frontend tests
cd frontend
npm test

# Integration tests (requires running servers)
cd backend
pytest tests/integration/ -v
```

### Performance Testing

Test p95 latency meets <2 second requirement:

```bash
# Use ab (Apache Bench) or wrk
ab -n 100 -c 10 -H "Authorization: Bearer $JWT_TOKEN" \
   -p chat_request.json \
   -T application/json \
   http://localhost:8000/api/{user_id}/chat
```

## Debugging

### Backend Logs

```bash
# View FastAPI logs
cd backend
tail -f logs/app.log

# Check database queries
export DATABASE_LOG_LEVEL=DEBUG
uvicorn src.main:app --reload
```

### Frontend Logs

Open browser DevTools (F12) and check:
- Console for errors
- Network tab for API calls
- Application tab for JWT token

### MCP Tool Debugging

Tools return `tool_calls` array in response for debugging:

```json
{
  "conversation_id": "...",
  "response": "✓ Added task",
  "tool_calls": [
    {
      "tool": "add_task",
      "parameters": {"user_id": "...", "title": "..."},
      "result": {"task_id": "...", "status": "success"}
    }
  ]
}
```

## Troubleshooting

### Common Issues

**Issue**: `OPENAI_API_KEY not found`
- **Fix**: Add to `backend/.env` file

**Issue**: `ChatKit domain not allowed`
- **Fix**: Add domain to `CHATKIT_ALLOWED_DOMAINS` in `.env`

**Issue**: `Conversation not found`
- **Fix**: Check conversation_id is valid UUID and belongs to user

**Issue**: `Agent not calling tools`
- **Fix**: Check tool descriptions are clear; review agent instructions

**Issue**: `Database migration fails`
- **Fix**: Check foreign key references; verify users table exists

**Issue**: `p95 latency >2 seconds`
- **Fix**: Check database indexes; reduce conversation history limit; optimize OpenAI API calls

## Next Steps

After implementation is complete:

1. **Run /sp.tasks**: Generate task breakdown with test cases
2. **Run /sp.implement**: Execute implementation via Claude Code
3. **Manual QA**: Test all user scenarios
4. **Performance testing**: Verify <2 second p95 latency
5. **Security audit**: Verify user isolation and input validation
6. **Create PR**: Document changes and request review

## Resources

- [OpenAI Agents SDK Documentation](https://github.com/openai/agents-sdk-python)
- [MCP SDK Documentation](https://github.com/modelcontextprotocol/mcp-sdk)
- [ChatKit Documentation](https://github.com/openai/chatkit)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Next.js App Router Documentation](https://nextjs.org/docs/app)
- [Feature Specification](./spec.md)
- [Technical Plan](./plan.md)
- [Data Model](./data-model.md)
- [API Contracts](./contracts/)

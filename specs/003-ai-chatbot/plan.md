# Implementation Plan: AI-Powered Chatbot for Task Management

**Branch**: `003-ai-chatbot` | **Date**: 2026-01-23 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/003-ai-chatbot/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Add natural language chat interface for task management using OpenAI Agents SDK, MCP tools, and ChatKit UI. Users can create, view, complete, delete, and update tasks through conversational AI. The system maintains conversation context across sessions with stateless server architecture and database-persisted conversation history. All MCP tools enforce user isolation via user_id parameter validation.

## Technical Context

**Language/Version**: Python 3.13+ (backend), TypeScript 5.x (frontend)
**Primary Dependencies**:
- Backend: FastAPI, SQLModel, OpenAI Agents SDK, MCP SDK, OpenAI Python SDK
- Frontend: Next.js 15+, React 18+, OpenAI ChatKit, TypeScript
**Storage**: Neon PostgreSQL (serverless, Phase 2 existing + new Conversation/Message tables)
**Testing**: pytest + httpx (backend), Jest + React Testing Library (frontend)
**Target Platform**: Linux server (backend), Web browsers (Chrome, Firefox, Safari, Edge)
**Project Type**: Web application (extends Phase 2 monorepo with /backend and /frontend)
**Performance Goals**: <2 seconds p95 latency for chat responses, 90% natural language understanding accuracy
**Constraints**:
- Stateless server (no in-memory session state)
- User isolation enforced at all layers (MCP tools, repository, database queries)
- OpenAI API rate limits (monitor and implement backoff)
- Conversation history limited to last 20 messages for context window management
**Scale/Scope**:
- Multi-user (100+ concurrent users)
- 6 user stories (3 P1, 1 P2, 2 P3)
- 2 new database entities (Conversation, Message)
- 5 MCP tools (add_task, list_tasks, complete_task, delete_task, update_task)
- 1 new chat endpoint (POST /api/{user_id}/chat)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Principle I: Spec-Driven Development
- ✅ **PASS**: Specification created and approved before planning
- ✅ **PASS**: All requirements traced from spec.md
- ✅ **PASS**: No manual coding - implementation via /sp.implement

### Principle II: Clean Code Principles
- ✅ **PASS**: Functions will have single responsibilities
- ✅ **PASS**: Descriptive naming (Conversation, Message, add_task, etc.)
- ✅ **PASS**: Target <20 lines per function, <200 lines per file
- ✅ **PASS**: No duplication - repository pattern reused from Phase 2

### Principle III: Language Best Practices
- ✅ **PASS**: Python 3.13+ with UV package manager
- ✅ **PASS**: Type hints for all functions (SQLModel, Pydantic)
- ✅ **PASS**: ruff format and ruff check for linting
- ✅ **PASS**: TypeScript strict mode enabled in frontend
- ✅ **PASS**: ESLint + Prettier for frontend formatting

### Principle IV: Test-First Approach
- ✅ **PASS**: Tests will be written before implementation
- ✅ **PASS**: pytest for backend, Jest for frontend
- ✅ **PASS**: Target >80% coverage for business logic
- ✅ **PASS**: MCP tools tested independently with mock data
- ✅ **PASS**: Mocked OpenAI responses for deterministic agent tests

### Principle V: Modular Architecture
- ✅ **PASS**: MCP Server as separate module (backend/src/mcp/)
- ✅ **PASS**: Repository pattern for data access (Phase 2 pattern reused)
- ✅ **PASS**: Clear module boundaries (models, repositories, services, api, mcp, agent)
- ✅ **PASS**: Dependencies flow inward (UI → API → Services → Models)
- ✅ **PASS**: No circular dependencies

### Principle VI: Simplicity First (YAGNI)
- ✅ **PASS**: Only Phase 3 features implemented (no speculative additions)
- ✅ **PASS**: No premature optimization (make it work, then optimize if needed)
- ✅ **PASS**: Simplest solution: OpenAI Agents SDK (not custom implementation)
- ✅ **PASS**: Out of scope: WebSockets, voice I/O, custom AI training

### Principle VII: API Design Principles
- ✅ **PASS**: Chat endpoint: POST /api/{user_id}/chat (per constitution)
- ✅ **PASS**: Request includes message + optional conversation_id
- ✅ **PASS**: Response includes conversation_id + response + tool_calls
- ✅ **PASS**: Stateless design (conversation state in database)
- ✅ **PASS**: Standard HTTP status codes (200, 400, 401, 404, 500)
- ✅ **PASS**: JSON request/response bodies
- ✅ **PASS**: JWT authentication required

### Principle VIII: Security Principles
- ✅ **PASS**: OPENAI_API_KEY stored in environment variables
- ✅ **PASS**: User input validated before agent processing
- ✅ **PASS**: Agent responses validated before database operations
- ✅ **PASS**: MCP tools enforce user isolation via user_id parameter
- ✅ **PASS**: Parameterized queries via SQLModel (no SQL injection)
- ✅ **PASS**: JWT token validation for all chat requests

### Principle IX: AI Agent Design Principles (Phase 3)
- ✅ **PASS**: MCP tools have single, clear purpose
- ✅ **PASS**: Tool parameters include user_id for ownership enforcement
- ✅ **PASS**: Tool responses include task_id, status, and data
- ✅ **PASS**: Tools are stateless (all state in database)
- ✅ **PASS**: Error handling returns structured user-friendly messages
- ✅ **PASS**: Agent confirms actions with friendly responses
- ✅ **PASS**: Agent uses appropriate tools based on user intent
- ✅ **PASS**: Conversations persisted to database
- ✅ **PASS**: Conversation history loaded on each request
- ✅ **PASS**: Server restart does not lose conversation state

### Phase 3 Technology Stack Compliance
- ✅ **PASS**: OpenAI Agents SDK for agent orchestration
- ✅ **PASS**: Official MCP SDK for tool exposure
- ✅ **PASS**: OpenAI ChatKit for frontend chat UI
- ✅ **PASS**: Conversation and Message SQLModel entities
- ✅ **PASS**: Stateless FastAPI chat endpoint

### Phase 3 Constraints Compliance
- ✅ **PASS**: Chat endpoint is stateless (conversation state in database only)
- ✅ **PASS**: MCP tools enforce user isolation via user_id parameter
- ✅ **PASS**: Agent uses MCP tools for all task operations (no direct DB access)
- ✅ **PASS**: Frontend includes JWT token in all chat requests
- ✅ **PASS**: Conversation history fetched from DB on each request

**GATE STATUS: ✅ ALL GATES PASSED** - Proceed to implementation

## Project Structure

### Documentation (this feature)

```text
specs/003-ai-chatbot/
├── spec.md              # Feature specification (user stories, requirements)
├── plan.md              # This file (technical architecture plan)
├── research.md          # Technology decisions and best practices
├── data-model.md        # Database entities (Conversation, Message)
├── quickstart.md        # Development guide and testing instructions
├── contracts/           # API specifications
│   ├── chat-api.yaml    # OpenAPI spec for chat endpoint
│   └── mcp-tools.yaml   # MCP tool specifications
├── checklists/
│   └── requirements.md  # Specification quality validation
└── tasks.md             # NEXT PHASE: /sp.tasks command (NOT created by /sp.plan)
```

### Source Code (repository root)

**Web Application Structure (Phase 2 monorepo extended for Phase 3)**

```text
backend/
├── src/
│   ├── models/
│   │   ├── user.py              # Phase 2 (updated with relationships)
│   │   ├── task.py              # Phase 2
│   │   ├── conversation.py      # Phase 3: NEW
│   │   └── message.py           # Phase 3: NEW
│   ├── repositories/
│   │   ├── task_repository.py           # Phase 2
│   │   ├── conversation_repository.py   # Phase 3: NEW (interface)
│   │   └── sqlmodel_conversation_repository.py  # Phase 3: NEW (implementation)
│   ├── services/
│   │   ├── task_service.py      # Phase 2
│   │   └── chat_service.py      # Phase 3: NEW
│   ├── api/
│   │   ├── tasks.py             # Phase 2
│   │   ├── auth.py              # Phase 2
│   │   └── chat.py              # Phase 3: NEW (POST /api/{user_id}/chat)
│   ├── mcp/                      # Phase 3: NEW MODULE
│   │   ├── __init__.py
│   │   ├── tools.py             # MCP tool implementations
│   │   └── server.py            # MCP server configuration
│   ├── agent/                    # Phase 3: NEW MODULE
│   │   ├── __init__.py
│   │   ├── config.py            # OpenAI Agents SDK setup
│   │   └── prompts.py           # System prompts and instructions
│   └── main.py                   # FastAPI application (Phase 2, extended)
├── tests/
│   ├── unit/
│   │   ├── test_task_models.py          # Phase 2
│   │   ├── test_conversation_models.py  # Phase 3: NEW
│   │   └── test_mcp_tools.py            # Phase 3: NEW
│   ├── integration/
│   │   ├── test_task_endpoints.py       # Phase 2
│   │   ├── test_chat_endpoint.py        # Phase 3: NEW
│   │   └── test_agent_config.py         # Phase 3: NEW (mocked OpenAI)
│   └── contract/
│       └── test_mcp_contract.py         # Phase 3: NEW
├── alembic/                      # Database migrations
│   └── versions/
│       ├── 001_initial.py        # Phase 2
│       ├── 002_add_tasks.py      # Phase 2
│       └── 003_add_conversation_message.py  # Phase 3: NEW
├── .env                          # Environment variables (add OPENAI_API_KEY)
└── pyproject.toml                # Dependencies (add openai-agents-sdk, mcp)

frontend/
├── src/
│   ├── components/
│   │   ├── TaskList.tsx          # Phase 2
│   │   ├── TaskForm.tsx          # Phase 2
│   │   └── ChatInterface.tsx     # Phase 3: NEW (ChatKit wrapper)
│   ├── app/
│   │   ├── layout.tsx            # Phase 2
│   │   ├── page.tsx              # Phase 2 (dashboard)
│   │   ├── tasks/                # Phase 2
│   │   └── chat/                 # Phase 3: NEW
│   │       └── page.tsx          # Chat page
│   ├── services/
│   │   ├── taskService.ts        # Phase 2
│   │   └── chatService.ts        # Phase 3: NEW (API client)
│   ├── hooks/
│   │   ├── useTasks.ts           # Phase 2
│   │   └── useChat.ts            # Phase 3: NEW (chat state management)
│   └── types/
│       ├── task.ts               # Phase 2
│       └── chat.ts               # Phase 3: NEW
├── tests/
│   ├── components/
│   │   ├── TaskList.test.tsx     # Phase 2
│   │   └── ChatInterface.test.tsx # Phase 3: NEW
│   └── services/
│       └── chatService.test.ts   # Phase 3: NEW
├── package.json                  # Dependencies (add @openai/chatkit)
└── .env.local                    # Environment variables (NEXT_PUBLIC_API_URL)
```

**Structure Decision**: Extends Phase 2 web application monorepo with new modules for AI chatbot functionality. Backend adds two new modules (`mcp/` and `agent/`) and two new database models. Frontend adds chat page and ChatKit integration. All new code follows existing Phase 2 patterns (repository, service, API layers) for consistency.

## Complexity Tracking

> **No violations detected - all constitution gates passed**

This feature introduces appropriate complexity for Phase 3 requirements:
- MCP module: Required by constitution Principle IX (MCP Server as separate module)
- Agent module: Necessary for OpenAI Agents SDK configuration and prompt management
- Repository pattern: Reused from Phase 2 (no new complexity)
- Two new database entities: Minimal required for conversation persistence
- Stateless architecture: Required by constitution (no server-side sessions)

All architectural decisions follow YAGNI principle - only Phase 3 specified features implemented.

# Tasks: AI-Powered Chatbot for Task Management

**Input**: Design documents from `/specs/003-ai-chatbot/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md

**Organization**: Tasks are consolidated and grouped by user story for efficient implementation. Each task combines related work (tests + implementation).

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different areas, no dependencies)
- **[Story]**: Which user story this task belongs to (US1-US6)
- Tasks include exact file paths

## Path Conventions

**Web app structure**: `backend/src/`, `backend/tests/`, `frontend/src/`, `frontend/tests/`

---

## Phase 1: Setup & Configuration

**Purpose**: Install dependencies and configure environment for Phase 3

- [X] T001 Install backend dependencies (openai-agents-sdk, mcp, openai) via `uv add` and verify installation
- [X] T002 Install frontend dependencies (@openai/chatkit) via npm and verify installation
- [X] T003 Configure environment variables in backend/.env (OPENAI_API_KEY, OPENAI_MODEL, CHATKIT_ALLOWED_DOMAINS)

---

## Phase 2: Database Foundation

**Purpose**: Database models and migrations that MUST be complete before user stories

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T004 [P] Create Conversation model in backend/src/models/conversation.py (id, user_id, created_at, updated_at) with unit tests
- [X] T005 [P] Create Message model in backend/src/models/message.py (id, user_id, conversation_id, role, content, tool_calls, created_at) with MessageRole enum and unit tests
- [X] T006 Update User model in backend/src/models/user.py to add conversations and messages relationships
- [X] T007 Create and run database migration backend/alembic/versions/002_add_conversation_message_tables.py with indexes (user_id, conversation_id, created_at)
- [X] T008 [P] Implement ConversationRepository with SQLModel in backend/src/repositories/conversation_repository.py with tests
- [ ] T009 Write and run user isolation tests for ConversationRepository (user A cannot access user B's conversations)

**Checkpoint**: Foundation ready - user stories can now begin

---

## Phase 3: User Story 1 - Create Task via Natural Language (Priority: P1) 🎯

**Goal**: Users can create tasks via chat ("remind me to buy groceries tomorrow")

**Independent Test**: Send "add task to call dentist", verify task created and agent responds

- [X] T010 [US1] Implement add_task MCP tool in backend/src/mcp/tools.py with validation, error handling, and unit tests (including user isolation test)
- [X] T011 [US1] Create agent configuration in backend/src/agent/config.py and prompts in backend/src/agent/prompts.py, register add_task tool with OpenAI Agents SDK
- [ ] T012 [US1] Write and run agent integration tests in backend/tests/integration/test_agent_config.py with mocked OpenAI responses for "add task" intent
- [X] T013 [US1] Implement ChatService in backend/src/services/chat_service.py (create_conversation, process_message with conversation history loading)
- [X] T014 [US1] Create chat endpoint POST /api/{user_id}/chat in backend/src/api/chat.py with JWT validation, request validation, and integration tests
- [X] T015 [P] [US1] Create frontend chat types in frontend/src/types/chat.ts (Message, ChatRequest, ChatResponse, ToolCall)
- [X] T016 [P] [US1] Implement chatService in frontend/src/services/chatService.ts (API client with JWT token inclusion)
- [X] T017 [P] [US1] Create useChat hook in frontend/src/hooks/useChat.ts for state management
- [X] T018 [US1] Create ChatInterface component in frontend/src/components/ChatInterface.tsx (ChatKit wrapper) with tests
- [X] T019 [US1] Create chat page in frontend/src/app/chat/page.tsx integrating ChatInterface with useChat hook

**Checkpoint**: US1 complete - users can create tasks via natural language chat

---

## Phase 4: User Story 2 - View Tasks via Natural Language (Priority: P1)

**Goal**: Users can view tasks via chat ("what's on my list?", "show pending tasks")

**Independent Test**: Create tasks, send "show my tasks", verify correct list returned

- [X] T020 [US2] Implement list_tasks MCP tool in backend/src/mcp/tools.py with user isolation, completed filter, and unit tests
- [X] T021 [US2] Register list_tasks tool in agent config backend/src/agent/config.py, update prompts, and write integration tests for "show tasks" intent
- [ ] T022 [US2] Add list_tasks integration tests to backend/tests/integration/test_chat_endpoint.py (empty list, filtered list scenarios)
- [X] T023 [US2] Update ChatInterface component in frontend/src/components/ChatInterface.tsx to format task lists with tests

**Checkpoint**: US1 + US2 complete - create and view tasks

---

## Phase 5: User Story 3 - Maintain Conversation Context (Priority: P1)

**Goal**: Chatbot remembers conversation history ("mark the first one done" after viewing tasks)

**Independent Test**: Multi-turn conversation, verify context maintained

- [X] T024 [US3] Implement conversation history loading in ChatService (load last 20 messages, include in agent context)
- [X] T025 [US3] Update ChatService to persist user and assistant messages to database with tests
- [ ] T026 [US3] Write integration tests for conversation persistence in backend/tests/integration/test_chat_endpoint.py (same conversation_id, server restart test)
- [X] T027 [US3] Update useChat hook in frontend/src/hooks/useChat.ts to persist and send conversation_id with tests

**Checkpoint**: MVP complete (P1 stories) - create + view + context

---

## Phase 6: User Story 4 - Complete Tasks via Natural Language (Priority: P2)

**Goal**: Users can complete tasks via chat ("I finished the report")

**Independent Test**: Create task, send completion message, verify status updated

- [X] T028 [US4] Implement complete_task MCP tool in backend/src/mcp/tools.py with user isolation, task_not_found error handling, and unit tests
- [X] T029 [US4] Register complete_task tool in agent config, update prompts, write integration tests for "mark done" intent
- [ ] T030 [US4] Add complete_task integration tests to chat endpoint (task completion, task_not_found scenarios)

**Checkpoint**: US1-4 complete

---

## Phase 7: User Story 5 - Delete Tasks via Natural Language (Priority: P3)

**Goal**: Users can delete tasks via chat ("remove buy groceries task")

**Independent Test**: Create task, send deletion command, verify removed from database

- [X] T031 [US5] Implement delete_task MCP tool in backend/src/mcp/tools.py with user isolation, error handling, and unit tests
- [X] T032 [US5] Register delete_task tool in agent config, update prompts, write integration tests for "delete task" intent
- [ ] T033 [US5] Add delete_task integration tests to chat endpoint

**Checkpoint**: US1-5 complete

---

## Phase 8: User Story 6 - Update Task Details via Natural Language (Priority: P3)

**Goal**: Users can update tasks via chat ("change the deadline to Friday")

**Independent Test**: Create task, send update command, verify fields modified

- [X] T034 [US6] Implement update_task MCP tool in backend/src/mcp/tools.py with user isolation, validation (require title or description), error handling, and unit tests
- [X] T035 [US6] Register update_task tool in agent config, update prompts, write integration tests for "change deadline" intent
- [ ] T036 [US6] Add update_task integration tests to chat endpoint

**Checkpoint**: All 6 user stories complete - full CRUD via chat

---

## Phase 9: MCP Server & Error Handling

**Purpose**: Configure MCP server and handle edge cases

- [ ] T037 Create MCP server configuration in backend/src/mcp/server.py, register all 5 tools, add metadata, write tool discovery tests
- [X] T038 [P] Add OpenAI API error handling to ChatService (API down, rate limit, timeout) with tests
- [X] T039 [P] Add conversation history truncation handling (>20 messages) with tests
- [X] T040 Update ChatInterface to display backend error messages with tests

**Checkpoint**: Error handling complete

---

## Phase 10: Performance & Optimization

**Purpose**: Ensure <2 second p95 latency requirement

- [ ] T041 [P] Add database indexes per data-model.md and configure connection pooling in backend/src/main.py
- [ ] T042 [P] Convert chat endpoint to async in backend/src/api/chat.py with async/await for I/O operations
- [ ] T043 Add performance logging to ChatService and write performance test for <2s p95 latency in backend/tests/performance/test_chat_latency.py

**Checkpoint**: Performance validated

---

## Phase 11: Polish & Validation

**Purpose**: Final quality checks and documentation

- [X] T044 [P] Update API documentation with chat endpoint in OpenAPI schema
- [X] T045 [P] Add GET /api/{user_id}/conversations endpoint for frontend to load existing chats
- [X] T046 [P] Add loading states and mobile responsive styles to chat page
- [X] T047 Run backend linting (ruff format && ruff check) and frontend linting (npm run lint && npm run format)
- [ ] T048 Run full test suite: backend (pytest -v --cov) and frontend (npm test)
- [ ] T049 Manual validation: Execute all 6 testing scenarios from quickstart.md
- [ ] T050 Security audit: Verify user isolation in all MCP tools and measure p95 latency with 100 requests

**Checkpoint**: Feature complete and validated

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - start immediately
- **Database (Phase 2)**: Depends on Setup - **BLOCKS all user stories**
- **User Stories (Phase 3-8)**: All depend on Database completion
  - US1, US2, US4, US5, US6: Independent (can run in parallel)
  - US3: Depends on US1 + US2 (needs both for context)
- **MCP & Error (Phase 9)**: Depends on at least US1
- **Performance (Phase 10)**: Depends on chat endpoint (US1)
- **Polish (Phase 11)**: Depends on all desired user stories

### Parallel Opportunities

**Within phases**:
- T004, T005 (database models) can run in parallel
- T015, T016, T017 (frontend pieces) can run in parallel
- T038, T039, T041, T042, T044, T045, T046 (cross-cutting concerns) can run in parallel

**User stories after Phase 2**:
- US1, US2, US4, US5, US6 can start in parallel if team has capacity
- US3 waits for US1 + US2

---

## Implementation Strategies

### MVP First (Recommended)
**Execute**: T001-T027 (27 tasks = 54% of total)

**Delivers**:
- Complete Phase 1: Setup (3 tasks)
- Complete Phase 2: Database (6 tasks)
- Complete Phase 3: US1 - Create (10 tasks)
- Complete Phase 4: US2 - View (4 tasks)
- Complete Phase 5: US3 - Context (4 tasks)

**Result**: Working MVP with create + view + context

### Full Feature
**Execute**: All 50 tasks

**Delivers**: All 6 user stories + error handling + performance + polish

### Parallel Team (3 developers)
After Phase 2 complete:
- Developer A: US1 (T010-T019)
- Developer B: US2 + US3 (T020-T027)
- Developer C: US4 + US5 + US6 (T028-T036)

Then converge for MCP, Performance, Polish

---

## Task Statistics

**Total Tasks**: 50 tasks (reduced from 156)

**Tasks per Phase**:
- Phase 1 (Setup): 3 tasks
- Phase 2 (Database): 6 tasks (BLOCKS all user stories)
- Phase 3 (US1 - Create): 10 tasks
- Phase 4 (US2 - View): 4 tasks
- Phase 5 (US3 - Context): 4 tasks
- Phase 6 (US4 - Complete): 3 tasks
- Phase 7 (US5 - Delete): 3 tasks
- Phase 8 (US6 - Update): 3 tasks
- Phase 9 (MCP & Error): 4 tasks
- Phase 10 (Performance): 3 tasks
- Phase 11 (Polish): 7 tasks

**MVP Scope**: 27 tasks (54% of total) = Setup + Database + US1 + US2 + US3

**Parallelizable Tasks**: 16 tasks marked [P] (32%)

---

## Notes

- [P] = Can run in parallel (different files/areas)
- [Story] = Maps to user story (US1-US6)
- Each task combines related work (tests + implementation)
- TDD approach: Tests included in implementation tasks
- Checkpoint after each user story for validation
- File paths use web app structure
- Commit after completing each task or logical group

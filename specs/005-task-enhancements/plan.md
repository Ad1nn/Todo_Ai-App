# Implementation Plan: Task Enhancements (Quick Wins)

**Branch**: `005-task-enhancements` | **Date**: 2026-02-04 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/005-task-enhancements/spec.md`

## Summary

Add three optional metadata fields to tasks: **due dates** (datetime), **priority levels** (low/normal/high/urgent enum), and **categories** (free-text string). These enhancements enable users to organize, filter, and prioritize tasks through both the web UI and AI chat interface. All fields are nullable to maintain backward compatibility with existing tasks.

## Technical Context

**Language/Version**: Python 3.13+ (backend), TypeScript 5.x (frontend)
**Primary Dependencies**: FastAPI, SQLModel, OpenAI Agents SDK (backend); Next.js 15+, Tailwind CSS (frontend)
**Storage**: Neon PostgreSQL (serverless) via SQLModel ORM
**Testing**: pytest (backend), Jest/Vitest (frontend)
**Target Platform**: Web application (Linux server backend, modern browsers frontend)
**Project Type**: Web application (monorepo: /backend, /frontend)
**Performance Goals**: Filtering returns results in <1 second for 500 tasks per user
**Constraints**: All new fields nullable (backward compatible), no breaking API changes
**Scale/Scope**: Extends existing Phase 2/3 implementation with 3 new database columns

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Spec-Driven Development | ✅ PASS | Spec complete (spec.md), plan in progress |
| II. Clean Code Principles | ✅ PASS | Single responsibility maintained; new enum for Priority |
| III. Language Best Practices | ✅ PASS | Python type hints, TypeScript strict mode |
| IV. Test-First Approach | ✅ PASS | Tests defined before implementation |
| V. Modular Architecture | ✅ PASS | Repository → Service → API pattern preserved |
| VI. Simplicity First (YAGNI) | ✅ PASS | Only spec'd features; no pagination yet |
| VII. API Design Principles | ✅ PASS | REST query params for filtering; consistent error handling |
| VIII. Security Principles | ✅ PASS | user_id ownership enforced in all queries |
| IX. AI Agent Design Principles | ✅ PASS | MCP tools extended with new parameters |
| X. UI/UX Design Principles | ✅ PASS | Color-coded badges, accessible form inputs |

**Post-Design Re-Check**: ✅ All principles satisfied

## Project Structure

### Documentation (this feature)

```text
specs/005-task-enhancements/
├── spec.md              # Feature specification
├── plan.md              # This file
├── research.md          # Phase 0 research output
├── data-model.md        # Phase 1 data model
├── quickstart.md        # Phase 1 implementation guide
├── contracts/
│   ├── api.yaml         # OpenAPI 3.1 contract
│   ├── types.ts         # TypeScript type definitions
│   └── mcp-tools.md     # MCP tool specifications
├── checklists/
│   └── requirements.md  # Specification quality checklist
└── tasks.md             # Phase 2 tasks (/sp.tasks output)
```

### Source Code (repository root)

```text
backend/
├── alembic/
│   └── versions/
│       └── 003_add_task_enhancements.py   # NEW: Database migration
├── src/
│   ├── models/
│   │   └── task.py                        # MODIFY: Add Priority enum, new fields
│   ├── repositories/
│   │   └── task_repository.py             # MODIFY: Add filtered list, get_categories
│   ├── services/
│   │   └── task_service.py                # MODIFY: Update create/update signatures
│   ├── api/
│   │   └── tasks.py                       # MODIFY: Add query params, categories endpoint
│   ├── mcp/
│   │   └── tools.py                       # MODIFY: Update tool parameters
│   └── agent/
│       ├── config.py                      # MODIFY: Update tool definitions
│       └── prompts.py                     # MODIFY: Update system prompt
└── tests/
    └── test_tasks.py                      # MODIFY: Add tests for new features

frontend/
├── src/
│   ├── lib/
│   │   └── types.ts                       # MODIFY: Add Priority type, update Task
│   ├── components/
│   │   ├── TaskItem.tsx                   # MODIFY: Add badges, indicators
│   │   ├── TaskForm.tsx                   # MODIFY: Add form fields
│   │   └── TaskList.tsx                   # MODIFY: Add filters
│   └── hooks/
│       └── useTasks.ts                    # MODIFY: Accept filter params
└── tests/
    └── components/
        └── TaskForm.test.tsx              # MODIFY: Test new fields
```

**Structure Decision**: Web application structure (Option 2) - extends existing monorepo with /backend and /frontend directories. No new directories created; all changes modify existing files.

## File Change Summary

| File | Change Type | Description |
|------|-------------|-------------|
| `backend/alembic/versions/003_*.py` | NEW | Migration adding 3 columns + indexes |
| `backend/src/models/task.py` | MODIFY | Priority enum, update schemas |
| `backend/src/repositories/task_repository.py` | MODIFY | list_by_user_filtered, get_user_categories |
| `backend/src/services/task_service.py` | MODIFY | Update method signatures |
| `backend/src/api/tasks.py` | MODIFY | Query params, /categories endpoint |
| `backend/src/mcp/tools.py` | MODIFY | Tool parameter extensions |
| `backend/src/agent/config.py` | MODIFY | Tool definitions |
| `backend/src/agent/prompts.py` | MODIFY | System prompt enhancements |
| `frontend/src/lib/types.ts` | MODIFY | Priority type, Task interface |
| `frontend/src/components/TaskItem.tsx` | MODIFY | Visual indicators |
| `frontend/src/components/TaskForm.tsx` | MODIFY | New form fields |
| `frontend/src/components/TaskList.tsx` | MODIFY | Filter controls |
| `frontend/src/hooks/useTasks.ts` | MODIFY | Filter support |

## Implementation Phases

### Phase 1: Backend Data Layer
1. Create database migration (003_add_task_enhancements.py)
2. Update Task model with Priority enum and new fields
3. Update repository with filtered queries
4. Update service layer signatures
5. Run migration and verify

### Phase 2: Backend API Layer
1. Update POST /tasks to accept new fields
2. Update PUT /tasks/{id} to accept new fields
3. Add query parameters to GET /tasks
4. Add GET /tasks/categories endpoint
5. Write API tests

### Phase 3: AI/MCP Layer
1. Update MCP tool parameters
2. Update agent tool definitions
3. Enhance system prompt with interpretation guidelines
4. Test natural language task creation

### Phase 4: Frontend
1. Update TypeScript types
2. Update TaskForm with new fields
3. Update TaskItem with visual indicators
4. Update TaskList with filter controls
5. Update useTasks hook for filtering
6. Write component tests

## Complexity Tracking

> No constitution violations requiring justification.

| Aspect | Decision | Rationale |
|--------|----------|-----------|
| Priority storage | VARCHAR(10) | StrEnum serializes cleanly; allows DB indexing |
| Category storage | Free-text on Task | Spec allows custom categories; separate table is overkill |
| Due date handling | TIMESTAMP (UTC) | Consistent with existing datetime fields |
| Filtering | Query params | REST convention; backward compatible |

## Related Documents

- [spec.md](./spec.md) - Feature specification (27 requirements, 8 success criteria)
- [research.md](./research.md) - Technical research and decisions
- [data-model.md](./data-model.md) - Database schema changes
- [contracts/api.yaml](./contracts/api.yaml) - OpenAPI specification
- [contracts/types.ts](./contracts/types.ts) - TypeScript type definitions
- [contracts/mcp-tools.md](./contracts/mcp-tools.md) - MCP tool specifications
- [quickstart.md](./quickstart.md) - Implementation guide

## Next Steps

Run `/sp.tasks` to generate the detailed task breakdown for implementation.

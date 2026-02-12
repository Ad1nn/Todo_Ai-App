# Implementation Plan: In-Memory Console Todo App

**Branch**: `001-console-todo-app` | **Date**: 2026-01-18 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-console-todo-app/spec.md`

## Summary

Build a command-line todo application in Python that stores tasks in memory. The app provides CRUD operations (Create, Read, Update, Delete) plus completion status toggling via a text-based menu interface. All data is held in Python data structures (dict/list) and lost on application exit—this is expected Phase 1 behavior.

## Technical Context

**Language/Version**: Python 3.13+
**Primary Dependencies**: None (standard library only for Phase 1)
**Storage**: In-memory (Python dict keyed by task ID)
**Testing**: pytest with pytest-cov for coverage reporting
**Target Platform**: Cross-platform CLI (Linux, macOS, Windows terminal)
**Project Type**: Single project (console application)
**Performance Goals**: Interactive response (<100ms for all operations)
**Constraints**: No external databases, no async complexity, single-user only
**Scale/Scope**: Unlimited tasks (bounded only by available memory)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Spec-Driven Development | PASS | All code generated from this spec via Claude Code |
| II. Clean Code Principles | PASS | Single-responsibility modules, descriptive names planned |
| III. Python Best Practices | PASS | Python 3.13+, UV, type hints, ruff formatting |
| IV. Test-First Approach | PASS | pytest with >80% coverage target |
| V. Modular Architecture | PASS | Separate models, services, CLI layers |
| VI. Simplicity First | PASS | In-memory only, no premature abstractions |

**Gate Result**: PASS - Proceed to Phase 0

## Project Structure

### Documentation (this feature)

```text
specs/001-console-todo-app/
├── spec.md              # Feature specification (completed)
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output (internal API contracts)
│   └── task_service.py  # Service interface definition
├── checklists/
│   └── requirements.md  # Specification quality checklist (completed)
└── tasks.md             # Phase 2 output (/sp.tasks command)
```

### Source Code (repository root)

```text
src/
├── __init__.py
├── models/
│   ├── __init__.py
│   └── task.py          # Task dataclass with validation
├── services/
│   ├── __init__.py
│   └── task_service.py  # Business logic: CRUD + completion toggle
├── storage/
│   ├── __init__.py
│   └── memory_store.py  # In-memory dict-based storage
└── cli/
    ├── __init__.py
    ├── __main__.py      # Entry point
    └── menu.py          # Menu display and input handling

tests/
├── __init__.py
├── unit/
│   ├── __init__.py
│   ├── test_task.py           # Task model tests
│   ├── test_task_service.py   # Service logic tests
│   └── test_memory_store.py   # Storage tests
└── integration/
    ├── __init__.py
    └── test_cli.py            # End-to-end CLI tests

pyproject.toml           # UV project configuration
```

**Structure Decision**: Single project structure selected. Console app with clear separation:
- `models/` - Data structures (Task dataclass)
- `services/` - Business logic (TaskService)
- `storage/` - Data persistence abstraction (MemoryStore)
- `cli/` - User interface (menu-driven console)

## Complexity Tracking

> No violations identified. All design choices align with constitution principles.

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| None | N/A | N/A |

## Architecture Decisions

### AD-001: Storage Abstraction Layer

**Decision**: Create a `storage/` module with a `MemoryStore` class even though Phase 1 only uses in-memory storage.

**Rationale**: Constitution Principle V (Modular Architecture) states "In-memory storage for Phase 1; design for future persistence layer abstraction." This allows Phase 2+ to swap in database storage without changing service layer code.

**Interface**:
```python
class MemoryStore:
    def add(self, task: Task) -> Task
    def get(self, task_id: int) -> Task | None
    def get_all(self) -> list[Task]
    def update(self, task: Task) -> Task | None
    def delete(self, task_id: int) -> bool
    def next_id(self) -> int
```

### AD-002: Task Model as Dataclass

**Decision**: Use Python `dataclass` with `@dataclass` decorator for the Task entity.

**Rationale**: Dataclasses provide:
- Automatic `__init__`, `__repr__`, `__eq__`
- Type hints enforcement
- Immutability option via `frozen=True` (not used—tasks need mutation)
- Clean, readable code aligned with Clean Code Principles

### AD-003: Service Layer Pattern

**Decision**: All business logic resides in `TaskService`, not in CLI or storage layers.

**Rationale**:
- CLI handles user interaction only (input/output)
- Storage handles data persistence only
- Service orchestrates validation, business rules, and coordinates between layers
- Enables testing business logic without CLI or storage dependencies

## Module Responsibilities

| Module | Responsibility | Dependencies |
|--------|---------------|--------------|
| `models.task` | Task data structure, field validation | None |
| `storage.memory_store` | In-memory CRUD operations | `models.task` |
| `services.task_service` | Business logic, validation rules | `storage`, `models` |
| `cli.menu` | User interface, input parsing | `services` |
| `cli.__main__` | Application entry point | `cli.menu` |

## Dependency Flow

```text
cli.__main__ → cli.menu → services.task_service → storage.memory_store
                                                 ↓
                                            models.task
```

Dependencies flow inward (UI → Logic → Data). No circular dependencies.

## Error Handling Strategy

| Error Type | Handler | User Message |
|------------|---------|--------------|
| Task not found | TaskService | "Error: Task with ID {id} not found." |
| Empty title | TaskService | "Error: Task title cannot be empty." |
| Invalid ID input | CLI | "Error: Please enter a valid numeric ID." |
| Invalid menu choice | CLI | "Error: Invalid option. Please try again." |

## Testing Strategy

### Unit Tests (target: 90% coverage)

| Test File | Coverage Target | Key Scenarios |
|-----------|-----------------|---------------|
| `test_task.py` | 100% | Creation, validation, field access |
| `test_task_service.py` | 100% | All CRUD operations, error cases |
| `test_memory_store.py` | 100% | Storage operations, ID generation |

### Integration Tests

| Test File | Coverage Target | Key Scenarios |
|-----------|-----------------|---------------|
| `test_cli.py` | 80% | Full user workflows via simulated input |

### Test Commands

```bash
# Run all tests with coverage
uv run pytest --cov=src --cov-report=term-missing

# Run only unit tests
uv run pytest tests/unit/

# Run with verbose output
uv run pytest -v
```

## Quality Gates

Before proceeding to implementation, verify:

- [ ] All unit tests written before implementation (TDD)
- [ ] Tests pass: `uv run pytest`
- [ ] Linting passes: `uv run ruff check src/ tests/`
- [ ] Formatting passes: `uv run ruff format --check src/ tests/`
- [ ] Coverage >80%: `uv run pytest --cov=src --cov-fail-under=80`

## Post-Design Constitution Re-Check

| Principle | Status | Evidence |
|-----------|--------|----------|
| I. Spec-Driven Development | PASS | Plan derives entirely from spec.md requirements |
| II. Clean Code Principles | PASS | Single-responsibility modules, clear naming |
| III. Python Best Practices | PASS | 3.13+, UV, type hints in all interfaces |
| IV. Test-First Approach | PASS | Test files defined, TDD workflow planned |
| V. Modular Architecture | PASS | 4 layers with inward dependencies |
| VI. Simplicity First | PASS | Minimal viable structure, no over-engineering |

**Final Gate Result**: PASS - Ready for Phase 0 research and Phase 1 design artifacts

# Research: In-Memory Console Todo App

**Feature**: 001-console-todo-app | **Date**: 2026-01-18 | **Phase**: 0

## Purpose

Document research findings and decisions for implementing the Phase 1 Console Todo App. Since this is a straightforward in-memory Python application with no external dependencies, research focuses on Python best practices and project structure.

## Research Tasks

### RT-001: Python 3.13+ Features

**Question**: Which Python 3.13+ features should we leverage?

**Findings**:
- Type hints with `|` union syntax (e.g., `Task | None` instead of `Optional[Task]`)
- Dataclasses with `@dataclass` decorator for clean model definitions
- f-strings for string formatting
- Walrus operator `:=` where it improves readability
- `match` statement for menu handling (cleaner than if/elif chains)

**Decision**: Use modern Python syntax throughout. Minimum version 3.13 enforced in pyproject.toml.

**Rationale**: Constitution Principle III mandates Python 3.13+ and modern features.

---

### RT-002: UV Package Manager Setup

**Question**: How to structure a UV-managed Python project?

**Findings**:
- UV uses `pyproject.toml` for project configuration (PEP 621 compliant)
- Virtual environment created automatically with `uv venv`
- Dependencies installed with `uv add <package>`
- Run commands with `uv run <command>`
- Lock file generated as `uv.lock`

**Decision**: Standard UV project structure with `pyproject.toml`, `src/` layout, and `tests/` directory.

**Configuration**:
```toml
[project]
name = "todo-app"
version = "0.1.0"
requires-python = ">=3.13"

[project.scripts]
todo = "src.cli.__main__:main"

[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["."]

[tool.ruff]
line-length = 88
target-version = "py313"

[tool.ruff.lint]
select = ["E", "F", "I", "UP"]
```

**Rationale**: Aligns with Constitution Principle III (UV required) and industry standards.

---

### RT-003: Testing Framework Configuration

**Question**: How to configure pytest for this project?

**Findings**:
- pytest is the de facto Python testing standard
- pytest-cov provides coverage reporting
- Fixtures enable clean test setup
- Parametrized tests reduce duplication

**Decision**: pytest with pytest-cov, fixtures for service/store instances.

**Dependencies**:
```toml
[project.optional-dependencies]
dev = [
    "pytest>=8.0",
    "pytest-cov>=4.0",
    "ruff>=0.5"
]
```

**Rationale**: Constitution Principle IV mandates pytest and >80% coverage.

---

### RT-004: In-Memory Storage Pattern

**Question**: Best pattern for in-memory task storage?

**Alternatives Considered**:

| Pattern | Pros | Cons |
|---------|------|------|
| Simple dict | Fast lookup by ID, minimal code | Requires manual ID tracking |
| List with linear search | Simple iteration | O(n) lookups |
| SQLite :memory: | SQL interface, easy migration | Over-engineering for Phase 1 |
| dataclasses + dict | Type safety, fast lookup | Slightly more code |

**Decision**: Python dict with integer keys (task IDs), Task dataclass values.

**Rationale**:
- O(1) lookup by ID (most common operation)
- Simple iteration for "view all"
- Aligns with Constitution Principle VI (Simplicity First)
- Easy to swap with database in Phase 2

---

### RT-005: CLI Input Handling

**Question**: How to handle user input robustly?

**Findings**:
- `input()` is sufficient for simple console apps
- Try/except for type conversion errors
- `match` statement for menu routing
- Empty string checks for validation

**Decision**: Standard `input()` with validation in CLI layer, business logic validation in service layer.

**Rationale**: No external dependencies needed. Keeps CLI focused on I/O, service on validation.

---

### RT-006: Project Structure Best Practices

**Question**: What's the recommended Python project layout?

**Findings**:
- `src/` layout prevents import confusion
- `__init__.py` files make packages explicit
- Separate `tests/` directory with mirrored structure
- Entry point in `__main__.py` enables `python -m` execution

**Decision**: Flat `src/` layout with models/, services/, storage/, cli/ packages.

**Rationale**: Constitution Principle V (Modular Architecture) and Python community standards.

---

## Summary

| Decision | Choice | Key Rationale |
|----------|--------|---------------|
| Python version | 3.13+ | Constitution requirement |
| Package manager | UV | Constitution requirement |
| Data model | dataclass | Type safety, clean code |
| Storage | dict[int, Task] | O(1) lookup, simplicity |
| Testing | pytest + coverage | Constitution requirement |
| Code quality | ruff format + check | Constitution requirement |

## Unresolved Questions

None. All technical decisions are clear for Phase 1 scope.

## References

- [UV Documentation](https://docs.astral.sh/uv/)
- [Python dataclasses](https://docs.python.org/3/library/dataclasses.html)
- [pytest Documentation](https://docs.pytest.org/)
- [Ruff Documentation](https://docs.astral.sh/ruff/)

# Quickstart Guide: Console Todo App

**Feature**: 001-console-todo-app | **Date**: 2026-01-18 | **Phase**: 1

## Prerequisites

- Python 3.13 or higher
- UV package manager installed ([install UV](https://docs.astral.sh/uv/getting-started/installation/))

## Setup

### 1. Initialize Project

```bash
# Create and enter project directory (if not already in repo)
cd /path/to/hackathon2

# Initialize UV project (creates pyproject.toml if not exists)
uv init --name todo-app

# Create virtual environment
uv venv

# Activate virtual environment
# Linux/macOS:
source .venv/bin/activate
# Windows:
.venv\Scripts\activate
```

### 2. Install Dependencies

```bash
# Install dev dependencies (pytest, ruff)
uv add --dev pytest pytest-cov ruff
```

### 3. Project Structure

After implementation, the project will have this structure:

```
hackathon2/
├── pyproject.toml
├── src/
│   ├── __init__.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── task.py
│   ├── services/
│   │   ├── __init__.py
│   │   └── task_service.py
│   ├── storage/
│   │   ├── __init__.py
│   │   └── memory_store.py
│   └── cli/
│       ├── __init__.py
│       ├── __main__.py
│       └── menu.py
└── tests/
    ├── __init__.py
    ├── unit/
    │   ├── __init__.py
    │   ├── test_task.py
    │   ├── test_task_service.py
    │   └── test_memory_store.py
    └── integration/
        ├── __init__.py
        └── test_cli.py
```

## Running the Application

```bash
# Run the todo app
uv run python -m src.cli

# Or if entry point is configured in pyproject.toml:
uv run todo
```

## Usage

The application presents a menu-driven interface:

```
=== Todo App ===
1. Add Task
2. View All Tasks
3. Mark Task Complete/Incomplete
4. Update Task
5. Delete Task
6. Exit

Select an option (1-6):
```

### Adding a Task

```
Select an option (1-6): 1
Enter task title: Buy groceries
Enter task description (optional): Milk, eggs, bread
Task added successfully with ID 1.
```

### Viewing Tasks

```
Select an option (1-6): 2

ID  | Status | Title           | Description
----|--------|-----------------|---------------------------
1   | [ ]    | Buy groceries   | Milk, eggs, bread
2   | [x]    | Call mom        |
```

### Marking Complete

```
Select an option (1-6): 3
Enter task ID: 1
Task 1 marked as complete.
```

### Updating a Task

```
Select an option (1-6): 4
Enter task ID: 1
Enter new title (press Enter to keep current): Buy organic groceries
Enter new description (press Enter to keep current):
Task 1 updated successfully.
```

### Deleting a Task

```
Select an option (1-6): 5
Enter task ID: 1
Task 1 deleted successfully.
```

## Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=src --cov-report=term-missing

# Run only unit tests
uv run pytest tests/unit/

# Run with verbose output
uv run pytest -v
```

## Code Quality

```bash
# Check code style
uv run ruff check src/ tests/

# Auto-fix issues
uv run ruff check --fix src/ tests/

# Format code
uv run ruff format src/ tests/

# Check formatting without changes
uv run ruff format --check src/ tests/
```

## Troubleshooting

### "Module not found" errors

Ensure you're running from the project root and using `uv run`:

```bash
cd /path/to/hackathon2
uv run python -m src.cli
```

### UV not found

Install UV following the [official guide](https://docs.astral.sh/uv/getting-started/installation/):

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### Python version issues

Ensure Python 3.13+ is installed:

```bash
python --version
# Should show Python 3.13.x or higher

# If not, install via pyenv or your system package manager
```

## Next Steps

After completing Phase 1:
1. All tests should pass with >80% coverage
2. Code should pass ruff linting and formatting
3. Ready for Phase 2: Full-Stack Web Application

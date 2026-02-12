# Todo Backend

FastAPI backend for the Todo application.

## Setup

```bash
uv sync
cp .env.example .env
# Edit .env with your database credentials
uv run alembic upgrade head
uv run uvicorn src.main:app --reload
```

## API Docs

Visit http://localhost:8000/docs for interactive API documentation.

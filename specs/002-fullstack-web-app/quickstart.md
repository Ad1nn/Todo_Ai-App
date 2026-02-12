# Quickstart: Full-Stack Web Todo Application

**Feature**: 002-fullstack-web-app
**Date**: 2026-01-20

## Prerequisites

- Python 3.13+
- Node.js 20+
- UV package manager (Python)
- npm or pnpm (Node.js)
- Neon PostgreSQL account (or local PostgreSQL for development)

## Project Setup

### 1. Clone and Navigate

```bash
cd hackathon2
git checkout 002-fullstack-web-app
```

### 2. Backend Setup

```bash
# Navigate to backend
cd backend

# Create virtual environment and install dependencies
uv sync

# Copy environment template
cp .env.example .env

# Edit .env with your database credentials
# DATABASE_URL=postgresql+asyncpg://user:pass@host/db
# JWT_SECRET=your-32-char-random-string

# Run database migrations
uv run alembic upgrade head

# Start development server
uv run uvicorn src.main:app --reload --port 8000
```

Backend will be available at: `http://localhost:8000`
API docs at: `http://localhost:8000/docs`

### 3. Frontend Setup

```bash
# Navigate to frontend (from project root)
cd frontend

# Install dependencies
npm install

# Copy environment template
cp .env.local.example .env.local

# Edit .env.local
# NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1

# Start development server
npm run dev
```

Frontend will be available at: `http://localhost:3000`

## Environment Variables

### Backend (.env)

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| DATABASE_URL | Yes | - | PostgreSQL connection string (asyncpg) |
| JWT_SECRET | Yes | - | Secret key for JWT signing (32+ chars) |
| JWT_ALGORITHM | No | HS256 | JWT signing algorithm |
| JWT_EXPIRATION_HOURS | No | 24 | Token expiration in hours |
| CORS_ORIGINS | No | ["http://localhost:3000"] | Allowed CORS origins |

### Frontend (.env.local)

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| NEXT_PUBLIC_API_URL | Yes | - | Backend API base URL |

## Running Tests

### Backend Tests

```bash
cd backend

# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=src --cov-report=term-missing

# Run specific test file
uv run pytest tests/unit/test_auth_service.py
```

### Frontend Tests

```bash
cd frontend

# Run all tests
npm test

# Run with coverage
npm test -- --coverage

# Run in watch mode
npm test -- --watch
```

## Development Commands

### Backend

```bash
# Format code
uv run ruff format src tests

# Lint code
uv run ruff check src tests

# Create new migration
uv run alembic revision --autogenerate -m "description"

# Apply migrations
uv run alembic upgrade head

# Rollback migration
uv run alembic downgrade -1
```

### Frontend

```bash
# Format code
npm run format

# Lint code
npm run lint

# Type check
npm run typecheck

# Build for production
npm run build
```

## API Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | /api/v1/auth/register | No | Register new user |
| POST | /api/v1/auth/login | No | Login user |
| POST | /api/v1/auth/logout | Yes | Logout user |
| GET | /api/v1/auth/me | Yes | Get current user |
| GET | /api/v1/tasks | Yes | List user's tasks |
| POST | /api/v1/tasks | Yes | Create task |
| GET | /api/v1/tasks/{id} | Yes | Get task |
| PUT | /api/v1/tasks/{id} | Yes | Update task |
| DELETE | /api/v1/tasks/{id} | Yes | Delete task |
| PATCH | /api/v1/tasks/{id}/toggle | Yes | Toggle completion |

## Validation Checklist

After setup, verify:

- [ ] Backend server starts without errors
- [ ] API docs accessible at `/docs`
- [ ] Frontend server starts without errors
- [ ] Can register a new user
- [ ] Can login with registered user
- [ ] Can create a task
- [ ] Can view task list
- [ ] Can toggle task completion
- [ ] Can update task
- [ ] Can delete task
- [ ] Can logout
- [ ] Cannot access tasks without login

## Troubleshooting

### Database Connection Issues

1. Verify DATABASE_URL format: `postgresql+asyncpg://user:pass@host:port/dbname`
2. Check Neon console for connection limits
3. Ensure SSL mode if required: `?sslmode=require`

### CORS Errors

1. Verify CORS_ORIGINS includes frontend URL
2. Check for trailing slashes in URLs
3. Ensure credentials mode matches

### JWT Issues

1. Verify JWT_SECRET is at least 32 characters
2. Check token expiration settings
3. Ensure Authorization header format: `Bearer <token>`

### Frontend Build Errors

1. Clear `.next` directory: `rm -rf .next`
2. Clear node_modules: `rm -rf node_modules && npm install`
3. Check TypeScript errors: `npm run typecheck`

# Research: Full-Stack Web Todo Application

**Feature**: 002-fullstack-web-app
**Date**: 2026-01-20
**Phase**: 0 - Research

## Technology Decisions

### 1. Backend Framework: FastAPI

**Decision**: Use FastAPI as the Python web framework

**Rationale**:
- Native async support for high concurrency
- Automatic OpenAPI documentation generation
- Built-in request validation via Pydantic
- Type hints integration aligns with constitution requirements
- Excellent performance benchmarks

**Alternatives Considered**:
- Django REST Framework: More batteries-included but heavier, unnecessary for MVP
- Flask: Simpler but lacks native async and validation
- Litestar: Good alternative but smaller ecosystem

### 2. ORM: SQLModel

**Decision**: Use SQLModel for database interactions

**Rationale**:
- Combines SQLAlchemy's power with Pydantic's validation
- Single model definition for DB and API schemas
- Type-safe queries
- First-class FastAPI integration (same author)
- Reduces code duplication between models and schemas

**Alternatives Considered**:
- SQLAlchemy alone: More verbose, requires separate Pydantic schemas
- Tortoise ORM: Good async support but less mature
- Piccolo: Modern but smaller ecosystem

### 3. Database: Neon PostgreSQL

**Decision**: Use Neon serverless PostgreSQL

**Rationale**:
- Serverless scaling (cost-effective for MVP)
- PostgreSQL compatibility (industry standard)
- Branching for development/staging environments
- Auto-suspend on inactivity (cost savings)
- Connection pooling included

**Alternatives Considered**:
- Supabase: Good but adds unnecessary auth layer (using Better Auth)
- PlanetScale: MySQL-based, prefer PostgreSQL ecosystem
- Local PostgreSQL: Requires hosting management

### 4. Authentication: Better Auth + JWT

**Decision**: Use Better Auth library with JWT tokens

**Rationale**:
- Framework-agnostic auth library
- JWT token generation and validation
- Password hashing with bcrypt included
- Session management built-in
- TypeScript-first (good for frontend integration)

**Alternatives Considered**:
- Auth0: External dependency, overkill for MVP
- Firebase Auth: Vendor lock-in
- Custom implementation: Security risk, reinventing wheel
- Passport.js: Node.js only, doesn't fit Python backend

**Implementation Note**: Better Auth will be used on the frontend for session management. Backend will use python-jose for JWT validation and passlib for password hashing to maintain Python-native implementation.

### 5. Frontend Framework: Next.js 15+ (App Router)

**Decision**: Use Next.js with App Router architecture

**Rationale**:
- React Server Components for performance
- Built-in routing and layouts
- SSR/SSG for SEO and initial load performance
- API routes for BFF pattern if needed
- Large ecosystem and community
- TypeScript first-class support

**Alternatives Considered**:
- Remix: Good but smaller ecosystem
- SvelteKit: Different paradigm, React more common
- Vite + React: No SSR out of box

### 6. Styling: Tailwind CSS

**Decision**: Use Tailwind CSS for styling

**Rationale**:
- Utility-first approach reduces CSS complexity
- No class naming decisions
- Responsive design utilities built-in
- Works well with component architecture
- Smaller final bundle (purges unused styles)

**Alternatives Considered**:
- CSS Modules: More boilerplate
- Styled Components: Runtime overhead
- Chakra UI: Additional dependency, opinionated

### 7. State Management: React Hooks + SWR

**Decision**: Use React hooks with SWR for server state

**Rationale**:
- SWR provides caching, revalidation, error handling
- Minimal boilerplate compared to Redux
- Optimistic updates for better UX
- Built-in request deduplication
- Perfect for CRUD operations

**Alternatives Considered**:
- Redux Toolkit + RTK Query: Overkill for this scope
- TanStack Query: Similar to SWR, either works
- Zustand: Good for client state, SWR better for server state

## Security Implementation

### Password Hashing

**Decision**: bcrypt with cost factor 12

**Rationale**:
- Industry standard for password hashing
- Adaptive cost factor protects against hardware improvements
- Cost 12 balances security and performance (~250ms)

### JWT Configuration

**Decision**: HS256 algorithm, 24-hour expiration

**Rationale**:
- HS256 simpler than RS256 for single-service auth
- 24-hour expiration balances security and UX
- Refresh tokens not needed for MVP (re-login acceptable)

### Input Validation

**Decision**: Pydantic (backend) + Zod (frontend)

**Rationale**:
- Both provide schema-based validation
- Type generation from schemas
- Consistent validation on both ends

## API Design

### Endpoint Structure

**Decision**: RESTful with `/api/v1/` prefix

```
POST   /api/v1/auth/register    - User registration
POST   /api/v1/auth/login       - User login
POST   /api/v1/auth/logout      - User logout
GET    /api/v1/tasks            - List user's tasks
POST   /api/v1/tasks            - Create task
GET    /api/v1/tasks/{id}       - Get single task
PUT    /api/v1/tasks/{id}       - Update task
DELETE /api/v1/tasks/{id}       - Delete task
PATCH  /api/v1/tasks/{id}/toggle - Toggle completion
```

**Rationale**:
- Standard REST patterns
- Versioned for future compatibility
- Separate toggle endpoint for atomic operation

### Error Response Format

**Decision**: Structured JSON errors

```json
{
  "detail": "Human-readable message",
  "code": "MACHINE_READABLE_CODE",
  "field": "optional_field_name"
}
```

**Rationale**:
- Consistent error handling
- Machine-readable codes for frontend logic
- Field-specific errors for form validation

## Testing Strategy

### Backend Testing

**Decision**: pytest + httpx + pytest-asyncio

**Rationale**:
- pytest is constitution requirement
- httpx provides async test client
- Fixtures for database isolation

**Coverage Target**: 80% business logic

### Frontend Testing

**Decision**: Jest + React Testing Library

**Rationale**:
- Jest is Next.js default
- RTL encourages testing user behavior
- Component + integration tests

**Coverage Target**: 80% component logic

## Database Schema Design

### Migration Strategy

**Decision**: Alembic with auto-generation

**Rationale**:
- SQLAlchemy integration
- Reversible migrations (up/down)
- Version control for schema changes

### Connection Pooling

**Decision**: SQLModel async session with Neon's built-in pooling

**Rationale**:
- Neon handles connection pooling
- Async sessions for non-blocking I/O
- Context manager for automatic cleanup

## CORS Configuration

**Decision**: Allow frontend origin only in production

**Rationale**:
- Security: Only trusted origins
- Development: localhost:3000 allowed
- Credentials: Enabled for JWT cookies

## Environment Configuration

### Backend (.env)

```
DATABASE_URL=postgresql+asyncpg://...
JWT_SECRET=<32+ char random string>
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24
CORS_ORIGINS=["http://localhost:3000"]
```

### Frontend (.env.local)

```
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

## Outstanding Decisions

All technical decisions resolved. No NEEDS CLARIFICATION items remaining.

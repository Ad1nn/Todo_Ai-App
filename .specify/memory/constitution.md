<!--
Sync Impact Report
==================
Version change: 1.4.0 → 1.5.0 (MINOR - adding Event-Driven & Cloud Deployment Principles for Phase 5)
Modified principles:
  - None renamed
Added sections:
  - New Principle XII: Event-Driven Architecture Principles (Kafka, Dapr)
  - New Principle XIII: Advanced Task Features (Recurring Tasks, Notifications)
  - New Principle XIV: Cloud Deployment & CI/CD Principles (DigitalOcean DOKS, GitHub Actions)
  - Technology Stack: Phase 5 Requirements (Advanced Cloud Deployment)
  - Development Workflow: Phase 5 section
  - Quality Gates: Phase 5 validation checklist items
Removed sections: None
Templates requiring updates:
  - plan-template.md: ✅ Compatible (supports event-driven and cloud deployment planning)
  - spec-template.md: ✅ Compatible (supports advanced feature requirements)
  - tasks-template.md: ✅ Compatible (supports infrastructure/deployment/event tasks)
Follow-up TODOs: None
-->

# Evolution of Todo Constitution

## Core Principles

### I. Spec-Driven Development (NON-NEGOTIABLE)

All implementation code MUST be generated via Claude Code from approved specifications.

- **No manual coding allowed**: Code MUST be produced by refining specifications until Claude Code generates correct output
- Specifications MUST be written and approved before any implementation begins
- The workflow is: Specify → Plan → Tasks → Implement via Claude Code
- Every code change MUST trace back to a specification requirement or task
- If Claude Code produces incorrect output, refine the specification—do not manually edit generated code

### II. Clean Code Principles

Code MUST be readable, maintainable, and follow established language conventions.

- Functions and classes MUST have single, clear responsibilities
- Names MUST be descriptive and self-documenting (no abbreviations without context)
- Functions SHOULD be under 20 lines; files SHOULD be under 200 lines
- No code duplication—extract common patterns into reusable functions
- Comments explain "why" not "what"—code should be self-explanatory

### III. Language Best Practices

All code MUST follow modern standards and tooling for the respective language.

**Python (Backend):**
- **Runtime**: Python 3.13+ required
- **Package Manager**: UV MUST be used for dependency management
- **Type Hints**: All functions MUST include type annotations
- **Formatting**: Code MUST pass `ruff format` and `ruff check`
- **Project Structure**: Follow standard Python package layout with `src/` directory

**TypeScript/JavaScript (Frontend):**
- **Runtime**: Node.js 20+ / Next.js 15+
- **Package Manager**: npm or pnpm
- **Type Safety**: TypeScript MUST be used; `strict` mode enabled
- **Formatting**: Code MUST pass ESLint and Prettier checks
- **Project Structure**: Follow Next.js App Router conventions

### IV. Test-First Approach

Tests MUST be written before implementation code.

- Write failing tests that define expected behavior
- Implement only enough code to make tests pass
- Refactor while keeping tests green
- Test coverage SHOULD exceed 80% for business logic
- **Backend**: Use pytest as the testing framework
- **Frontend**: Use Jest/Vitest and React Testing Library
- **MCP Tools**: Test each tool function independently with mock data

### V. Modular Architecture

Code MUST be organized into loosely-coupled, cohesive modules.

- Separate concerns: data models, business logic, API layer, user interface
- Each module MUST have a clear, documented public interface
- Dependencies flow inward (UI → API → Services → Models)
- No circular dependencies between modules
- **Phase 1**: In-memory storage (Python dict)
- **Phase 2**: PostgreSQL via SQLModel ORM with repository pattern abstraction
- **Phase 3**: MCP Server as separate module exposing task operations as tools
- **Phase 5**: Event producers/consumers as separate services communicating via Kafka

### VI. Simplicity First (YAGNI)

Start with the simplest solution that works; add complexity only when needed.

- Implement only features specified in the current phase requirements
- No premature optimization—make it work, then make it fast (if needed)
- No speculative features or "nice to have" additions
- If unsure between two approaches, choose the simpler one
- Refactor incrementally as requirements evolve

### VII. API Design Principles (Phase 2+)

REST APIs and Chat APIs MUST follow consistent, predictable patterns.

**REST Endpoints:**
- Use standard HTTP methods: GET (read), POST (create), PUT/PATCH (update), DELETE (remove)
- Return appropriate HTTP status codes (200, 201, 400, 401, 404, 500)
- Use JSON for request/response bodies
- Endpoints MUST be versioned (e.g., `/api/v1/`)
- All endpoints MUST require authentication except explicit public routes
- Error responses MUST include structured error messages

**Chat Endpoints (Phase 3+):**
- Chat endpoint: `POST /api/{user_id}/chat` for natural language interactions
- Request MUST include `message` (required) and `conversation_id` (optional)
- Response MUST include `conversation_id`, `response`, and `tool_calls` array
- Server MUST be stateless—conversation state persisted to database
- Each request MUST fetch conversation history, process, and store results

### VIII. Security Principles (Phase 2+)

Security MUST be built-in, not bolted-on.

- Never store plaintext passwords—use proper hashing (bcrypt/argon2)
- All API endpoints MUST validate and sanitize input
- Use parameterized queries—no string concatenation for SQL
- JWT tokens MUST have appropriate expiration times
- Secrets MUST be stored in environment variables, never in code
- CORS MUST be configured to allow only trusted origins
- **AI/LLM Security (Phase 3+)**:
  - API keys (OpenAI, etc.) MUST be stored securely in environment variables
  - User input to AI MUST be validated before processing
  - AI responses MUST be validated before database operations
  - MCP tools MUST enforce user isolation (user can only access own tasks)

### IX. AI Agent Design Principles (Phase 3+)

AI agents MUST be predictable, auditable, and user-controlled.

**MCP Server Design:**
- Each MCP tool MUST have a single, clear purpose
- Tool parameters MUST include `user_id` for ownership enforcement
- Tool responses MUST include `task_id`, `status`, and relevant data
- Tools MUST be stateless—all state stored in database
- Error handling MUST return structured error messages to the agent

**Agent Behavior:**
- Agent MUST confirm actions with friendly responses
- Agent MUST gracefully handle "task not found" and other errors
- Agent MUST use appropriate tools based on user intent:
  - "add/create/remember" → `add_task`
  - "show/list/view" → `list_tasks`
  - "done/complete/finished" → `complete_task`
  - "delete/remove/cancel" → `delete_task`
  - "change/update/rename" → `update_task`

**Conversation Management:**
- Conversations MUST be persisted to database
- Each message MUST include role (user/assistant) and content
- Conversation history MUST be loaded on each request for context
- Server restart MUST NOT lose conversation state

### X. UI/UX Design Principles

User interfaces MUST be intuitive, accessible, and visually polished.

**Visual Design:**
- Use a consistent design system with defined color palette, typography, and spacing
- Primary colors MUST have sufficient contrast ratios (WCAG AA minimum: 4.5:1)
- Typography MUST use a readable font stack with appropriate sizing (base: 16px)
- Spacing MUST follow a consistent scale (4px, 8px, 16px, 24px, 32px, 48px)
- Components MUST have clear visual hierarchy and focus states
- Dark mode SHOULD be supported with appropriate color adjustments

**Layout & Responsiveness:**
- Mobile-first design approach—start with smallest screens
- Breakpoints: sm (640px), md (768px), lg (1024px), xl (1280px)
- Touch targets MUST be minimum 44x44px on mobile devices
- Content MUST be readable without horizontal scrolling on any viewport
- Navigation MUST be accessible on all screen sizes (hamburger menu on mobile)

**Interaction Design:**
- Provide immediate visual feedback for all user actions
- Loading states MUST be displayed for operations > 300ms
- Success/error states MUST be clearly communicated with color and icons
- Form validation MUST show inline errors near the relevant field
- Destructive actions MUST require confirmation
- Animations SHOULD be subtle (200-300ms) and respect reduced-motion preferences

**Accessibility (WCAG 2.1 AA):**
- All interactive elements MUST be keyboard navigable
- Focus indicators MUST be visible (minimum 2px outline)
- Images MUST have descriptive alt text
- Form inputs MUST have associated labels
- Color alone MUST NOT convey information—use icons/text as well
- Screen reader announcements for dynamic content changes

**Component Patterns:**
- Use established UI patterns (cards, modals, dropdowns, toasts)
- Buttons: primary (main action), secondary (alternative), ghost (subtle), danger (destructive)
- Forms: clear labels, placeholder hints, validation feedback, submit/cancel actions
- Lists: consistent item spacing, hover/selected states, empty states
- Modals: backdrop overlay, close button, escape key dismissal, focus trap
- Toast notifications: auto-dismiss (5s), manual dismiss option, stacking behavior

**Chat Interface (Phase 3+):**
- Message bubbles: user (right-aligned, primary color), assistant (left-aligned, neutral)
- Typing indicator during AI response generation
- Timestamp display (relative time: "2m ago", "Yesterday")
- Message history with smooth scroll and load-more pagination
- Input area: multi-line support, send button, keyboard shortcut (Enter to send)
- Tool call visualization (collapsible, shows action taken)

### XI. Container & Orchestration Principles (Phase 4+)

Applications MUST be containerized and orchestrated for consistent, scalable deployment.

**Docker Containerization:**
- All services MUST have a `Dockerfile` in their root directory
- Dockerfiles MUST use multi-stage builds to minimize image size
- Base images MUST use slim/alpine variants where possible (e.g., `python:3.13-slim`)
- Dependencies MUST be installed in a separate layer before copying application code
- Container images MUST NOT include development dependencies or tools
- Secrets MUST NOT be baked into images—use environment variables or mounted secrets
- Each image MUST expose only necessary ports via `EXPOSE` directive
- Images MUST be tagged with semantic versions (not just `latest`)

**Kubernetes Orchestration:**
- All deployable services MUST have Kubernetes manifests (via Helm charts)
- Deployments MUST specify resource requests and limits
- Pods MUST include liveness and readiness probes
- Services MUST use appropriate types: ClusterIP (internal), NodePort/LoadBalancer (external)
- Sensitive configuration MUST use Kubernetes Secrets (not ConfigMaps)
- Non-sensitive configuration SHOULD use ConfigMaps for easy updates
- Pod replicas SHOULD be configurable via values (default: 1 for local, 2+ for production)

**Helm Chart Standards:**
- Charts MUST follow standard structure: `Chart.yaml`, `values.yaml`, `templates/`
- All configurable values MUST be documented in `values.yaml` with comments
- Templates MUST use helper functions in `_helpers.tpl` for name generation
- Charts MUST include `NOTES.txt` for post-install instructions
- Values MUST allow override of image repository, tag, and pull policy
- Secrets MUST be passed via `--set` flags, never committed to values.yaml

**Health & Observability:**
- All services MUST expose a `/health` endpoint for Kubernetes probes
- Liveness probe: Restart container if unhealthy (check if process is alive)
- Readiness probe: Remove from load balancer if not ready (check dependencies)
- Initial delay MUST account for application startup time
- Probe timeouts MUST be reasonable (5s) with appropriate failure thresholds (3)

**Local Development:**
- Docker Desktop Kubernetes OR Minikube MUST be supported for local testing
- `imagePullPolicy: Never` MUST be used for locally-built images
- Port-forwarding or NodePort MUST be used to access services locally
- A deployment script SHOULD automate: build images → create namespace → helm install

**Security in Containers:**
- Containers MUST run as non-root user where possible
- Read-only root filesystem SHOULD be enabled for production
- Network policies SHOULD restrict pod-to-pod communication to necessary paths
- Image scanning SHOULD be performed before deployment

### XII. Event-Driven Architecture Principles (Phase 5+)

Applications MUST use event-driven patterns for decoupled, scalable communication between services.

**Kafka Message Streaming:**
- Kafka MUST be used as the primary message broker for event streaming
- All events MUST be published to well-defined topics with clear naming conventions
- Topic naming: `<domain>.<entity>.<action>` (e.g., `todo.task.reminder`, `todo.task.audit`)
- Events MUST include: `event_type`, `timestamp`, `user_id`, `payload`
- Producers MUST NOT wait for consumer acknowledgment (fire-and-forget for non-critical)
- Consumers MUST be idempotent—processing the same event twice produces the same result
- Consumer groups MUST be used for load balancing across service replicas

**Dapr Integration:**
- Dapr MUST be used to abstract infrastructure concerns from application code
- **Pub/Sub**: Application publishes to Dapr sidecar via HTTP; Dapr routes to Kafka
- **State Management**: Conversation state MAY use Dapr state store for caching
- **Bindings**: Dapr cron bindings SHOULD trigger scheduled operations (e.g., reminder checks)
- **Secrets**: Dapr secrets API MUST be used to retrieve sensitive configuration
- Application code MUST NOT directly depend on Kafka client libraries—use Dapr APIs
- Dapr component YAML files MUST be version-controlled in `dapr/components/`

**Event Topics for Todo App:**
- `todo.reminders`: Task due date approaching → Notification service consumes
- `todo.audit`: All task operations (create, update, delete, complete) → Audit service consumes
- Event payloads MUST be JSON with schema versioning (`"schema_version": "1.0"`)

**Event Processing Patterns:**
- Reminder System: When task due date is set, schedule reminder event via Dapr Jobs API
- Audit Logging: Every MCP tool call publishes audit event with user_id, action, task_id
- Consumers MUST handle failures gracefully with retry logic (3 attempts, exponential backoff)
- Dead letter queues SHOULD capture events that fail all retry attempts

**Local Development:**
- Dapr MUST be installed and initialized locally (`dapr init`)
- Local Kafka via Redpanda (single binary, Kafka-compatible) for simplicity
- `dapr run` MUST be used to start services with sidecars locally
- Docker Compose MAY be used to run Kafka/Redpanda + Dapr locally before K8s deployment

### XIII. Advanced Task Features Principles (Phase 5+)

Task management MUST support recurring tasks and in-app notifications.

**Recurring Tasks:**
- Tasks MUST support optional recurrence patterns: daily, weekly, monthly
- Recurrence MUST be stored as a `recurrence_rule` field (enum: none, daily, weekly, monthly)
- When a recurring task is completed, the system MUST auto-create the next occurrence
- Next occurrence date calculation:
  - Daily: due_date + 1 day
  - Weekly: due_date + 7 days
  - Monthly: due_date + 1 month (same day, or last day if month is shorter)
- Original task remains completed; new task created with same title, description, category, priority
- Recurring task creation MUST be triggered by task completion event (via Kafka)
- Users MUST be able to stop recurrence by editing the task to remove recurrence rule

**In-App Notifications:**
- Notification system MUST support toast messages and a notification bell/center
- Notifications MUST be stored in database with: user_id, type, title, message, read, created_at
- Notification types: `reminder` (task due soon), `system` (general info), `action` (task completed)
- Toast notifications MUST auto-dismiss after 5 seconds with manual dismiss option
- Notification bell MUST display unread count badge (max display: 99+)
- Notification center MUST list recent notifications with mark-as-read functionality
- Reminder notifications MUST be created when task due date is within 24 hours
- Reminder check SHOULD run via Dapr cron binding (every 15 minutes)

**Notification Delivery Flow:**
1. Dapr cron binding triggers reminder check service
2. Service queries tasks due within 24 hours that haven't been notified
3. For each task, publish reminder event to `todo.reminders` topic
4. Notification consumer creates notification record in database
5. Frontend polls or uses WebSocket to fetch new notifications
6. Toast displayed for new notifications; bell badge updated

**AI Integration for Recurring Tasks:**
- AI agent MUST understand recurrence in natural language:
  - "add daily task standup meeting" → recurrence_rule: daily
  - "add weekly task review PRs every Monday" → recurrence_rule: weekly
  - "remind me monthly to pay rent" → recurrence_rule: monthly
- MCP tools MUST include `recurrence_rule` parameter in add_task and update_task

### XIV. Cloud Deployment & CI/CD Principles (Phase 5+)

Production deployment MUST use managed Kubernetes with automated CI/CD pipelines.

**DigitalOcean Kubernetes (DOKS):**
- DigitalOcean Kubernetes Service (DOKS) MUST be used for production deployment
- Cluster configuration:
  - Minimum: 2 nodes for high availability
  - Node size: Basic (2 vCPU, 4GB RAM) for cost efficiency
  - Region: Choose closest to target users (e.g., NYC, SFO, AMS)
- `doctl` CLI MUST be used for cluster management and `kubectl` context setup
- Container registry: DigitalOcean Container Registry (DOCR) for private images
- Load Balancer: DigitalOcean Load Balancer via Kubernetes Service type `LoadBalancer`

**CI/CD with GitHub Actions:**
- All deployments MUST be automated via GitHub Actions workflows
- Workflow triggers:
  - Push to `main` branch → Deploy to production
  - Pull request → Run tests and build validation only
- CI pipeline stages:
  1. Lint and type check (ruff, eslint, tsc)
  2. Run tests (pytest, jest)
  3. Build Docker images
  4. Push images to container registry
  5. Deploy to Kubernetes via Helm
- Secrets (DIGITALOCEAN_ACCESS_TOKEN, DOCKER_REGISTRY_TOKEN) MUST be stored in GitHub Secrets
- Deployment MUST use `helm upgrade --install` for idempotent deploys

**GitHub Actions Workflow Structure:**
```yaml
# .github/workflows/deploy.yml
name: Deploy to DOKS
on:
  push:
    branches: [main]
jobs:
  test: ...
  build: ...
  deploy:
    needs: [test, build]
    runs-on: ubuntu-latest
    steps:
      - uses: digitalocean/action-doctl@v2
      - run: doctl kubernetes cluster kubeconfig save <cluster-name>
      - run: helm upgrade --install todo-app ./helm/todo-app ...
```

**Environment Management:**
- Separate namespaces for environments: `todo-app-staging`, `todo-app-production`
- Environment-specific values files: `values-staging.yaml`, `values-production.yaml`
- Staging MUST be deployed first; production deploy MUST require manual approval
- Feature branches MAY deploy to ephemeral preview environments

**Monitoring & Observability:**
- DigitalOcean Monitoring MUST be enabled for cluster metrics
- Application logs MUST be accessible via `kubectl logs` or centralized logging
- Health check endpoints MUST be monitored for uptime
- Alerts SHOULD be configured for: pod restarts, high CPU/memory, failed deployments

**Rollback Strategy:**
- Helm revision history MUST be preserved (default: 10 revisions)
- Rollback command: `helm rollback todo-app <revision> -n todo-app-production`
- Failed deployments MUST automatically rollback (Helm atomic flag)
- Database migrations MUST be backward-compatible to support rollback

## Technology Stack

**Phase 1 Requirements (Console App):**

| Component | Technology | Notes |
|-----------|------------|-------|
| Language | Python 3.13+ | Modern features, type hints |
| Package Manager | UV | Fast, reliable dependency resolution |
| Testing | pytest | Industry standard for Python |
| Linting | ruff | Fast, comprehensive linting |
| Formatting | ruff format | Consistent code style |
| Data Storage | In-memory (dict) | Phase 1 only; no persistence |

**Phase 2 Requirements (Full-Stack Web App):**

| Component | Technology | Notes |
|-----------|------------|-------|
| **Backend** | | |
| Language | Python 3.13+ | FastAPI framework |
| Framework | FastAPI | Async-capable, auto-OpenAPI docs |
| ORM | SQLModel | Type-safe, Pydantic integration |
| Database | Neon PostgreSQL | Serverless, auto-scaling |
| Auth | Better Auth | JWT-based authentication |
| Testing | pytest + httpx | API testing with async support |
| **Frontend** | | |
| Framework | Next.js 15+ | App Router, React Server Components |
| Language | TypeScript | Strict mode enabled |
| Styling | Tailwind CSS | Utility-first CSS |
| State | React hooks | Server state via fetch/SWR |
| Testing | Jest + RTL | Component and integration tests |
| **Infrastructure** | | |
| Monorepo | Root-level | `/backend` and `/frontend` directories |
| API Pattern | REST | JSON over HTTP |
| Environment | .env files | Separate dev/prod configs |

**Phase 3 Requirements (AI-Powered Chatbot):**

| Component | Technology | Notes |
|-----------|------------|-------|
| **AI/Agent Layer** | | |
| AI Framework | OpenAI Agents SDK | Agent orchestration and tool calling |
| MCP Server | Official MCP SDK | Model Context Protocol for tool exposure |
| LLM Provider | OpenAI API | GPT models for natural language |
| **Frontend** | | |
| Chat UI | OpenAI ChatKit | Pre-built chat components |
| Integration | Next.js API routes | Proxy to backend chat endpoint |
| **Backend** | | |
| Chat Endpoint | FastAPI | `POST /api/{user_id}/chat` |
| MCP Tools | Python functions | add_task, list_tasks, complete_task, delete_task, update_task |
| **Database** | | |
| Conversation | SQLModel | user_id, id, created_at, updated_at |
| Message | SQLModel | user_id, id, conversation_id, role, content, created_at |
| **Environment** | | |
| OPENAI_API_KEY | Required | OpenAI API access |
| Domain Allowlist | Required | ChatKit security configuration |

**Phase 4 Requirements (Kubernetes Deployment):**

| Component | Technology | Notes |
|-----------|------------|-------|
| **Containerization** | | |
| Container Runtime | Docker | Docker Desktop or standalone |
| Backend Image | python:3.13-slim | Multi-stage build |
| Frontend Image | node:22-slim | Multi-stage build with static export |
| Image Registry | Local / Docker Hub | Local for dev, registry for prod |
| **Orchestration** | | |
| Kubernetes | Docker Desktop K8s / Minikube | Local Kubernetes cluster |
| Package Manager | Helm 3.x | Chart-based deployment |
| CLI Tools | kubectl | Cluster management |
| **Helm Chart** | | |
| Chart Location | `helm/todo-app/` | Single chart for all services |
| Backend Deployment | Deployment + Service | ClusterIP, port 8000 |
| Frontend Deployment | Deployment + Service | NodePort, port 3000 |
| Secrets | Kubernetes Secret | DATABASE_URL, JWT_SECRET, OPENAI_API_KEY |
| Config | ConfigMap | Non-sensitive environment variables |
| **Health Checks** | | |
| Backend Probe | `/health` | Liveness + Readiness |
| Frontend Probe | `/` | Liveness + Readiness |
| **AI-Assisted Tools (Optional)** | | |
| kubectl-ai | Natural language → kubectl | AI-powered K8s commands |
| kagent | AI agent for K8s ops | Diagnosis and automation |
| Docker AI (Gordon) | Docker assistant | Dockerfile optimization |

**Phase 5 Requirements (Advanced Cloud Deployment):**

| Component | Technology | Notes |
|-----------|------------|-------|
| **Event Streaming** | | |
| Message Broker | Apache Kafka | Via Redpanda (local) or managed service |
| Local Kafka | Redpanda | Single binary, Kafka-compatible |
| Cloud Kafka | Redpanda Cloud / Strimzi | Free tier or self-hosted |
| **Distributed Runtime** | | |
| Sidecar Runtime | Dapr 1.12+ | Pub/Sub, State, Bindings, Secrets |
| Dapr CLI | dapr init / dapr run | Local development |
| Dapr on K8s | Helm install | Production deployment |
| **Cloud Infrastructure** | | |
| Kubernetes | DigitalOcean DOKS | Managed Kubernetes |
| Container Registry | DigitalOcean DOCR | Private image registry |
| Load Balancer | DO Load Balancer | Via K8s Service type LoadBalancer |
| CLI | doctl | DigitalOcean CLI |
| **CI/CD** | | |
| Pipeline | GitHub Actions | Automated deployments |
| Triggers | Push to main | Auto-deploy to production |
| Secrets | GitHub Secrets | API tokens, registry credentials |
| **Monitoring** | | |
| Cluster Metrics | DO Monitoring | Built-in metrics |
| Logs | kubectl logs | Centralized via DigitalOcean |
| **New Database Models** | | |
| Notification | SQLModel | user_id, type, title, message, read, created_at |
| AuditLog | SQLModel | user_id, action, entity_type, entity_id, timestamp, details |
| **Task Enhancements** | | |
| Recurrence Rule | Enum field | none, daily, weekly, monthly |
| Notification Trigger | Dapr Cron | Check reminders every 15 minutes |

**UI/UX Tools and Libraries:**

| Component | Technology | Notes |
|-----------|------------|-------|
| **Design System** | | |
| CSS Framework | Tailwind CSS | Utility-first, responsive design |
| Component Base | Headless UI / Radix | Accessible, unstyled primitives |
| Icons | Heroicons / Lucide | Consistent icon set |
| Animations | Tailwind / Framer Motion | Subtle, performant transitions |
| **Colors** | | |
| Primary | Blue (600 base) | Actions, links, primary buttons |
| Secondary | Gray (600 base) | Secondary actions, borders |
| Success | Green (600 base) | Success states, confirmations |
| Warning | Yellow (500 base) | Warnings, cautions |
| Error | Red (600 base) | Errors, destructive actions |
| **Typography** | | |
| Font Family | Inter / System UI | Clean, readable sans-serif |
| Base Size | 16px (1rem) | Body text |
| Scale | 1.25 ratio | sm(14), base(16), lg(18), xl(20), 2xl(24), 3xl(30) |
| **Spacing** | | |
| Base Unit | 4px (0.25rem) | Consistent spacing scale |
| Scale | 1, 2, 3, 4, 6, 8, 12, 16 | Multipliers of base unit |

**Phase 5 Constraints:**
- Dapr sidecar MUST be running alongside application containers
- Kafka/Redpanda MUST be accessible from within the cluster
- Events MUST be idempotent—duplicate processing produces same result
- Recurring task creation MUST NOT block the completion API response
- Notifications MUST be user-scoped (no cross-user data leakage)
- CI/CD pipeline MUST pass all tests before deployment
- Production deployments MUST be gated by staging success
- Database migrations MUST be backward-compatible for zero-downtime deploys

**Phase 4 Constraints:**
- Docker images MUST build successfully before Helm deployment
- Helm charts MUST pass `helm lint` before deployment
- All pods MUST reach Running state within 60 seconds
- Health probes MUST pass before pod is marked Ready
- Secrets MUST be passed via `--set` flags, never hardcoded
- Local images require `imagePullPolicy: Never` in values

**Phase 3 Constraints:**
- Chat endpoint MUST be stateless (conversation state in database only)
- MCP tools MUST enforce user isolation via user_id parameter
- Agent MUST use MCP tools for all task operations (no direct DB access from agent)
- Frontend MUST include JWT token in all chat requests
- Conversation history MUST be fetched from DB on each request

**Phase 2 Constraints:**
- Backend and frontend MUST be independently deployable
- API MUST be stateless (session state in JWT/database only)
- Frontend MUST work with JavaScript disabled for critical paths (SSR)
- Database migrations MUST be reversible

## Development Workflow

### Spec-Driven Development Lifecycle

```
1. /sp.specify  → Create feature specification (WHAT)
2. /sp.plan     → Generate technical plan (HOW)
3. /sp.tasks    → Break into actionable tasks (BREAKDOWN)
4. /sp.implement → Execute via Claude Code (BUILD)
```

### Phase-Specific Workflow

**Phase 1 (Console App):**
- Single `src/` directory structure
- Run with `python -m src.cli`
- Tests in `tests/unit/` and `tests/integration/`

**Phase 2 (Full-Stack Web App):**
- Monorepo with `/backend` and `/frontend`
- Backend: `cd backend && uvicorn src.main:app --reload`
- Frontend: `cd frontend && npm run dev`
- API contracts defined before implementation
- Backend endpoints tested before frontend integration

**Phase 3 (AI-Powered Chatbot):**
- Extends Phase 2 monorepo structure
- MCP Server: Integrated within backend or as separate module
- Agent: Configured with MCP tools for task operations
- Chat flow: Frontend → Backend Chat API → Agent → MCP Tools → Database
- Database: Add Conversation and Message models
- Testing: Mock OpenAI responses for deterministic tests
- Development order:
  1. Database models (Conversation, Message)
  2. MCP tools (add_task, list_tasks, etc.)
  3. Agent configuration with tools
  4. Chat endpoint integration
  5. Frontend ChatKit integration

**Phase 4 (Kubernetes Deployment):**
- Containerizes Phase 2/3 application for orchestrated deployment
- Local Kubernetes via Docker Desktop or Minikube
- Helm-based deployment with configurable values
- Development order:
  1. Create/verify Dockerfiles (backend, frontend)
  2. Build and test images locally with `docker build` and `docker run`
  3. Create Helm chart structure (`helm/todo-app/`)
  4. Define Kubernetes manifests (Deployment, Service, Secret, ConfigMap)
  5. Configure health probes and resource limits
  6. Deploy with `helm install` and verify pods
  7. Test application via port-forward or NodePort
- Deployment commands:
  ```bash
  # Build images
  docker build -t todo-backend:latest ./backend
  docker build -t todo-frontend:latest ./frontend

  # Create namespace and deploy
  kubectl create namespace todo-app
  helm install todo-app ./helm/todo-app \
    --namespace todo-app \
    --set secrets.databaseUrl="..." \
    --set secrets.jwtSecret="..." \
    --set backend.image.pullPolicy=Never \
    --set frontend.image.pullPolicy=Never

  # Verify deployment
  kubectl get pods -n todo-app
  kubectl port-forward svc/todo-app-frontend 3000:3000 -n todo-app
  ```

**Phase 5 (Advanced Cloud Deployment):**
- Extends Phase 4 with event-driven architecture and cloud deployment
- Local development with Dapr + Redpanda before cloud
- DigitalOcean DOKS for production Kubernetes
- GitHub Actions for CI/CD automation
- Development order:
  1. Add recurring tasks feature (database + API + AI)
  2. Add notification system (database + API + frontend)
  3. Setup Dapr locally (`dapr init`)
  4. Setup Redpanda locally for Kafka
  5. Implement event producers (task operations → audit events)
  6. Implement reminder service (Dapr cron → check due dates → notifications)
  7. Test event flow locally with `dapr run`
  8. Create DigitalOcean account and DOKS cluster
  9. Setup GitHub Actions for CI/CD
  10. Deploy Dapr to DOKS
  11. Deploy application to DOKS
  12. Configure production Kafka (Redpanda Cloud or Strimzi)
  13. Verify end-to-end flow in production
- Local development commands:
  ```bash
  # Start Redpanda (Kafka-compatible)
  docker run -d --name redpanda -p 9092:9092 redpandadata/redpanda

  # Initialize Dapr
  dapr init

  # Run backend with Dapr sidecar
  dapr run --app-id backend --app-port 8000 -- uvicorn src.main:app

  # Deploy Dapr to Kubernetes
  dapr init -k

  # Apply Dapr components
  kubectl apply -f dapr/components/
  ```
- Cloud deployment commands:
  ```bash
  # Setup DigitalOcean CLI
  doctl auth init
  doctl kubernetes cluster create todo-cluster --region nyc1 --size s-2vcpu-4gb --count 2

  # Configure kubectl
  doctl kubernetes cluster kubeconfig save todo-cluster

  # Deploy via GitHub Actions (automatic on push to main)
  # Or manually:
  helm upgrade --install todo-app ./helm/todo-app \
    --namespace todo-app-production \
    -f helm/todo-app/values-production.yaml \
    --set secrets.databaseUrl="..." \
    --set secrets.kafkaBrokers="..."
  ```

### Quality Gates

Before proceeding to the next phase, verify:

- [ ] All specification requirements are met
- [ ] Tests pass and coverage targets achieved
- [ ] Code passes linting and formatting checks
- [ ] No manual code edits outside of spec-driven workflow
- [ ] Documentation updated if public interface changed
- [ ] (Phase 2+) API contracts validated against implementation
- [ ] (Phase 2+) Database migrations tested both up and down
- [ ] (Phase 3+) MCP tools tested with mock agent responses
- [ ] (Phase 3+) Conversation persistence verified across requests
- [ ] (Phase 3+) User isolation enforced in all MCP tools
- [ ] **UI/UX Quality Gates:**
  - [ ] Responsive design tested on mobile, tablet, desktop viewports
  - [ ] Keyboard navigation works for all interactive elements
  - [ ] Color contrast meets WCAG AA standards (4.5:1 minimum)
  - [ ] Loading states displayed for async operations
  - [ ] Error states clearly communicated with appropriate styling
  - [ ] Animations respect prefers-reduced-motion
  - [ ] Focus states visible on all interactive elements
- [ ] **Container & Orchestration Quality Gates (Phase 4+):**
  - [ ] Dockerfiles use multi-stage builds with slim base images
  - [ ] Docker images build without errors (`docker build`)
  - [ ] Containers run successfully standalone (`docker run`)
  - [ ] Helm chart passes linting (`helm lint`)
  - [ ] All pods reach Running state after deployment
  - [ ] Health probes (liveness/readiness) pass for all services
  - [ ] Application accessible via port-forward or NodePort
  - [ ] Secrets not hardcoded in images or values.yaml
  - [ ] Resource requests/limits defined for all containers
  - [ ] Deployment can be upgraded with `helm upgrade`
  - [ ] Rollback works correctly with `helm rollback`
- [ ] **Event-Driven & Cloud Quality Gates (Phase 5+):**
  - [ ] Dapr sidecar starts successfully with application
  - [ ] Events published to Kafka topics successfully
  - [ ] Consumers receive and process events correctly
  - [ ] Recurring task creates next occurrence on completion
  - [ ] Notifications created for tasks due within 24 hours
  - [ ] Notification bell displays correct unread count
  - [ ] Toast notifications appear and auto-dismiss
  - [ ] Audit log captures all task operations
  - [ ] GitHub Actions workflow passes all stages
  - [ ] Application deploys successfully to DOKS
  - [ ] Load balancer routes traffic correctly
  - [ ] Rollback works in production environment
  - [ ] Monitoring shows healthy metrics

### Commit Practices

- Commit after each completed task
- Commit messages reference task IDs (e.g., "T001: Create project structure")
- Keep commits atomic—one logical change per commit

## Governance

### Authority

This constitution supersedes all other development practices for this project. Any deviation requires:
1. Documented justification
2. Amendment to this constitution
3. Migration plan for affected code

### Amendments

- MAJOR version: Removing or fundamentally changing principles
- MINOR version: Adding new principles or sections
- PATCH version: Clarifications, typo fixes, non-semantic changes

### Compliance

- All code reviews MUST verify constitution compliance
- Claude Code prompts MUST reference relevant principles
- Violations MUST be documented and resolved before merge

**Version**: 1.5.0 | **Ratified**: 2026-01-18 | **Last Amended**: 2026-02-09

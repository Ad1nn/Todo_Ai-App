# Implementation Plan: Advanced Cloud Deployment

**Branch**: `007-advanced-cloud-deployment` | **Date**: 2026-02-09 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/007-advanced-cloud-deployment/spec.md`

## Summary

Phase 5 adds event-driven architecture with Kafka/Dapr for reminder notifications and audit logging, recurring task patterns (daily/weekly/monthly), in-app notifications (toast + bell icon), and cloud deployment to DigitalOcean DOKS with GitHub Actions CI/CD. This extends the existing Phase 2-4 full-stack application with advanced features and production-grade infrastructure.

## Technical Context

**Language/Version**: Python 3.13+ (backend), TypeScript 5.x (frontend)
**Primary Dependencies**: FastAPI, SQLModel, Dapr SDK (backend); Next.js 15+, Tailwind CSS (frontend)
**Storage**: Neon PostgreSQL (existing) + Redpanda/Kafka (events)
**Testing**: pytest (backend), Jest/Vitest (frontend)
**Target Platform**: DigitalOcean Kubernetes Service (DOKS)
**Project Type**: Web application (monorepo with /backend and /frontend)
**Performance Goals**: Reminders within 1 minute, deployments under 10 minutes
**Constraints**: Dapr sidecar required, events must be idempotent, user-scoped data isolation
**Scale/Scope**: Single-region deployment, 99.5% uptime target

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Requirement | Status |
|-----------|-------------|--------|
| I. Spec-Driven Development | All code via Claude Code from specs | ✅ Pass |
| II. Clean Code | Readable, maintainable code | ✅ Will enforce |
| III. Language Best Practices | Python 3.13+, TypeScript strict | ✅ Existing setup |
| IV. Test-First Approach | Tests before implementation | ✅ Will enforce |
| V. Modular Architecture | Event producers/consumers as separate services | ✅ Planned |
| VI. Simplicity First | Only specified features | ✅ Scoped to spec |
| VII. API Design | REST patterns, versioned endpoints | ✅ Existing |
| VIII. Security | Secrets in env vars, user isolation | ✅ Will enforce |
| IX. AI Agent Design | MCP tools include recurrence_rule | ✅ Planned |
| X. UI/UX Design | Toast 5s dismiss, bell icon, accessibility | ✅ Planned |
| XI. Container & Orchestration | Helm, health probes, resource limits | ✅ Existing from Phase 4 |
| XII. Event-Driven Architecture | Kafka via Dapr, idempotent consumers | ✅ Core of Phase 5 |
| XIII. Advanced Task Features | Recurrence, notifications | ✅ Core of Phase 5 |
| XIV. Cloud Deployment & CI/CD | DOKS, GitHub Actions | ✅ Core of Phase 5 |

**Gate Status**: ✅ PASSED - All principles aligned

## Project Structure

### Documentation (this feature)

```text
specs/007-advanced-cloud-deployment/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
│   ├── notifications-api.yaml
│   ├── audit-api.yaml
│   └── dapr-components.yaml
└── tasks.md             # Phase 2 output (/sp.tasks)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── models/
│   │   ├── task.py          # Extended with recurrence_rule
│   │   ├── notification.py  # NEW: Notification model
│   │   └── audit.py         # NEW: AuditEntry model
│   ├── services/
│   │   ├── task_service.py  # Extended for recurring tasks
│   │   ├── notification_service.py  # NEW
│   │   ├── audit_service.py         # NEW
│   │   └── reminder_service.py      # NEW: Dapr cron handler
│   ├── api/
│   │   ├── tasks.py         # Extended endpoints
│   │   ├── notifications.py # NEW
│   │   └── audit.py         # NEW
│   ├── events/
│   │   ├── producers.py     # NEW: Dapr pub/sub producers
│   │   └── consumers.py     # NEW: Event handlers
│   └── mcp/
│       └── tools.py         # Extended with recurrence_rule
├── dapr/
│   └── components/
│       ├── pubsub.yaml      # Kafka/Redpanda config
│       ├── cron-binding.yaml # Reminder scheduler
│       └── secrets.yaml     # Dapr secrets store
└── tests/
    ├── unit/
    ├── integration/
    └── events/              # NEW: Event testing

frontend/
├── src/
│   ├── components/
│   │   ├── TaskForm.tsx     # Extended with recurrence
│   │   ├── TaskItem.tsx     # Extended with recurrence badge
│   │   ├── NotificationBell.tsx    # NEW
│   │   ├── NotificationCenter.tsx  # NEW
│   │   ├── Toast.tsx               # NEW
│   │   └── AuditLog.tsx            # NEW
│   ├── hooks/
│   │   ├── useNotifications.ts     # NEW
│   │   └── useAudit.ts             # NEW
│   └── lib/
│       └── types.ts         # Extended with new types
└── tests/

.github/
└── workflows/
    ├── ci.yml               # Test + build
    └── deploy.yml           # Deploy to DOKS

helm/
└── todo-app/
    ├── values-staging.yaml      # NEW
    ├── values-production.yaml   # NEW
    └── templates/
        ├── dapr-components.yaml # NEW
        └── ...existing...
```

**Structure Decision**: Extends existing Phase 2-4 monorepo structure with new modules for events, notifications, audit, and Dapr configuration.

## Complexity Tracking

No violations requiring justification. The event-driven architecture is explicitly required by the specification and constitution principles XII-XIV.

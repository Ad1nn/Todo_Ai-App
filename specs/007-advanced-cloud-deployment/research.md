# Research: Advanced Cloud Deployment

**Feature**: 007-advanced-cloud-deployment
**Date**: 2026-02-09

## Research Summary

This document consolidates research findings for Phase 5 implementation decisions.

---

## 1. Event Streaming: Kafka vs Alternatives

### Decision: Redpanda (Kafka-compatible) for local, Strimzi/Redpanda Cloud for production

### Rationale
- Redpanda is a single binary, Kafka-compatible alternative that's simpler to run locally
- No JVM required (unlike Apache Kafka), faster startup
- 100% Kafka API compatible - same client libraries work
- Strimzi provides Kubernetes-native Kafka operator for production
- Redpanda Cloud offers free tier for small workloads

### Alternatives Considered
| Option | Pros | Cons | Decision |
|--------|------|------|----------|
| Apache Kafka | Industry standard, mature | Heavy (JVM), complex local setup | Rejected for local |
| Redpanda | Lightweight, Kafka-compatible | Newer, smaller community | ✅ Chosen for local |
| AWS SQS/SNS | Managed, serverless | Not Kafka-compatible, AWS lock-in | Rejected |
| RabbitMQ | Lightweight, flexible | Different protocol, not Kafka API | Rejected |

### Implementation Notes
- Local: `docker run redpandadata/redpanda`
- Production: Strimzi operator on DOKS or Redpanda Cloud
- Topics: `todo.reminders`, `todo.audit`

---

## 2. Distributed Runtime: Dapr Architecture

### Decision: Dapr sidecar pattern with HTTP API

### Rationale
- Dapr abstracts infrastructure (Kafka, secrets, state) from application code
- Sidecar pattern: application talks to local Dapr sidecar via HTTP
- Dapr handles routing to actual infrastructure
- Easy to swap backends (Redpanda → Kafka → Cloud) without code changes
- Built-in retry, circuit breaker, tracing

### Dapr Components for Phase 5
| Component | Purpose | Backend |
|-----------|---------|---------|
| Pub/Sub | Event publishing/subscribing | Kafka/Redpanda |
| Bindings (Cron) | Scheduled reminder checks | Built-in |
| Secrets | API keys, DB credentials | Kubernetes Secrets |

### Implementation Notes
```yaml
# dapr/components/pubsub.yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: todo-pubsub
spec:
  type: pubsub.kafka
  metadata:
    - name: brokers
      value: "localhost:9092"  # or Redpanda Cloud URL
    - name: consumerGroup
      value: "todo-backend"
```

---

## 3. Recurring Task Implementation

### Decision: Database field + completion event trigger

### Rationale
- Store `recurrence_rule` as enum field on Task model
- When task is marked complete, check if recurring
- If recurring, create new task with calculated next due date
- Event-driven: completion triggers `todo.task.completed` event
- Consumer creates next occurrence asynchronously

### Next Due Date Calculation
| Pattern | Calculation | Edge Case Handling |
|---------|-------------|--------------------|
| Daily | `due_date + 1 day` | None needed |
| Weekly | `due_date + 7 days` | None needed |
| Monthly | `due_date + 1 month` | If day > month length, use last day |

### Implementation Notes
```python
from dateutil.relativedelta import relativedelta

def calculate_next_due_date(current_due: datetime, rule: RecurrenceRule) -> datetime:
    match rule:
        case RecurrenceRule.DAILY:
            return current_due + relativedelta(days=1)
        case RecurrenceRule.WEEKLY:
            return current_due + relativedelta(weeks=1)
        case RecurrenceRule.MONTHLY:
            return current_due + relativedelta(months=1)
```

---

## 4. Notification System Design

### Decision: Database-backed with polling + optional WebSocket

### Rationale
- Store notifications in PostgreSQL for durability
- Frontend polls `/api/v1/notifications` every 30 seconds
- Optional: WebSocket for real-time updates (stretch goal)
- Toast component manages display queue with 5s auto-dismiss
- Bell icon shows unread count from poll response

### Notification Flow
```
1. Dapr cron (15 min) → Reminder service
2. Query tasks due within 1 hour, not yet notified
3. Publish to `todo.reminders` topic
4. Consumer creates Notification record in DB
5. Frontend poll fetches new notifications
6. Toast displayed, bell count updated
```

### Alternatives Considered
| Option | Pros | Cons | Decision |
|--------|------|------|----------|
| Polling | Simple, works everywhere | Higher latency | ✅ MVP |
| WebSocket | Real-time | More complex | Stretch goal |
| Server-Sent Events | Simpler than WS | Less browser support | Rejected |
| Push Notifications | Native feel | Out of scope (spec) | Rejected |

---

## 5. Audit Logging Strategy

### Decision: Event-sourced audit with Kafka + PostgreSQL persistence

### Rationale
- Every task mutation publishes event to `todo.audit` topic
- Audit consumer persists to AuditEntry table
- Async processing doesn't block API response
- 90-day retention with archival (per spec)

### Event Schema
```json
{
  "schema_version": "1.0",
  "event_type": "task.updated",
  "timestamp": "2026-02-09T12:00:00Z",
  "user_id": "uuid",
  "entity_type": "task",
  "entity_id": "uuid",
  "action": "update",
  "before": { "title": "Old Title" },
  "after": { "title": "New Title" }
}
```

---

## 6. DigitalOcean DOKS Setup

### Decision: Basic 2-node cluster with auto-scaling

### Rationale
- Minimum 2 nodes for high availability
- Basic droplet size (s-2vcpu-4gb) for cost efficiency (~$24/month per node)
- DigitalOcean Container Registry (DOCR) for images
- DO Load Balancer via Service type LoadBalancer

### Cluster Configuration
| Setting | Value | Notes |
|---------|-------|-------|
| Region | NYC1 | Low latency for US users |
| Node Pool | 2 x s-2vcpu-4gb | ~$48/month |
| Auto-scale | 2-4 nodes | Scale on load |
| Registry | DOCR Basic | $5/month, 5GB storage |

### Implementation Notes
```bash
# Create cluster
doctl kubernetes cluster create todo-cluster \
  --region nyc1 \
  --size s-2vcpu-4gb \
  --count 2 \
  --auto-upgrade

# Create container registry
doctl registry create todo-registry
```

---

## 7. GitHub Actions CI/CD

### Decision: Separate CI and Deploy workflows

### Rationale
- CI runs on every push/PR (lint, test, build)
- Deploy runs only on main branch after CI passes
- Manual approval gate for production
- Helm upgrade for idempotent deployments

### Workflow Structure
```
.github/workflows/
├── ci.yml          # Lint, test, build images
└── deploy.yml      # Push images, helm deploy
```

### Secrets Required
| Secret | Purpose |
|--------|---------|
| DIGITALOCEAN_ACCESS_TOKEN | doctl auth |
| DOCKERHUB_TOKEN | Image push (or DOCR) |
| DATABASE_URL | Neon PostgreSQL |
| JWT_SECRET | Auth signing |
| OPENAI_API_KEY | AI features |

---

## 8. Dapr on Kubernetes

### Decision: Helm-based Dapr installation

### Rationale
- `dapr init -k` installs Dapr to Kubernetes
- Helm values configure HA mode for production
- Sidecar injector automatically adds Dapr to pods with annotation
- Components deployed via Kubernetes manifests

### Implementation Notes
```bash
# Install Dapr to cluster
helm repo add dapr https://dapr.github.io/helm-charts/
helm install dapr dapr/dapr --namespace dapr-system --create-namespace

# Annotate deployment for sidecar injection
annotations:
  dapr.io/enabled: "true"
  dapr.io/app-id: "todo-backend"
  dapr.io/app-port: "8000"
```

---

## Dependencies Verified

| Dependency | Status | Notes |
|------------|--------|-------|
| Phase 4 (K8s) | ✅ Complete | Helm chart exists |
| 005-task-enhancements | ⚠️ Required | Need due_date field |
| DigitalOcean account | ⏳ Pending | User setting up |
| GitHub repo | ✅ Exists | Actions can be enabled |

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Kafka complexity | Medium | High | Use Redpanda, Dapr abstraction |
| DO credits exhausted | Low | Medium | Monitor usage, use minimal resources |
| Event ordering issues | Medium | Medium | Idempotent consumers, event timestamps |
| Notification latency | Low | Low | 15-min interval acceptable per spec |

---

## Next Steps

1. Create data-model.md with entity schemas
2. Create API contracts for new endpoints
3. Create Dapr component configurations
4. Create quickstart.md for local development

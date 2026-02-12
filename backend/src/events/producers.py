"""Event producers for Dapr pub/sub.

Publishes events to Kafka topics via Dapr sidecar HTTP API.
"""

import json
import logging
from datetime import datetime
from typing import Any
from uuid import UUID

import httpx

logger = logging.getLogger(__name__)

# Dapr sidecar configuration
DAPR_HTTP_PORT = 3500
DAPR_PUBSUB_NAME = "todo-pubsub"

# Topics
TOPIC_REMINDERS = "todo.reminders"
TOPIC_AUDIT = "todo.audit"


def _serialize_value(value: Any) -> Any:
    """Serialize values for JSON, handling UUID and datetime."""
    if isinstance(value, UUID):
        return str(value)
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, dict):
        return {k: _serialize_value(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_serialize_value(item) for item in value]
    return value


async def _publish_event(topic: str, event_data: dict[str, Any]) -> bool:
    """Publish event to Dapr pub/sub.

    Args:
        topic: Kafka topic name
        event_data: Event payload

    Returns:
        True if published successfully, False otherwise
    """
    url = f"http://localhost:{DAPR_HTTP_PORT}/v1.0/publish/{DAPR_PUBSUB_NAME}/{topic}"

    # Serialize the event data
    serialized_data = _serialize_value(event_data)

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                json=serialized_data,
                headers={"Content-Type": "application/json"},
                timeout=5.0,
            )
            response.raise_for_status()
            logger.info(f"Published event to {topic}: {event_data.get('event_type')}")
            return True
    except httpx.HTTPError as e:
        logger.error(f"Failed to publish event to {topic}: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error publishing to {topic}: {e}")
        return False


async def publish_reminder_event(
    user_id: UUID,
    task_id: UUID,
    task_title: str,
    due_date: datetime,
) -> bool:
    """Publish a reminder event for a task due soon.

    Args:
        user_id: Owner of the task
        task_id: Task identifier
        task_title: Task title for notification
        due_date: When the task is due

    Returns:
        True if published successfully
    """
    event_data = {
        "schema_version": "1.0",
        "event_type": "task.reminder",
        "timestamp": datetime.utcnow().isoformat(),
        "user_id": str(user_id),
        "task_id": str(task_id),
        "task_title": task_title,
        "due_date": due_date.isoformat(),
    }

    return await _publish_event(TOPIC_REMINDERS, event_data)


async def publish_audit_event(
    user_id: UUID,
    entity_type: str,
    entity_id: UUID,
    action: str,
    before_value: dict[str, Any] | None = None,
    after_value: dict[str, Any] | None = None,
    metadata: dict[str, Any] | None = None,
) -> bool:
    """Publish an audit event for entity changes.

    Args:
        user_id: User who performed the action
        entity_type: Type of entity (e.g., "task")
        entity_id: Entity identifier
        action: Action performed (create, update, complete, delete)
        before_value: State before the change
        after_value: State after the change
        metadata: Additional context

    Returns:
        True if published successfully
    """
    event_data = {
        "schema_version": "1.0",
        "event_type": f"{entity_type}.{action}",
        "timestamp": datetime.utcnow().isoformat(),
        "user_id": str(user_id),
        "entity_type": entity_type,
        "entity_id": str(entity_id),
        "action": action,
        "before": before_value,
        "after": after_value,
        "metadata": metadata,
    }

    return await _publish_event(TOPIC_AUDIT, event_data)

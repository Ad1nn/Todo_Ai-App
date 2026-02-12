"""Event consumers for Dapr pub/sub.

Handles events received from Kafka topics via Dapr subscriptions.
"""

import logging
from datetime import datetime
from typing import Any
from uuid import UUID

from sqlmodel.ext.asyncio.session import AsyncSession

from src.models.audit import AuditAction, AuditEntry
from src.models.notification import Notification, NotificationType

logger = logging.getLogger(__name__)


async def handle_reminder_event(
    event_data: dict[str, Any],
    session: AsyncSession,
) -> bool:
    """Handle a reminder event and create a notification.

    Args:
        event_data: Event payload from Kafka
        session: Database session

    Returns:
        True if handled successfully
    """
    try:
        user_id = UUID(event_data["user_id"])
        task_id = UUID(event_data["task_id"])
        task_title = event_data["task_title"]
        due_date = event_data["due_date"]

        # Create notification
        notification = Notification(
            user_id=user_id,
            type=NotificationType.REMINDER,
            title=f"Task due soon: {task_title}",
            message=f"Due: {due_date}",
            task_id=task_id,
            read=False,
            created_at=datetime.utcnow(),
        )

        session.add(notification)
        await session.commit()

        logger.info(f"Created reminder notification for task {task_id}")
        return True

    except KeyError as e:
        logger.error(f"Missing field in reminder event: {e}")
        return False
    except Exception as e:
        logger.error(f"Error handling reminder event: {e}")
        await session.rollback()
        return False


async def handle_audit_event(
    event_data: dict[str, Any],
    session: AsyncSession,
) -> bool:
    """Handle an audit event and persist to database.

    Args:
        event_data: Event payload from Kafka
        session: Database session

    Returns:
        True if handled successfully
    """
    try:
        user_id = UUID(event_data["user_id"])
        entity_type = event_data["entity_type"]
        entity_id = UUID(event_data["entity_id"])
        action = AuditAction(event_data["action"])
        before_value = event_data.get("before")
        after_value = event_data.get("after")
        metadata = event_data.get("metadata")
        timestamp = datetime.fromisoformat(event_data["timestamp"])

        # Create audit entry
        audit_entry = AuditEntry(
            user_id=user_id,
            entity_type=entity_type,
            entity_id=entity_id,
            action=action,
            before_value=before_value,
            after_value=after_value,
            metadata=metadata,
            timestamp=timestamp,
        )

        session.add(audit_entry)
        await session.commit()

        logger.info(f"Created audit entry for {entity_type} {entity_id}: {action}")
        return True

    except KeyError as e:
        logger.error(f"Missing field in audit event: {e}")
        return False
    except ValueError as e:
        logger.error(f"Invalid value in audit event: {e}")
        return False
    except Exception as e:
        logger.error(f"Error handling audit event: {e}")
        await session.rollback()
        return False

"""Events API routes for Dapr pub/sub and bindings."""

import logging
from typing import Any

from fastapi import APIRouter, Request, status
from fastapi.responses import JSONResponse

from src.api.deps import DbSession
from src.events import handle_audit_event, handle_reminder_event
from src.services.reminder_service import handle_cron_trigger

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/events", tags=["events"])


@router.post("/cron/reminder-check", status_code=status.HTTP_200_OK)
async def cron_reminder_check(session: DbSession) -> dict:
    """Handle cron trigger for reminder checks.

    This endpoint is called by the Dapr cron binding every 15 minutes.
    It checks for tasks due soon and publishes reminder events.
    """
    return await handle_cron_trigger(session)


@router.post("/reminders", status_code=status.HTTP_200_OK)
async def handle_reminder_subscription(
    request: Request,
    session: DbSession,
) -> JSONResponse:
    """Handle reminder events from Dapr pub/sub.

    This endpoint receives reminder events published to the todo.reminders topic
    and creates notifications in the database.
    """
    try:
        # Parse the CloudEvent from Dapr
        body = await request.json()

        # Dapr wraps the data in a CloudEvents envelope
        # The actual event data is in the 'data' field
        event_data = body.get("data", body)

        logger.info(f"Received reminder event: {event_data}")

        success = await handle_reminder_event(event_data, session)

        if success:
            await session.commit()
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={"status": "success"},
            )
        else:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"status": "failed", "message": "Failed to process reminder"},
            )

    except Exception as e:
        logger.error(f"Error handling reminder event: {e}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"status": "error", "message": str(e)},
        )


@router.post("/audit", status_code=status.HTTP_200_OK)
async def handle_audit_subscription(
    request: Request,
    session: DbSession,
) -> JSONResponse:
    """Handle audit events from Dapr pub/sub.

    This endpoint receives audit events published to the todo.audit topic
    and persists them to the database.
    """
    try:
        # Parse the CloudEvent from Dapr
        body = await request.json()

        # Dapr wraps the data in a CloudEvents envelope
        event_data = body.get("data", body)

        logger.info(f"Received audit event: {event_data.get('event_type')}")

        success = await handle_audit_event(event_data, session)

        if success:
            await session.commit()
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={"status": "success"},
            )
        else:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"status": "failed", "message": "Failed to process audit event"},
            )

    except Exception as e:
        logger.error(f"Error handling audit event: {e}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"status": "error", "message": str(e)},
        )


# Dapr subscription configuration endpoint
# This tells Dapr which topics to subscribe to
@router.get("/dapr/subscribe")
async def dapr_subscribe() -> list[dict[str, Any]]:
    """Return Dapr subscription configuration.

    Dapr calls this endpoint to discover which topics this service subscribes to.
    """
    return [
        {
            "pubsubname": "todo-pubsub",
            "topic": "todo.reminders",
            "route": "/events/reminders",
        },
        {
            "pubsubname": "todo-pubsub",
            "topic": "todo.audit",
            "route": "/events/audit",
        },
    ]

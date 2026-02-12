"""Notifications API routes."""

from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, status

from src.api.deps import CurrentUser, DbSession
from src.models.notification import Notification, NotificationPublic
from src.services.notification_service import NotificationService

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("", response_model=list[NotificationPublic])
async def list_notifications(
    session: DbSession,
    current_user: CurrentUser,
    unread_only: bool = Query(default=False),
    limit: int = Query(default=50, ge=1, le=100),
) -> list[Notification]:
    """List notifications for the current user."""
    notification_service = NotificationService(session)
    return await notification_service.list_by_user(
        user_id=current_user.id,
        unread_only=unread_only,
        limit=limit,
    )


@router.get("/unread-count")
async def get_unread_count(
    session: DbSession,
    current_user: CurrentUser,
) -> dict[str, int]:
    """Get count of unread notifications for the current user."""
    notification_service = NotificationService(session)
    count = await notification_service.get_unread_count(current_user.id)
    return {"unread_count": count}


@router.post("/{notification_id}/read", response_model=NotificationPublic)
async def mark_as_read(
    notification_id: UUID,
    session: DbSession,
    current_user: CurrentUser,
) -> Notification:
    """Mark a notification as read."""
    notification_service = NotificationService(session)
    notification = await notification_service.mark_as_read(
        notification_id, current_user.id
    )
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found",
        )
    return notification


@router.post("/mark-all-read")
async def mark_all_as_read(
    session: DbSession,
    current_user: CurrentUser,
) -> dict[str, int]:
    """Mark all notifications as read for the current user."""
    notification_service = NotificationService(session)
    count = await notification_service.mark_all_as_read(current_user.id)
    return {"marked_as_read": count}


@router.delete("/{notification_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_notification(
    notification_id: UUID,
    session: DbSession,
    current_user: CurrentUser,
) -> None:
    """Delete a notification."""
    notification_service = NotificationService(session)
    deleted = await notification_service.delete(notification_id, current_user.id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found",
        )


@router.delete("/clear", status_code=status.HTTP_200_OK)
async def clear_old_notifications(
    session: DbSession,
    current_user: CurrentUser,
    days_old: int = Query(default=30, ge=1, le=365),
) -> dict[str, int]:
    """Clear notifications older than specified days."""
    notification_service = NotificationService(session)
    count = await notification_service.clear_old_notifications(
        user_id=current_user.id,
        days_old=days_old,
    )
    return {"deleted": count}

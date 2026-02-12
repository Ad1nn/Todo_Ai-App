"""Audit API routes."""

from uuid import UUID

from fastapi import APIRouter, Query, status

from src.api.deps import CurrentUser, DbSession
from src.models.audit import AuditAction, AuditEntry, AuditEntryPublic
from src.services.audit_service import AuditService

router = APIRouter(prefix="/audit", tags=["audit"])


@router.get("", response_model=list[AuditEntryPublic])
async def list_audit_entries(
    session: DbSession,
    current_user: CurrentUser,
    entity_type: str | None = Query(default=None, max_length=50),
    action: AuditAction | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
) -> list[AuditEntry]:
    """List audit entries for the current user with optional filters."""
    audit_service = AuditService(session)
    return await audit_service.list_entries(
        user_id=current_user.id,
        entity_type=entity_type,
        action=action,
        limit=limit,
        offset=offset,
    )


@router.get("/task/{task_id}", response_model=list[AuditEntryPublic])
async def get_task_audit_history(
    task_id: UUID,
    session: DbSession,
    current_user: CurrentUser,
    limit: int = Query(default=50, ge=1, le=100),
) -> list[AuditEntry]:
    """Get audit history for a specific task."""
    audit_service = AuditService(session)
    return await audit_service.get_task_history(
        task_id=task_id,
        user_id=current_user.id,
        limit=limit,
    )

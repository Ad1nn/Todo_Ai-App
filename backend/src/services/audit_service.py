"""Audit service for business logic."""

from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.models.audit import AuditAction, AuditEntry
from src.repositories.audit_repository import AuditRepository


class AuditService:
    """Service for audit operations."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.audit_repo = AuditRepository(session)

    async def log_action(
        self,
        user_id: UUID,
        entity_type: str,
        entity_id: UUID,
        action: AuditAction,
        before_value: dict[str, Any] | None = None,
        after_value: dict[str, Any] | None = None,
        extra_data: dict[str, Any] | None = None,
    ) -> AuditEntry:
        """Log an auditable action."""
        return await self.audit_repo.create(
            user_id=user_id,
            entity_type=entity_type,
            entity_id=entity_id,
            action=action,
            before_value=before_value,
            after_value=after_value,
            extra_data=extra_data,
        )

    async def list_entries(
        self,
        user_id: UUID,
        entity_type: str | None = None,
        action: AuditAction | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[AuditEntry]:
        """List audit entries for a user."""
        return await self.audit_repo.list_by_user(
            user_id=user_id,
            entity_type=entity_type,
            action=action,
            limit=limit,
            offset=offset,
        )

    async def list_by_entity(
        self,
        entity_type: str,
        entity_id: UUID,
        user_id: UUID,
        limit: int = 50,
    ) -> list[AuditEntry]:
        """List audit entries for a specific entity."""
        return await self.audit_repo.list_by_entity(
            entity_type=entity_type,
            entity_id=entity_id,
            user_id=user_id,
            limit=limit,
        )

    async def get_task_history(
        self,
        task_id: UUID,
        user_id: UUID,
        limit: int = 50,
    ) -> list[AuditEntry]:
        """Get the audit history for a specific task."""
        return await self.list_by_entity(
            entity_type="task",
            entity_id=task_id,
            user_id=user_id,
            limit=limit,
        )

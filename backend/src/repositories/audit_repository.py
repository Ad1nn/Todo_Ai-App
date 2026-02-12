"""Audit repository for database operations."""

from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.audit import AuditAction, AuditEntry


class AuditRepository:
    """Repository for AuditEntry database operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self,
        user_id: UUID,
        entity_type: str,
        entity_id: UUID,
        action: AuditAction,
        before_value: dict[str, Any] | None = None,
        after_value: dict[str, Any] | None = None,
        extra_data: dict[str, Any] | None = None,
        timestamp: datetime | None = None,
    ) -> AuditEntry:
        """Create a new audit entry."""
        audit_entry = AuditEntry(
            user_id=user_id,
            entity_type=entity_type,
            entity_id=entity_id,
            action=action,
            before_value=before_value,
            after_value=after_value,
            extra_data=extra_data,
            timestamp=timestamp or datetime.utcnow(),
        )
        self.session.add(audit_entry)
        await self.session.flush()
        await self.session.refresh(audit_entry)
        return audit_entry

    async def get_by_id(self, audit_id: UUID) -> AuditEntry | None:
        """Get audit entry by ID."""
        result = await self.session.execute(
            select(AuditEntry).where(AuditEntry.id == audit_id)
        )
        return result.scalar_one_or_none()

    async def list_by_user(
        self,
        user_id: UUID,
        entity_type: str | None = None,
        action: AuditAction | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[AuditEntry]:
        """List audit entries for a user with optional filters."""
        query = select(AuditEntry).where(AuditEntry.user_id == user_id)

        if entity_type is not None:
            query = query.where(AuditEntry.entity_type == entity_type)
        if action is not None:
            query = query.where(AuditEntry.action == action)

        query = (
            query.order_by(AuditEntry.timestamp.desc())
            .limit(limit)
            .offset(offset)
        )

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def list_by_entity(
        self,
        entity_type: str,
        entity_id: UUID,
        user_id: UUID | None = None,
        limit: int = 50,
    ) -> list[AuditEntry]:
        """List audit entries for a specific entity."""
        query = select(AuditEntry).where(
            AuditEntry.entity_type == entity_type,
            AuditEntry.entity_id == entity_id,
        )

        # Optionally filter by user (for security)
        if user_id is not None:
            query = query.where(AuditEntry.user_id == user_id)

        query = query.order_by(AuditEntry.timestamp.desc()).limit(limit)

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def count_by_user(
        self,
        user_id: UUID,
        entity_type: str | None = None,
    ) -> int:
        """Count audit entries for a user."""
        from sqlalchemy import func

        query = select(func.count(AuditEntry.id)).where(
            AuditEntry.user_id == user_id
        )

        if entity_type is not None:
            query = query.where(AuditEntry.entity_type == entity_type)

        result = await self.session.execute(query)
        return result.scalar() or 0

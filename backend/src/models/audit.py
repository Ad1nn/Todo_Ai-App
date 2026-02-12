"""Audit entry model definitions for activity tracking."""

from datetime import datetime
from enum import Enum
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import JSON, String
from sqlmodel import Field, SQLModel


class AuditAction(str, Enum):
    """Types of auditable actions."""

    CREATE = "create"
    UPDATE = "update"
    COMPLETE = "complete"
    DELETE = "delete"


class AuditEntryBase(SQLModel):
    """Base audit entry fields shared across schemas."""

    entity_type: str = Field(max_length=50)  # e.g., "task", "notification"
    entity_id: UUID
    action: AuditAction = Field(sa_type=String(20))


class AuditEntry(AuditEntryBase, table=True):
    """Audit entry database model."""

    __tablename__ = "audit_entry"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="user.id", index=True)
    before_value: dict[str, Any] | None = Field(default=None, sa_type=JSON)
    after_value: dict[str, Any] | None = Field(default=None, sa_type=JSON)
    timestamp: datetime = Field(default_factory=datetime.utcnow, index=True)
    extra_data: dict[str, Any] | None = Field(default=None, sa_type=JSON)


class AuditEntryCreate(SQLModel):
    """Schema for creating a new audit entry."""

    user_id: UUID
    entity_type: str = Field(max_length=50)
    entity_id: UUID
    action: AuditAction
    before_value: dict[str, Any] | None = None
    after_value: dict[str, Any] | None = None
    extra_data: dict[str, Any] | None = None


class AuditEntryPublic(AuditEntryBase):
    """Public audit entry data."""

    id: UUID
    user_id: UUID
    before_value: dict[str, Any] | None = None
    after_value: dict[str, Any] | None = None
    timestamp: datetime
    extra_data: dict[str, Any] | None = None

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import List, Optional
from uuid import uuid4


REQUIRED_AUDIT_FIELDS = [
    "audit_event_id",
    "event_name",
    "actor_id",
    "actor_role",
    "tenant_id",
    "resource_type",
    "resource_id",
    "action_result",
    "correlation_id",
    "occurred_at",
]


@dataclass
class AuditEvent:
    audit_event_id: str
    event_name: str
    actor_id: str
    actor_role: str
    tenant_id: str
    clinic_id: Optional[str]
    resource_type: str
    resource_id: str
    action_result: str
    reason_code: Optional[str]
    correlation_id: str
    occurred_at: str


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def emit_audit_event(
    event_name: str,
    actor_id: str,
    actor_role: str,
    tenant_id: str,
    clinic_id: Optional[str],
    resource_type: str,
    resource_id: str,
    action_result: str,
    reason_code: Optional[str],
    correlation_id: str,
) -> AuditEvent:
    return AuditEvent(
        audit_event_id=str(uuid4()),
        event_name=event_name,
        actor_id=actor_id,
        actor_role=actor_role,
        tenant_id=tenant_id,
        clinic_id=clinic_id,
        resource_type=resource_type,
        resource_id=resource_id,
        action_result=action_result,
        reason_code=reason_code,
        correlation_id=correlation_id,
        occurred_at=utc_now_iso(),
    )


def validate_audit_event(event: AuditEvent) -> List[str]:
    """Return list of required field names that are missing or empty."""
    missing = []
    for field in REQUIRED_AUDIT_FIELDS:
        value = getattr(event, field, None)
        if value is None or value == "":
            missing.append(field)
    return missing


def serialize_audit_event(event: AuditEvent) -> dict:
    """Return a deterministic dict representation with keys in sorted order."""
    return dict(sorted(asdict(event).items()))

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4


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


def serialize_audit_event(event: AuditEvent) -> dict:
    return asdict(event)

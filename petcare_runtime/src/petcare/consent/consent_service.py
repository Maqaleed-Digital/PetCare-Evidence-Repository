from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4


STATUS_ACTIVE = "active"
STATUS_REVOKED = "revoked"


@dataclass
class ConsentRecord:
    consent_record_id: str
    pet_id: str
    owner_id: str
    consent_scope: str
    purpose_of_use: str
    granted_to_role: str
    status: str
    granted_at: str
    revoked_at: Optional[str]
    captured_by_actor_id: str
    audit_reference_id: str


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def create_consent_record(
    pet_id: str,
    owner_id: str,
    consent_scope: str,
    purpose_of_use: str,
    granted_to_role: str,
    captured_by_actor_id: str,
    audit_reference_id: str,
) -> ConsentRecord:
    return ConsentRecord(
        consent_record_id=str(uuid4()),
        pet_id=pet_id,
        owner_id=owner_id,
        consent_scope=consent_scope,
        purpose_of_use=purpose_of_use,
        granted_to_role=granted_to_role,
        status=STATUS_ACTIVE,
        granted_at=utc_now_iso(),
        revoked_at=None,
        captured_by_actor_id=captured_by_actor_id,
        audit_reference_id=audit_reference_id,
    )


def revoke_consent_record(record: ConsentRecord) -> ConsentRecord:
    record.status = STATUS_REVOKED
    record.revoked_at = utc_now_iso()
    return record

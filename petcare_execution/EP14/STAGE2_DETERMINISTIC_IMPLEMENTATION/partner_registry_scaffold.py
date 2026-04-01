from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import List


ALLOWED_STATUSES = [
    "INACTIVE",
    "SANDBOX_ENABLED",
    "VALIDATING",
    "CERTIFIED",
    "ACTIVE",
    "SUSPENDED",
    "REVOKED",
]

ALLOWED_CERTIFICATION_STATES = [
    "NOT_STARTED",
    "IN_PROGRESS",
    "PASSED",
    "FAILED",
    "EXPIRED",
]


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


@dataclass(frozen=True)
class PartnerRecord:
    partner_id: str
    legal_name: str
    display_name: str
    tenant_scope: List[str]
    allowed_scopes: List[str]
    status: str
    sandbox_enabled: bool
    certification_state: str
    created_at: str
    updated_at: str


def build_partner_record(
    partner_id: str,
    legal_name: str,
    display_name: str,
    tenant_scope: List[str],
    allowed_scopes: List[str],
    status: str,
    sandbox_enabled: bool,
    certification_state: str,
) -> PartnerRecord:
    if status not in ALLOWED_STATUSES:
        raise ValueError(f"Unsupported partner status: {status}")
    if certification_state not in ALLOWED_CERTIFICATION_STATES:
        raise ValueError(f"Unsupported certification state: {certification_state}")
    if status == "ACTIVE" and certification_state != "PASSED":
        raise ValueError("ACTIVE requires PASSED certification state.")
    now = utc_now_iso()
    return PartnerRecord(
        partner_id=partner_id,
        legal_name=legal_name,
        display_name=display_name,
        tenant_scope=tenant_scope,
        allowed_scopes=allowed_scopes,
        status=status,
        sandbox_enabled=sandbox_enabled,
        certification_state=certification_state,
        created_at=now,
        updated_at=now,
    )


def record_to_json(record: PartnerRecord) -> str:
    return json.dumps(asdict(record), indent=2, sort_keys=True)


if __name__ == "__main__":
    example = build_partner_record(
        partner_id="partner_001",
        legal_name="Example Partner Legal Name",
        display_name="Example Partner",
        tenant_scope=["tenant_001"],
        allowed_scopes=["orders.write_request", "webhooks.manage"],
        status="SANDBOX_ENABLED",
        sandbox_enabled=True,
        certification_state="IN_PROGRESS",
    )
    print(record_to_json(example))

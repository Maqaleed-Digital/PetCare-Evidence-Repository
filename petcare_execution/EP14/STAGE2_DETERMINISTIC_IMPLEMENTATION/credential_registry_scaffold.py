from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Optional


ALLOWED_ENVIRONMENTS = [
    "SANDBOX",
    "PRODUCTION_REFERENCE_ONLY",
]

ALLOWED_CREDENTIAL_TYPES = [
    "SANDBOX_API_KEY",
    "SANDBOX_OAUTH_CLIENT",
    "PRODUCTION_API_KEY_REFERENCE",
    "PRODUCTION_OAUTH_CLIENT_REFERENCE",
]

ALLOWED_STATUSES = [
    "ISSUED",
    "ACTIVE",
    "ROTATION_PENDING",
    "REVOKED",
]


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


@dataclass(frozen=True)
class CredentialRecord:
    credential_id: str
    partner_id: str
    environment: str
    credential_type: str
    status: str
    issued_at: str
    rotated_at: Optional[str]
    revoked_at: Optional[str]


def build_credential_record(
    credential_id: str,
    partner_id: str,
    environment: str,
    credential_type: str,
    status: str,
    rotated_at: Optional[str] = None,
    revoked_at: Optional[str] = None,
) -> CredentialRecord:
    if environment not in ALLOWED_ENVIRONMENTS:
        raise ValueError(f"Unsupported environment: {environment}")
    if credential_type not in ALLOWED_CREDENTIAL_TYPES:
        raise ValueError(f"Unsupported credential type: {credential_type}")
    if status not in ALLOWED_STATUSES:
        raise ValueError(f"Unsupported status: {status}")
    if environment == "SANDBOX" and credential_type.startswith("PRODUCTION_"):
        raise ValueError("Sandbox environment cannot use production credential types.")
    if environment == "PRODUCTION_REFERENCE_ONLY" and credential_type.startswith("SANDBOX_"):
        raise ValueError("Production reference environment cannot use sandbox credential types.")
    return CredentialRecord(
        credential_id=credential_id,
        partner_id=partner_id,
        environment=environment,
        credential_type=credential_type,
        status=status,
        issued_at=utc_now_iso(),
        rotated_at=rotated_at,
        revoked_at=revoked_at,
    )


def record_to_json(record: CredentialRecord) -> str:
    return json.dumps(asdict(record), indent=2, sort_keys=True)


if __name__ == "__main__":
    example = build_credential_record(
        credential_id="cred_001",
        partner_id="partner_001",
        environment="SANDBOX",
        credential_type="SANDBOX_API_KEY",
        status="ACTIVE",
    )
    print(record_to_json(example))

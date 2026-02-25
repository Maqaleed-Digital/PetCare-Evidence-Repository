from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from FND.CODE_SCAFFOLD.storage.audit_bundle_verifier import AuditBundleVerifyResult, verify_audit_bundle


@dataclass
class AuditVerificationRequest:
    bundle: Dict[str, Any]
    require_signature: bool = False
    strict_sequence: bool = True


@dataclass
class AuditVerificationResponse:
    ok: bool
    errors: List[str]
    details: Dict[str, Any]


class AuditVerificationService:
    """
    PH28: Integration wrapper around PH27 verifier.

    Goals:
    - Provide a stable call surface for future API wiring (FastAPI or background jobs)
    - Normalize response structure for UI/runtime consumption
    - Keep all logic deterministic and testable
    """

    def __init__(self, signer: Optional[Any] = None):
        self._signer = signer

    def verify(self, req: AuditVerificationRequest) -> AuditVerificationResponse:
        res: AuditBundleVerifyResult = verify_audit_bundle(
            req.bundle,
            signer=self._signer,
            require_signature=req.require_signature,
            strict_sequence=req.strict_sequence,
        )

        details = {
            "tenant_id": res.tenant_id,
            "event_count": res.event_count,
            "first_sequence": res.first_sequence,
            "last_sequence": res.last_sequence,
            "bundle_checksum_ok": res.bundle_checksum_ok,
            "signature_present": res.signature_present,
            "signature_ok": res.signature_ok,
        }

        return AuditVerificationResponse(
            ok=res.ok,
            errors=list(res.errors),
            details=details,
        )


__all__ = [
    "AuditVerificationRequest",
    "AuditVerificationResponse",
    "AuditVerificationService",
]

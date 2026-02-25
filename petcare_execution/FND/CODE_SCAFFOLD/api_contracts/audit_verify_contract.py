from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

from FND.CODE_SCAFFOLD.services.audit_verification_service import (
    AuditVerificationRequest,
    AuditVerificationResponse,
)


DEFAULT_REQUIRE_SIGNATURE = False
DEFAULT_STRICT_SEQUENCE = True
CONTRACT_VERSION = "PH29-A.v1"


@dataclass
class AuditVerifyContractError:
    code: str
    message: str
    path: str = ""


def _err(code: str, message: str, path: str = "") -> AuditVerifyContractError:
    return AuditVerifyContractError(code=code, message=message, path=path)


def parse_audit_verify_payload(payload: Any) -> Tuple[Optional[AuditVerificationRequest], List[AuditVerifyContractError]]:
    """
    Parse inbound API payload (dict-like) into an AuditVerificationRequest.

    Expected payload:
    {
      "bundle": { ... required ... },
      "require_signature": bool (optional, default False),
      "strict_sequence": bool (optional, default True)
    }

    This function never raises; it returns (request_or_none, errors[]).
    """
    errors: List[AuditVerifyContractError] = []

    if not isinstance(payload, dict):
        return None, [_err("invalid_payload", "payload must be a JSON object", path="$")]

    if "bundle" not in payload:
        errors.append(_err("missing_field", "bundle is required", path="$.bundle"))
        return None, errors

    bundle = payload.get("bundle")
    if not isinstance(bundle, dict):
        errors.append(_err("invalid_field", "bundle must be an object", path="$.bundle"))

    require_signature = payload.get("require_signature", DEFAULT_REQUIRE_SIGNATURE)
    if not isinstance(require_signature, bool):
        errors.append(_err("invalid_field", "require_signature must be boolean", path="$.require_signature"))

    strict_sequence = payload.get("strict_sequence", DEFAULT_STRICT_SEQUENCE)
    if not isinstance(strict_sequence, bool):
        errors.append(_err("invalid_field", "strict_sequence must be boolean", path="$.strict_sequence"))

    if errors:
        return None, errors

    return (
        AuditVerificationRequest(
            bundle=bundle,
            require_signature=require_signature,
            strict_sequence=strict_sequence,
        ),
        [],
    )


def contract_error_response(errors: List[AuditVerifyContractError]) -> Dict[str, Any]:
    """
    Standard error response when request parsing/validation fails.
    JSON-serializable.
    """
    return {
        "contract_version": CONTRACT_VERSION,
        "ok": False,
        "errors": [
            {"code": e.code, "message": e.message, "path": e.path}
            for e in errors
        ],
        "details": {},
    }


def verification_response_to_dict(resp: AuditVerificationResponse) -> Dict[str, Any]:
    """
    Convert service response to JSON-serializable dict for API output.

    Output shape:
    {
      "contract_version": "...",
      "ok": bool,
      "errors": [str],
      "details": { ... }
    }
    """
    return {
        "contract_version": CONTRACT_VERSION,
        "ok": bool(resp.ok),
        "errors": list(resp.errors),
        "details": dict(resp.details),
    }


__all__ = [
    "CONTRACT_VERSION",
    "DEFAULT_REQUIRE_SIGNATURE",
    "DEFAULT_STRICT_SEQUENCE",
    "AuditVerifyContractError",
    "parse_audit_verify_payload",
    "contract_error_response",
    "verification_response_to_dict",
]

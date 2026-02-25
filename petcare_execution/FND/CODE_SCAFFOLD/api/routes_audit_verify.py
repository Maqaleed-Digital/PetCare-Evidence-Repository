from __future__ import annotations

def _coerce_audit_verify_parse_result(parsed):
    if hasattr(parsed, "ok"):
        return parsed

    class _Parsed:
        def __init__(self, ok=False, error=None, bundle=None, strict_sequence=None):
            self.ok = bool(ok)
            self.error = error if isinstance(error, dict) else {}
            self.bundle = bundle
            self.strict_sequence = strict_sequence

    if isinstance(parsed, tuple):
        ok = parsed[0] if len(parsed) >= 1 else False
        error = parsed[1] if len(parsed) >= 2 else {}
        bundle = None
        strict_sequence = None

        if len(parsed) >= 3 and isinstance(parsed[2], dict):
            d = parsed[2]
            bundle = d.get("bundle")
            strict_sequence = d.get("strict_sequence")

        return _Parsed(ok=ok, error=error, bundle=bundle, strict_sequence=strict_sequence)

    return _Parsed(ok=False, error={"ok": False, "code": "invalid_parse_result", "message": "Unsupported parse result shape."})

from typing import Any, Dict

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from FND.CODE_SCAFFOLD.api_contracts.audit_verify_contract import (
    contract_error_response,
    parse_audit_verify_payload,
    verification_response_to_dict,
)
from FND.CODE_SCAFFOLD.services.audit_verification_service import (
    AuditVerificationRequest,
    AuditVerificationService,
)


def register_audit_verify_routes(app: FastAPI) -> None:
    """
    PH29-B: HTTP wiring for audit verification contract.

    Endpoint:
      POST /api/audit/verify

    Input:
      JSON body parsed by parse_audit_verify_payload()

    Output:
      JSON dict produced by verification_response_to_dict()
      or contract_error_response() on contract errors.
    """

    @app.post("/api/audit/verify")
    async def audit_verify_endpoint(request: Request) -> JSONResponse:
        try:
            payload: Dict[str, Any] = await request.json()
        except Exception:
            return JSONResponse(
                status_code=400,
                content=contract_error_response(
                    code="invalid_json",
                    message="Request body must be valid JSON.",
                ),
            )

        parsed = parse_audit_verify_payload(payload)
        parsed = _coerce_audit_verify_parse_result(parsed)
        if not parsed.ok:
            return JSONResponse(status_code=400, content=parsed.error)

        svc = AuditVerificationService(signer=None)

        bundle = parsed.bundle
        if bundle is None:
            bundle = payload.get("bundle") if isinstance(payload, dict) else None
        if not isinstance(bundle, dict):
            return JSONResponse(
                status_code=400,
                content=contract_error_response(
                    code="invalid_bundle",
                    message="bundle is required and must be an object.",
                ),
            )

        resp = svc.verify(
            AuditVerificationRequest(
                bundle=bundle,
                strict_sequence=parsed.strict_sequence,
            )
        )
        return JSONResponse(status_code=200, content=verification_response_to_dict(resp))

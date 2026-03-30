import pytest

from FND.CODE_SCAFFOLD.api_contracts.audit_verify_contract import (
    CONTRACT_VERSION,
    DEFAULT_REQUIRE_SIGNATURE,
    DEFAULT_STRICT_SEQUENCE,
    contract_error_response,
    parse_audit_verify_payload,
    verification_response_to_dict,
)
from FND.CODE_SCAFFOLD.services.audit_verification_service import (
    AuditVerificationResponse,
)


def _minimal_bundle() -> dict:
    return {
        "tenant_id": "t1",
        "export_id": "exp-001",
        "exported_at_utc": "2026-01-01T00:00:00.000Z",
        "event_count": 0,
        "first_sequence": None,
        "last_sequence": None,
        "events": [],
    }


def test_parse_rejects_non_object_payload():
    req, errs = parse_audit_verify_payload("nope")
    assert req is None
    assert len(errs) == 1
    assert errs[0].code == "invalid_payload"


def test_parse_requires_bundle():
    req, errs = parse_audit_verify_payload({})
    assert req is None
    assert any(e.code == "missing_field" for e in errs)


def test_parse_rejects_non_object_bundle():
    req, errs = parse_audit_verify_payload({"bundle": "x"})
    assert req is None
    assert any(e.code == "invalid_field" and e.path == "$.bundle" for e in errs)


def test_parse_defaults_are_applied():
    req, errs = parse_audit_verify_payload({"bundle": _minimal_bundle()})
    assert errs == []
    assert req is not None
    assert req.require_signature == DEFAULT_REQUIRE_SIGNATURE
    assert req.strict_sequence == DEFAULT_STRICT_SEQUENCE


def test_parse_accepts_explicit_flags():
    req, errs = parse_audit_verify_payload(
        {
            "bundle": _minimal_bundle(),
            "require_signature": True,
            "strict_sequence": False,
        }
    )
    assert errs == []
    assert req is not None
    assert req.require_signature is True
    assert req.strict_sequence is False


def test_parse_rejects_invalid_flag_types():
    req, errs = parse_audit_verify_payload(
        {
            "bundle": _minimal_bundle(),
            "require_signature": "yes",
            "strict_sequence": 1,
        }
    )
    assert req is None
    assert any(e.path == "$.require_signature" for e in errs)
    assert any(e.path == "$.strict_sequence" for e in errs)


def test_contract_error_response_is_serializable_and_shaped():
    resp = contract_error_response(
        [
            type("E", (), {"code": "c", "message": "m", "path": "$.x"})(),
        ]
    )
    assert resp["contract_version"] == CONTRACT_VERSION
    assert resp["ok"] is False
    assert isinstance(resp["errors"], list)
    assert resp["errors"][0]["path"] == "$.x"
    assert resp["details"] == {}


def test_verification_response_to_dict_shape():
    svc_resp = AuditVerificationResponse(ok=True, errors=[], details={"k": "v"})
    out = verification_response_to_dict(svc_resp)
    assert out["contract_version"] == CONTRACT_VERSION
    assert out["ok"] is True
    assert out["errors"] == []
    assert out["details"]["k"] == "v"

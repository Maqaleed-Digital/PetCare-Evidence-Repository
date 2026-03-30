import pytest

from FND.CODE_SCAFFOLD.services.audit_verification_service import (
    AuditVerificationRequest,
    AuditVerificationService,
)
from FND.CODE_SCAFFOLD.storage.audit_bundle_verifier import _fallback_bundle_checksum


def _make_events(tenant_id: str, count: int) -> list:
    events = []
    prev = None
    for i in range(1, count + 1):
        e = {
            "event_id": f"e{i}",
            "tenant_id": tenant_id,
            "sequence": i,
            "timestamp_utc": f"2026-01-01T00:00:{i:02d}.000Z",
            "checksum": f"chk{i}",
            "prev_checksum": prev,
        }
        prev = e["checksum"]
        events.append(e)
    return events


def _make_bundle(tenant_id: str = "t1", count: int = 3) -> dict:
    bundle = {
        "tenant_id": tenant_id,
        "export_id": "exp-001",
        "exported_at_utc": "2026-01-01T00:00:00.000Z",
        "event_count": count,
        "first_sequence": 1,
        "last_sequence": count,
        "events": _make_events(tenant_id, count),
    }
    bundle["bundle_checksum"] = _fallback_bundle_checksum(bundle)
    return bundle


class _DummySigner:
    def __init__(self, ok: bool = True):
        self._ok = ok

    def verify_bundle(self, bundle: dict) -> bool:
        return self._ok


def test_service_ok_basic():
    svc = AuditVerificationService(signer=None)
    req = AuditVerificationRequest(bundle=_make_bundle())
    resp = svc.verify(req)
    assert resp.ok is True
    assert resp.errors == []
    assert resp.details["bundle_checksum_ok"] is True
    assert resp.details["signature_present"] is False


def test_service_reports_tenant_mismatch():
    svc = AuditVerificationService(signer=None)
    b = _make_bundle(tenant_id="a")
    b["events"][0]["tenant_id"] = "b"
    b["bundle_checksum"] = _fallback_bundle_checksum(b)

    resp = svc.verify(AuditVerificationRequest(bundle=b))
    assert resp.ok is False
    assert any("tenant_id mismatch" in e for e in resp.errors)


def test_service_require_signature_fails_when_missing():
    svc = AuditVerificationService(signer=None)
    b = _make_bundle()
    resp = svc.verify(AuditVerificationRequest(bundle=b, require_signature=True))
    assert resp.ok is False
    assert any("signature required" in e for e in resp.errors)


def test_service_signature_present_requires_signer():
    svc = AuditVerificationService(signer=None)
    b = _make_bundle()
    b["_signature"] = "abc"
    b["bundle_checksum"] = _fallback_bundle_checksum(b)

    resp = svc.verify(AuditVerificationRequest(bundle=b))
    assert resp.ok is False
    assert any("no signer provided" in e for e in resp.errors)


def test_service_signature_valid_with_dummy_signer():
    svc = AuditVerificationService(signer=_DummySigner(ok=True))
    b = _make_bundle()
    b["_signature"] = "abc"
    b["bundle_checksum"] = _fallback_bundle_checksum(b)

    resp = svc.verify(AuditVerificationRequest(bundle=b, require_signature=True))
    assert resp.ok is True
    assert resp.details["signature_present"] is True
    assert resp.details["signature_ok"] is True


def test_service_signature_invalid_with_dummy_signer():
    svc = AuditVerificationService(signer=_DummySigner(ok=False))
    b = _make_bundle()
    b["_signature"] = "abc"
    b["bundle_checksum"] = _fallback_bundle_checksum(b)

    resp = svc.verify(AuditVerificationRequest(bundle=b, require_signature=True))
    assert resp.ok is False
    assert any("signature invalid" in e for e in resp.errors)


def test_service_strict_sequence_toggle_still_fails_monotonicity():
    svc = AuditVerificationService(signer=None)
    b = _make_bundle(count=3)
    b["events"][1]["sequence"] = 99
    b["bundle_checksum"] = _fallback_bundle_checksum(b)

    strict_resp = svc.verify(AuditVerificationRequest(bundle=b, strict_sequence=True))
    assert strict_resp.ok is False

    non_strict_resp = svc.verify(AuditVerificationRequest(bundle=b, strict_sequence=False))
    assert non_strict_resp.ok is False


def test_service_details_are_stable_and_serializable():
    svc = AuditVerificationService(signer=None)
    b = _make_bundle()
    resp = svc.verify(AuditVerificationRequest(bundle=b))
    assert isinstance(resp.details, dict)
    assert resp.details["tenant_id"] == "t1"
    assert resp.details["event_count"] == 3

import copy
import importlib

import pytest

from FND.CODE_SCAFFOLD.storage.audit_bundle_verifier import (
    verify_audit_bundle,
    _fallback_bundle_checksum,
)

signing = importlib.import_module("FND.CODE_SCAFFOLD.storage.audit_bundle_signing")


def _reset_signer_singleton():
    reset_fn = getattr(signing, "reset_bundle_signer", None)
    if callable(reset_fn):
        reset_fn()


def _get_signer():
    get_fn = getattr(signing, "get_bundle_signer", None)
    if not callable(get_fn):
        return None
    return get_fn()


def _ensure_signing_key(signer, key_id: str = "k1"):
    gen = getattr(signer, "generate_key", None)
    if callable(gen):
        gen(key_id=key_id)
        return True
    return False


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
    def __init__(self, ok: bool = True, raises: bool = False):
        self._ok = ok
        self._raises = raises

    def verify_bundle(self, bundle: dict) -> bool:
        if self._raises:
            raise RuntimeError("boom")
        return self._ok


def test_basic_bundle_verifies_without_signature():
    bundle = _make_bundle()
    res = verify_audit_bundle(bundle, require_signature=False)
    assert res.ok is True
    assert res.bundle_checksum_ok is True
    assert res.signature_present is False


def test_hash_chain_break_fails():
    bundle = _make_bundle()
    bundle["events"][2]["prev_checksum"] = "WRONG"
    bundle["bundle_checksum"] = _fallback_bundle_checksum(bundle)
    res = verify_audit_bundle(bundle, require_signature=False)
    assert res.ok is False
    assert any("hash-chain broken" in e for e in res.errors)


def test_sequence_non_contiguous_fails_by_default():
    bundle = _make_bundle()
    bundle["events"][1]["sequence"] = 99
    bundle["bundle_checksum"] = _fallback_bundle_checksum(bundle)
    res = verify_audit_bundle(bundle, strict_sequence=True, require_signature=False)
    assert res.ok is False
    assert any("contiguous" in e for e in res.errors)


def test_tenant_isolation_mismatch_fails():
    bundle = _make_bundle(tenant_id="tenant-a")
    bundle["events"][0]["tenant_id"] = "tenant-b"
    bundle["bundle_checksum"] = _fallback_bundle_checksum(bundle)
    res = verify_audit_bundle(bundle, require_signature=False)
    assert res.ok is False
    assert any("tenant_id mismatch" in e for e in res.errors)


def test_event_count_mismatch_fails():
    bundle = _make_bundle(count=3)
    bundle["event_count"] = 2
    bundle["bundle_checksum"] = _fallback_bundle_checksum(bundle)
    res = verify_audit_bundle(bundle, require_signature=False)
    assert res.ok is False
    assert any("event_count mismatch" in e for e in res.errors)


def test_signature_required_missing_fails():
    bundle = _make_bundle()
    res = verify_audit_bundle(bundle, require_signature=True)
    assert res.ok is False
    assert any("signature required" in e for e in res.errors)


def test_signature_present_but_no_signer_fails_legacy_fields():
    bundle = _make_bundle()
    bundle["_signature"] = "abc"
    bundle["_signature_algorithm"] = "hmac-sha256"
    bundle["_signature_key_id"] = "k1"
    bundle["bundle_checksum"] = _fallback_bundle_checksum(bundle)
    res = verify_audit_bundle(bundle, signer=None, require_signature=False)
    assert res.ok is False
    assert any("no signer provided" in e for e in res.errors)


def test_signature_present_but_no_signer_fails_ph26_fields():
    bundle = _make_bundle()
    bundle["signature_b64"] = "abc"
    bundle["signature_algorithm"] = "ed25519"
    bundle["signing_public_key_b64"] = "pub"
    bundle["signing_key_fingerprint"] = "fp"
    bundle["signed_at_utc"] = "2026-01-01T00:00:00.000Z"
    bundle["bundle_checksum"] = _fallback_bundle_checksum(bundle)
    res = verify_audit_bundle(bundle, signer=None, require_signature=False)
    assert res.ok is False
    assert any("no signer provided" in e for e in res.errors)


def test_bundle_checksum_excludes_signature_fields():
    bundle = _make_bundle()
    bundle["signature_b64"] = "abc"
    bundle["signature_algorithm"] = "ed25519"
    bundle["signed_at_utc"] = "2026-01-01T00:00:00.000Z"
    bundle["bundle_checksum"] = _fallback_bundle_checksum(bundle)
    res = verify_audit_bundle(bundle, require_signature=False)
    assert res.bundle_checksum_ok is True


def test_signature_dummy_signer_accepts():
    bundle = _make_bundle()
    bundle["_signature"] = "abc"
    bundle["bundle_checksum"] = _fallback_bundle_checksum(bundle)
    signer = _DummySigner(ok=True)
    res = verify_audit_bundle(bundle, signer=signer, require_signature=True)
    assert res.ok is True
    assert res.signature_present is True
    assert res.signature_ok is True


def test_signature_dummy_signer_rejects():
    bundle = _make_bundle()
    bundle["_signature"] = "abc"
    bundle["bundle_checksum"] = _fallback_bundle_checksum(bundle)
    signer = _DummySigner(ok=False)
    res = verify_audit_bundle(bundle, signer=signer, require_signature=True)
    assert res.ok is False
    assert any("signature invalid" in e for e in res.errors)


def test_signature_dummy_signer_raises():
    bundle = _make_bundle()
    bundle["_signature"] = "abc"
    bundle["bundle_checksum"] = _fallback_bundle_checksum(bundle)
    signer = _DummySigner(ok=True, raises=True)
    res = verify_audit_bundle(bundle, signer=signer, require_signature=True)
    assert res.ok is False
    assert any("raised exception" in e for e in res.errors)


def test_signature_roundtrip_if_signer_available():
    _reset_signer_singleton()
    signer = _get_signer()
    if signer is None:
        pytest.skip("get_bundle_signer not available in this repo")

    if not _ensure_signing_key(signer, key_id="k1"):
        pytest.skip("signer.generate_key not available; cannot provision key for signing")

    bundle = _make_bundle()
    sign_fn = getattr(signer, "sign_bundle", None)
    if not callable(sign_fn):
        pytest.skip("signer.sign_bundle not available in this repo")

    signed = sign_fn(bundle, key_id="k1")

    res = verify_audit_bundle(signed, signer=signer, require_signature=True)
    assert res.ok is True
    assert res.signature_present is True
    assert res.signature_ok is True


def test_signature_tamper_detected_if_signer_available():
    _reset_signer_singleton()
    signer = _get_signer()
    if signer is None:
        pytest.skip("get_bundle_signer not available in this repo")

    if not _ensure_signing_key(signer, key_id="k1"):
        pytest.skip("signer.generate_key not available; cannot provision key for signing")

    bundle = _make_bundle()
    sign_fn = getattr(signer, "sign_bundle", None)
    if not callable(sign_fn):
        pytest.skip("signer.sign_bundle not available in this repo")

    signed = sign_fn(bundle, key_id="k1")

    tampered = copy.deepcopy(signed)
    tampered["events"][0]["event_id"] = "tampered"
    tampered["bundle_checksum"] = _fallback_bundle_checksum(tampered)

    res = verify_audit_bundle(tampered, signer=signer, require_signature=True)
    assert res.ok is False
    assert any("signature invalid" in e or "raised exception" in e for e in res.errors)

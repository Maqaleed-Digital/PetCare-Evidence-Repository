import os
import tempfile

import pytest

from FND.CODE_SCAFFOLD.storage.audit_bundle_signing import (
    CRYPTOGRAPHY_AVAILABLE,
    canonical_json_bytes,
    sign_bundle,
    strip_signature_fields,
    verify_signed_bundle,
    generate_ed25519_keypair_bytes,
)


def sample_bundle():
    return {
        "tenant_id": "tenant-1",
        "export_id": "abcd1234",
        "event_count": 1,
        "events": [
            {
                "event_id": "e1",
                "tenant_id": "tenant-1",
                "event_name": "x",
                "category": "data",
                "severity": "INFO",
                "actor_id": "u",
                "actor_type": "user",
                "action": "create",
                "sequence": 1,
                "payload": {"k": "v"},
                "checksum": "c",
                "prev_checksum": None,
                "timestamp_utc": "2026-02-22T20:00:00.000Z",
            }
        ],
        "bundle_checksum": "deadbeef",
        "exported_at_utc": "2026-02-22T20:00:00.000Z",
    }


def test_canonical_json_is_stable():
    b1 = sample_bundle()
    b2 = dict(sample_bundle())
    b2["events"] = list(reversed(b2["events"]))
    assert canonical_json_bytes(b1) == canonical_json_bytes(b2)


def test_strip_signature_fields_removes_only_signing_metadata():
    b = sample_bundle()
    signed = dict(b)
    signed["signature_algorithm"] = "hmac-sha256"
    signed["signature_b64"] = "AA=="
    signed["signing_key_fingerprint"] = "x"
    signed["signing_public_key_b64"] = ""
    signed["signed_at_utc"] = "2026-02-22T20:00:00.000Z"
    stripped = strip_signature_fields(signed)
    assert "signature_algorithm" not in stripped
    assert "signature_b64" not in stripped
    assert "signed_at_utc" not in stripped
    assert stripped["tenant_id"] == "tenant-1"


def test_hmac_sign_and_verify_roundtrip():
    bundle = sample_bundle()
    secret = b"unit-test-secret-key"
    signed = sign_bundle(bundle, algorithm="hmac-sha256", hmac_secret_key_bytes=secret)
    assert signed["signature_algorithm"] == "hmac-sha256"
    assert signed["signature_b64"]
    assert verify_signed_bundle(signed, hmac_secret_key_bytes=secret) is True


def test_hmac_tamper_detected():
    bundle = sample_bundle()
    secret = b"unit-test-secret-key"
    signed = sign_bundle(bundle, algorithm="hmac-sha256", hmac_secret_key_bytes=secret)

    tampered = dict(signed)
    tampered["event_count"] = 999
    assert verify_signed_bundle(tampered, hmac_secret_key_bytes=secret) is False


def test_hmac_signature_is_deterministic_for_same_key_and_payload():
    bundle = sample_bundle()
    secret = b"unit-test-secret-key"
    s1 = sign_bundle(bundle, algorithm="hmac-sha256", hmac_secret_key_bytes=secret)
    s2 = sign_bundle(bundle, algorithm="hmac-sha256", hmac_secret_key_bytes=secret)
    assert s1["signature_b64"] == s2["signature_b64"]


@pytest.mark.skipif(not CRYPTOGRAPHY_AVAILABLE, reason="cryptography not available; ed25519 signing skipped")
def test_ed25519_sign_and_verify_roundtrip():
    bundle = sample_bundle()
    priv_raw, pub_raw = generate_ed25519_keypair_bytes()
    signed = sign_bundle(
        bundle,
        algorithm="ed25519",
        ed25519_private_key_raw=priv_raw,
        ed25519_public_key_raw=pub_raw,
    )
    assert signed["signature_algorithm"] == "ed25519"
    assert signed["signing_public_key_b64"]
    assert verify_signed_bundle(signed) is True


@pytest.mark.skipif(not CRYPTOGRAPHY_AVAILABLE, reason="cryptography not available; ed25519 signing skipped")
def test_ed25519_tamper_detected():
    bundle = sample_bundle()
    priv_raw, pub_raw = generate_ed25519_keypair_bytes()
    signed = sign_bundle(
        bundle,
        algorithm="ed25519",
        ed25519_private_key_raw=priv_raw,
        ed25519_public_key_raw=pub_raw,
    )

    tampered = dict(signed)
    tampered["tenant_id"] = "other"
    assert verify_signed_bundle(tampered) is False


@pytest.mark.skipif(not CRYPTOGRAPHY_AVAILABLE, reason="cryptography not available; ed25519 signing skipped")
def test_ed25519_signature_is_deterministic_for_same_key_and_payload():
    bundle = sample_bundle()
    priv_raw, pub_raw = generate_ed25519_keypair_bytes()

    s1 = sign_bundle(
        bundle,
        algorithm="ed25519",
        ed25519_private_key_raw=priv_raw,
        ed25519_public_key_raw=pub_raw,
    )
    s2 = sign_bundle(
        bundle,
        algorithm="ed25519",
        ed25519_private_key_raw=priv_raw,
        ed25519_public_key_raw=pub_raw,
    )
    assert s1["signature_b64"] == s2["signature_b64"]


def test_compatibility_with_existing_audit_export_adapter_if_present():
    """
    If audit_export_adapter exists in this repo, sign its produced bundle without breaking checksum verification.
    This test is resilient: it will skip if dependencies are not available.
    """
    try:
        from FND.CODE_SCAFFOLD.storage.audit_export_adapter import (
            export_audit_ledger_bundle,
            verify_bundle_checksum,
        )
        from FND.CODE_SCAFFOLD.storage.audit_ledger_sqlite import SqliteAuditLedger
    except Exception:
        pytest.skip("export adapter or sqlite ledger not available in environment")

    tmp = tempfile.mkdtemp(prefix="ph26b_")
    ledger = SqliteAuditLedger(data_dir=tmp)

    async def _run():
        await ledger.append(
            tenant_id="tenant-compat",
            event_name="t",
            category="data",
            severity="INFO",
            actor_id="u",
            actor_type="user",
            action="create",
            payload={"k": "v"},
        )
        b = await export_audit_ledger_bundle(ledger, "tenant-compat")
        assert verify_bundle_checksum(b) is True

        secret = b"unit-test-secret-key"
        signed = sign_bundle(b, algorithm="hmac-sha256", hmac_secret_key_bytes=secret)

        assert verify_bundle_checksum(strip_signature_fields(signed)) is True
        assert verify_signed_bundle(signed, hmac_secret_key_bytes=secret) is True

    import asyncio
    asyncio.run(_run())

from __future__ import annotations

from fastapi.testclient import TestClient

from FND.CODE_SCAFFOLD.app import create_app


def _make_minimal_bundle() -> dict:
    """
    Minimal bundle compatible with existing PH27/PH28 contract patterns.

    We avoid signing requirements because the verifier/service supports
    signature skips when cryptography isn't available (and signer=None in HTTP wiring).
    """
    return {
        "schema_version": "1",
        "tenant_id": "t1",
        "bundle_id": "b1",
        "created_at": "2026-02-23T00:00:00Z",
        "events": [
            {
                "sequence": 1,
                "event_id": "e1",
                "event_type": "TEST",
                "created_at": "2026-02-23T00:00:01Z",
                "payload": {"k": "v1"},
                "prev_hash": None,
                "hash": "00",
            },
            {
                "sequence": 2,
                "event_id": "e2",
                "event_type": "TEST",
                "created_at": "2026-02-23T00:00:02Z",
                "payload": {"k": "v2"},
                "prev_hash": "00",
                "hash": "01",
            },
        ],
        "bundle_checksum": "00",
        "signature": None,
        "signature_alg": None,
        "public_key": None,
    }


def test_http_audit_verify_endpoint_exists_and_returns_contract_shape():
    app = create_app()
    client = TestClient(app)

    body = {
        "contract_version": "1",
        "strict_sequence": True,
        "bundle": _make_minimal_bundle(),
    }

    r = client.post("/api/audit/verify", json=body)
    assert r.status_code in (200, 400)

    data = r.json()
    assert isinstance(data, dict)

    if r.status_code == 200:
        assert "contract_version" in data
        assert "ok" in data
        assert "errors" in data
        assert "details" in data
    else:
        assert "ok" in data and data["ok"] is False
        assert "code" in data
        assert "message" in data

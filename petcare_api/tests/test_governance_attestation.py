"""W0-E — the governance endpoint must not assert what it cannot compute.

MVC-INC-ATTEST-001. GET /api/governance/status previously returned hard-coded
literals claiming audit_chain_active=true and fail_closed=true while nothing in
the serving path evaluated either. These are ARMED negative controls: each is
demonstrated failing against the original defect before it is trusted.
"""
import re
from pathlib import Path

from fastapi.testclient import TestClient

import main as api

client = TestClient(api.app)

SOURCE = Path(__file__).resolve().parents[1] / "main.py"


def test_t_gov_01_chain_claim_matches_independent_verification():
    """T-GOV-01 — the reported claim must equal an independent check.

    W0-G wired the chain into the serving path, so the honest answer flipped from
    False to True. The INVARIANT this guards is unchanged and is the point of the
    test: the endpoint reports what an independent check computes, never a
    constant. Only the state snapshot moved, because W0-G moved the state.
    """
    api._audit(
        event_name="t.gov.01.probe",
        actor_id="t",
        actor_role="admin",
        tenant_id="t1",
        resource_type="test",
        resource_id="r1",
        action_result="success",
        correlation_id="c1",
    )
    body = client.get("/api/governance/status").json()
    independent = api._audit_chain_active()
    assert body["audit_chain_active"] is independent

    # W0-G: the chain is now computed and linked on every audit write.
    assert independent is True
    assert body["audit_chain_verification"] == "VERIFIED"

    # ...but it is NOT durable. Reported as a separate field so that
    # audit_chain_active can never be read as a persistence claim.
    assert body["audit_chain_persisted"] is False
    assert "not durable" in body["audit_chain_durability"]


def test_t_gov_02_no_governance_field_is_a_hardcoded_true():
    """T-GOV-02 (ARMED) — reintroducing a constant `True` must fail this test.

    The original defect was literally `"audit_chain_active": True` in the
    handler body. This asserts the defect cannot come back.
    """
    src = SOURCE.read_text()
    start = src.index("def governance_status(")
    end = src.index("\n@app.", start) if "\n@app." in src[start:] else len(src)
    handler = src[start:end]

    for field in ("audit_chain_active", "fail_closed", "no_autonomous_execution"):
        assert not re.search(rf'"{field}"\s*:\s*True', handler), (
            f"{field} is a hard-coded True — this is the MVC-INC-ATTEST-001 defect"
        )


def test_t_gov_03_unevaluable_fields_are_reported_not_asserted():
    """Fields this service cannot compute must say so, not guess a value."""
    body = client.get("/api/governance/status").json()
    assert body["fail_closed"] == "NOT_ESTABLISHED"
    assert body["constitutional_status"] == "NOT_ESTABLISHED_BY_THIS_SERVICE"
    assert body["platform_state"] == "NOT_ESTABLISHED_BY_THIS_SERVICE"


def test_t_gov_04_chain_active_requires_persisted_hashes():
    """A chain is only 'active' if every event carries prev_hash and event_hash."""
    saved = list(api.AUDIT_REPO._events)
    try:
        api.AUDIT_REPO._events.clear()
        assert api._audit_chain_active() is False, "empty log is not an active chain"

        api.AUDIT_REPO._events.append({"event_name": "x"})
        assert api._audit_chain_active() is False, "unhashed event is not a chain"

        api.AUDIT_REPO._events.clear()
        api.AUDIT_REPO._events.append({"event_name": "x", "prev_hash": "a", "event_hash": "b"})
        assert api._audit_chain_active() is True, "hashed event should verify"
    finally:
        api.AUDIT_REPO._events.clear()
        api.AUDIT_REPO._events.extend(saved)

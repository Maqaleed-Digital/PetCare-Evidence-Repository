"""W0-G — the audit chain is wired, and breaks are detected, never healed.

CP-2 W0-G: the algorithm at `petcare_execution/FND/security/audit_chain.py`
already existed and was correct; it was imported by nothing. This is integration
work, not new cryptography — the algorithm is REUSED unmodified.

T-CHAIN-01..03 are ARMED negative controls: each asserts that a specific
corruption is DETECTED. A chain that cannot fail these tests is decorative.

The chain proves TAMPER-EVIDENCE. Durability is a SEPARATE property, and W0-G's
discipline is that the service must not blur them — T-CHAIN-05 asserts it reports
both, and reports each correctly for the store it is actually configured with.

These controls run against the in-memory repository, which is the non-production
implementation. They reach into its `_events` list to simulate tampering, which
is the point: a tamper control that could not modify storage would be testing
nothing. The equivalent tampering against PostgreSQL — an `UPDATE` on a stored
row — is asserted in `test_audit_persistence_postgres.py`, and both must detect
it, because the semantics are meant to be identical across the two stores.
"""
import pytest
from fastapi.testclient import TestClient

import main as api

client = TestClient(api.app)


def _emit(name: str = "e") -> dict:
    return api._audit(
        event_name=name,
        actor_id="a",
        actor_role="admin",
        tenant_id="t1",
        resource_type="test",
        resource_id="r",
        action_result="success",
        correlation_id="c",
    )


@pytest.fixture
def clean_log():
    """Isolate the chain for one test, then put it back exactly.

    `AUDIT_REPO._events` is the in-memory repository's storage. Reaching into it
    is deliberate and is what makes the negative controls below real corruptions
    rather than simulated ones.
    """
    events = api.AUDIT_REPO._events
    saved = list(events)
    events.clear()
    yield
    events.clear()
    events.extend(saved)


def test_chain_links_every_event(clean_log):
    """Baseline. Without this the negative controls could pass vacuously."""
    _emit("one")
    _emit("two")
    _emit("three")

    assert api.AUDIT_REPO._events[0]["prev_hash"] == api.AUDIT_CHAIN_GENESIS
    for prev, cur in zip(api.AUDIT_REPO._events, api.AUDIT_REPO._events[1:]):
        assert cur["prev_hash"] == prev["event_hash"], "chain is not linked"

    result = api.verify_audit_chain()
    assert result["ok"] is True, result
    assert result["events"] == 3


def test_t_chain_01_tampering_a_historical_row_is_detected(clean_log):
    """T-CHAIN-01 (ARMED) — edit a stored field, verification must fail.

    This is the control that matters: an attacker who can reach the store edits
    a past event to hide an action. The digest covers the record, so the edit
    breaks verification at exactly that index.
    """
    _emit("one")
    _emit("two")
    _emit("three")
    assert api.verify_audit_chain()["ok"] is True

    api.AUDIT_REPO._events[1]["action_result"] = "denied"   # the tamper

    result = api.verify_audit_chain()
    assert result["ok"] is False, "tampering a historical row went undetected"
    assert result["reason"] == "hash_mismatch"
    assert result["index"] == 1, "the break must localise to the tampered row"


def test_t_chain_02_deleting_a_row_is_detected_as_a_gap(clean_log):
    """T-CHAIN-02 (ARMED) — remove an event, the gap must be detected.

    Deletion is the subtler attack: nothing is edited, so a per-row integrity
    check would pass. The chain catches it because the surviving successor's
    prev_hash no longer matches its new predecessor.
    """
    _emit("one")
    _emit("two")
    _emit("three")
    assert api.verify_audit_chain()["ok"] is True

    del api.AUDIT_REPO._events[1]                            # the gap

    result = api.verify_audit_chain()
    assert result["ok"] is False, "a deleted row left no trace"
    assert result["reason"] == "prev_hash_mismatch"
    assert result["index"] == 1


def test_t_chain_03_a_fork_fails_closed(clean_log):
    """T-CHAIN-03 (ARMED) — two events claiming the same parent must fail.

    A fork is what a replayed or duplicated writer produces. Both branches look
    internally consistent; only the chain position reveals the conflict.
    """
    _emit("one")
    _emit("two")
    forked = dict(api.AUDIT_REPO._events[-1])
    assert api.verify_audit_chain()["ok"] is True

    # A sibling claiming the SAME parent as the event before it: two events at
    # the same chain position.
    api.AUDIT_REPO._events.append(
        {**forked, "audit_event_id": "forked", "event_name": "two-prime"}
    )

    result = api.verify_audit_chain()
    assert result["ok"] is False, "a forked chain verified as sound"
    assert result["reason"] == "prev_hash_mismatch"
    assert result["index"] == 2, "the fork must localise to the sibling"


def test_t_chain_04_a_break_is_reported_never_repaired(clean_log):
    """The chain must not self-heal. Silently rehashing destroys the evidence
    that the log was ever broken — the one thing the chain exists to preserve."""
    _emit("one")
    _emit("two")
    api.AUDIT_REPO._events[0]["actor_id"] = "someone-else"

    before = [dict(e) for e in api.AUDIT_REPO._events]
    assert api.verify_audit_chain()["ok"] is False
    # Verifying twice must not mutate the log back into a valid state.
    assert api.verify_audit_chain()["ok"] is False
    assert [dict(e) for e in api.AUDIT_REPO._events] == before, "verification mutated the log"


def test_t_chain_05_activity_and_durability_are_reported_separately(clean_log):
    """W0-G's distinction, now that persistence exists.

    Previously this asserted `audit_chain_persisted is False` — true of the
    in-memory list and a characterisation of the gap, not of the requirement.
    The requirement is that the two properties are reported SEPARATELY and each
    reports the store actually in use.

    So the control is now stronger: durability is asserted to AGREE with the
    configured repository rather than to hold a fixed value. Pinning it to False
    would make the suite fail the moment the service was correctly configured for
    a durable store — and pinning it to True would let an in-memory deployment
    claim durability it does not have.
    """
    _emit("one")
    body = client.get("/api/governance/status").json()

    assert body["audit_chain_active"] is True
    assert body["audit_chain_verification"] == "VERIFIED"

    # The two fields are distinct, and durability tracks the store.
    assert body["audit_chain_persisted"] is api.AUDIT_REPO.durable
    if api.AUDIT_REPO.durable:
        assert "DURABLE" in body["audit_chain_durability"]
    else:
        assert "not durable" in body["audit_chain_durability"]

    # This suite runs in memory mode, so the gap is still what is reported here.
    assert body["audit_chain_persisted"] is False

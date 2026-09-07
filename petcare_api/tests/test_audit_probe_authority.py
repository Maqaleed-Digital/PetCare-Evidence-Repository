"""Tenant-sweep finding — the unauthenticated UI probe confers no authority.

`POST /audit/ui` accepts telemetry from a surface that may have no session yet,
so it cannot be gated. It previously took `tenant_id: Optional[str] = "platform"`
from the request body — the same defect W0-C removed from the tenant header,
where an omitted value silently granted the platform scope.

This matters more since W0-G. Every audit write is now chained, so an event
forged through this endpoint is correctly hashed and the chain verifies as
VERIFIED. The integrity proof would lend the forgery its own credibility. A
tamper-evident log is only as trustworthy as the authority of what enters it.

These are ARMED negative controls: each asserts that a specific assertion by an
unauthenticated caller is NOT honoured.
"""
import pytest
from fastapi.testclient import TestClient

import main as api

client = TestClient(api.app)


def _probe(**overrides) -> dict:
    body = {
        "event_name": "ui.surface.viewed",
        "actor_role": "platform_admin",
        "surface": "/owner",
        "correlation_id": "c-1",
    }
    body.update(overrides)
    r = client.post("/audit/ui", json=body)
    assert r.status_code == 200, r.text
    event_id = r.json()["audit_event_id"]
    return next(e for e in api._audit_log if e["audit_event_id"] == event_id)


def test_probe_is_still_accepted_without_a_session():
    """The endpoint must stay usable pre-authentication — otherwise the fix has
    simply broken the telemetry it was protecting."""
    rec = _probe()
    assert rec["event_name"] == "ui.surface.viewed"
    assert rec["reason_code"] == "UNAUTHENTICATED_UI_PROBE"


def test_caller_cannot_assert_a_tenant():
    """ARMED — the body may not choose the tenant, under any key.

    An unauthenticated caller naming a tenant must not have it honoured; the
    record is UNATTRIBUTED because no verified identity backs it.
    """
    rec = _probe(tenant_id="platform")
    assert rec["tenant_id"] == api.UNATTRIBUTED_TENANT, (
        "an unauthenticated caller filed an audit event under a tenant it named"
    )

    rec = _probe(tenant_id="some-other-clinic")
    assert rec["tenant_id"] == api.UNATTRIBUTED_TENANT


def test_unattributed_is_not_a_real_scope():
    """The sentinel must not collide with a tenant anyone could legitimately
    hold — otherwise it re-creates the defect under a new name."""
    assert api.UNATTRIBUTED_TENANT != "platform"
    assert api.UNATTRIBUTED_TENANT.isupper()


def test_caller_cannot_assert_a_role_that_matches_a_real_one():
    """ARMED — a claimed role is recorded, but structurally cannot authorize.

    The prefix is what makes this safe: no member of VALID_ROLES carries it, so
    no authorization check can match a value that entered here.
    """
    rec = _probe(actor_role="platform_admin")
    assert rec["actor_role"].startswith(api.CLIENT_ASSERTED_PREFIX)
    assert rec["actor_role"] not in api.VALID_ROLES
    for role in api.VALID_ROLES:
        assert rec["actor_role"] != role


def test_caller_cannot_assert_an_authenticated_actor_id():
    rec = _probe(actor_id="admin-1")
    assert rec["actor_role"].startswith(api.CLIENT_ASSERTED_PREFIX)
    assert rec["actor_id"] == f"{api.CLIENT_ASSERTED_PREFIX}admin-1"


def test_probe_events_still_chain_and_verify():
    """The hardening must not break W0-G: probe events are real audit events and
    must link into the chain like any other."""
    _probe()
    _probe()
    result = api.verify_audit_chain()
    assert result["ok"] is True, result

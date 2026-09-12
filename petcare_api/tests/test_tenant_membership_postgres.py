"""The governed tenant-assignment control path, proven.

Sponsor ruling of 12 September 2026, item 3. Each control below maps to one of
the twelve proof points the ruling authorises, and every one runs against real
PostgreSQL with the adapter installed into the live serving path.
"""
import os
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

psycopg = pytest.importorskip("psycopg")

import main as api  # noqa: E402
import routers.auth as auth  # noqa: E402
from persistence import MODE_POSTGRES, PERSISTENCE_MODE_ENV_VAR, build_persistence  # noqa: E402
from roles import ROLE_OWNER, ROLE_PLATFORM_ADMIN, ROLE_VETERINARIAN  # noqa: E402
from secret_provider import SECRET_MODE_ENV_VAR  # noqa: E402
from tenant_membership import (  # noqa: E402
    EVENT_MEMBERSHIP_ADDED,
    EVENT_MEMBERSHIP_REMOVED,
    RESOURCE_TYPE_MEMBERSHIP,
    TenantMembershipService,
)
from tenants import Tenant  # noqa: E402

client = TestClient(api.app, base_url="https://testserver")

T_A, T_B, T_DISABLED = "t-alpha", "t-beta", "t-disabled"
ADMIN = "admin@test.invalid"
TARGET = "target@test.invalid"
HDRS = {"X-Correlation-Id": "c-mem"}


@pytest.fixture()
def pg(clean_postgres):
    env = {SECRET_MODE_ENV_VAR: "environment",
           PERSISTENCE_MODE_ENV_VAR: MODE_POSTGRES}
    persistence = build_persistence(env, connection_url=clean_postgres)
    saved = (auth.PERSISTENCE, auth.SESSION_STORE, auth.IDENTITY_REPO,
             auth.INVITE_REPO, api.AUDIT_REPO, api.TENANT_MEMBERSHIP)
    auth.PERSISTENCE = persistence
    auth.SESSION_STORE = persistence.session_store
    auth.IDENTITY_REPO = persistence.identities
    auth.INVITE_REPO = persistence.invites
    api.AUDIT_REPO = persistence.audit
    api.TENANT_MEMBERSHIP = TenantMembershipService(persistence)

    for tid in (T_A, T_B):
        persistence.tenants.create(Tenant(tenant_id=tid, display_name=f"Fixture {tid}"))
    persistence.tenants.create(Tenant(tenant_id=T_DISABLED, display_name="Disabled"))
    persistence.tenants.disable(T_DISABLED)

    client.cookies.clear()
    try:
        yield persistence, clean_postgres
    finally:
        client.cookies.clear()
        (auth.PERSISTENCE, auth.SESSION_STORE, auth.IDENTITY_REPO,
         auth.INVITE_REPO, api.AUDIT_REPO, api.TENANT_MEMBERSHIP) = saved
        if persistence.pool is not None:
            persistence.pool.close()


def _signed_in(email: str, role: str, tenant):
    auth.seed_user("u-" + email, email, "pw", role, tenant_id=tenant)
    r = client.post("/api/auth/sign-in", json={"email": email, "password": "pw"})
    assert r.status_code == 200, r.text
    return r.cookies["petcare_session"]


def _as_admin(tenant=T_A):
    client.cookies.set("petcare_session", _signed_in(ADMIN, ROLE_PLATFORM_ADMIN, tenant))


def _target(tenant=None, role=ROLE_OWNER) -> str:
    auth.seed_user("u-" + TARGET, TARGET, "pw", role, tenant_id=tenant)
    return "u-" + TARGET


def _post(user_id: str, tenant_id, reason="governed test change"):
    return client.post(f"/api/admin/identities/{user_id}/tenant",
                       json={"tenant_id": tenant_id, "reason": reason},
                       headers=HDRS)


def _events(url: str, tenant: str) -> list:
    with psycopg.connect(url) as conn:
        return conn.execute(
            "SELECT event_name, resource_id, actor_id, actor_role, reason_code_nullable "
            "FROM audit_event WHERE tenant_id = %s AND resource_type = %s "
            "ORDER BY chain_seq", (tenant, RESOURCE_TYPE_MEMBERSHIP),
        ).fetchall()


# --- 6 · first assignment and revocation semantics -------------------------

def test_a_first_assignment_writes_the_addition_event_only(pg):
    p, url = pg
    _as_admin(); uid = _target(tenant=None)
    r = _post(uid, T_B)
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["previous_tenant_id"] is None
    assert body["tenant_id"] == T_B
    assert body["removal_event_id"] is None
    assert body["addition_event_id"]

    assert [e[0] for e in _events(url, T_B)] == [EVENT_MEMBERSHIP_ADDED]
    assert _events(url, T_A) == []
    assert p.identities.get_by_user_id(uid).tenant_id == T_B


def test_a_revocation_writes_the_removal_event_only(pg):
    p, url = pg
    _as_admin(); uid = _target(tenant=T_A)
    r = _post(uid, None, reason="offboarded")
    assert r.status_code == 200, r.text
    assert r.json()["revoked"] is True
    assert r.json()["tenant_id"] is None
    assert r.json()["addition_event_id"] is None

    assert [e[0] for e in _events(url, T_A)] == [EVENT_MEMBERSHIP_REMOVED]
    assert p.identities.get_by_user_id(uid).tenant_id is None


# --- 5 · old-tenant and new-tenant audit visibility, INDEPENDENTLY ---------

def test_a_reassignment_is_visible_in_each_tenants_own_audit_history(pg):
    """The two-event model, and the reason it was ruled.

    `query_events_for_tenant` filters on a single `tenant_id`. A single event
    would leave the tenant an identity LEFT with no record that it left.
    """
    p, url = pg
    _as_admin(); uid = _target(tenant=T_A)
    r = _post(uid, T_B, reason="transferred")
    assert r.status_code == 200, r.text
    assert r.json()["previous_tenant_id"] == T_A
    assert r.json()["tenant_id"] == T_B

    left = _events(url, T_A)
    joined = _events(url, T_B)
    assert [e[0] for e in left] == [EVENT_MEMBERSHIP_REMOVED], (
        "the tenant that was LEFT has no record of the departure"
    )
    assert [e[0] for e in joined] == [EVENT_MEMBERSHIP_ADDED]
    for row in left + joined:
        assert row[1] == uid                       # target identity
        assert row[2] == "u-" + ADMIN              # actor, from the session
        assert row[3] == ROLE_PLATFORM_ADMIN
        assert row[4] == "transferred"             # the human reason


def test_the_tenant_scoped_read_shows_each_tenant_only_its_own_event(pg):
    """Through the governed read surface, not by querying the table."""
    p, _ = pg
    _as_admin(); uid = _target(tenant=T_A)
    assert _post(uid, T_B).status_code == 200

    a = [e["event_name"] for e in p.audit.query_events_for_tenant(T_A, limit=50)
         if e["resource_type"] == RESOURCE_TYPE_MEMBERSHIP]
    b = [e["event_name"] for e in p.audit.query_events_for_tenant(T_B, limit=50)
         if e["resource_type"] == RESOURCE_TYPE_MEMBERSHIP]
    assert a == [EVENT_MEMBERSHIP_REMOVED]
    assert b == [EVENT_MEMBERSHIP_ADDED]


def test_no_previous_tenant_field_was_added_to_the_governed_record(pg):
    """The ruling forbids widening the field set for this requirement."""
    from audit_repository import GOVERNED_EVENT_FIELDS

    assert "previous_tenant_id" not in GOVERNED_EVENT_FIELDS
    assert len(GOVERNED_EVENT_FIELDS) == 12


def test_the_reason_field_carries_no_encoded_tenant_transition(pg):
    """Forbidden explicitly: structured old→new state hidden in an unvalidated
    field as a substitute for governed representation."""
    p, url = pg
    _as_admin(); uid = _target(tenant=T_A)
    _post(uid, T_B, reason="transferred")
    for row in _events(url, T_A) + _events(url, T_B):
        reason = row[4] or ""
        assert T_B not in reason and T_A not in reason, (
            f"the tenant transition was encoded into reason_code: {reason!r}"
        )


# --- 7 · cross-tenant administration ---------------------------------------

def test_a_platform_admin_administers_membership_across_tenants(pg):
    """The admin's own tenant is A; it moves an identity into B."""
    p, _ = pg
    _as_admin(tenant=T_A)
    uid = _target(tenant=T_A)
    assert _post(uid, T_B).status_code == 200
    assert p.identities.get_by_user_id(uid).tenant_id == T_B


def test_a_tenantless_platform_admin_can_still_administer(pg):
    p, _ = pg
    _as_admin(tenant=None)
    uid = _target(tenant=T_A)
    assert _post(uid, T_B).status_code == 200


# --- 8 · unauthorized actors ----------------------------------------------

@pytest.mark.parametrize("role", [ROLE_OWNER, ROLE_VETERINARIAN])
def test_a_non_admin_cannot_change_membership(pg, role):
    p, _ = pg
    uid = _target(tenant=T_A)
    client.cookies.set("petcare_session",
                       _signed_in(f"nonadmin-{role}@test.invalid", role, T_A))
    r = _post(uid, T_B)
    assert r.status_code == 403
    assert p.identities.get_by_user_id(uid).tenant_id == T_A


def test_an_unauthenticated_caller_cannot_change_membership(pg):
    p, _ = pg
    uid = _target(tenant=T_A)
    client.cookies.clear()
    assert _post(uid, T_B).status_code == 401
    assert p.identities.get_by_user_id(uid).tenant_id == T_A


def test_a_header_cannot_assert_the_admin_role(pg):
    """W0-B: authority comes from the session, never a header."""
    p, _ = pg
    uid = _target(tenant=T_A)
    client.cookies.set("petcare_session",
                       _signed_in("hdr@test.invalid", ROLE_OWNER, T_A))
    r = client.post(f"/api/admin/identities/{uid}/tenant",
                    json={"tenant_id": T_B, "reason": "x"},
                    headers={**HDRS, "X-Petcare-Role": ROLE_PLATFORM_ADMIN})
    assert r.status_code == 403
    assert p.identities.get_by_user_id(uid).tenant_id == T_A


def test_a_denied_attempt_writes_no_membership_audit_event(pg):
    p, url = pg
    uid = _target(tenant=T_A)
    client.cookies.set("petcare_session",
                       _signed_in("nobody@test.invalid", ROLE_OWNER, T_A))
    _post(uid, T_B)
    assert _events(url, T_A) == [] and _events(url, T_B) == []


# --- 9 · unknown and disabled tenants fail closed --------------------------

def test_an_unknown_tenant_fails_closed(pg):
    p, url = pg
    _as_admin(); uid = _target(tenant=T_A)
    r = _post(uid, "t-never-registered")
    assert r.status_code == 400
    assert r.json()["detail"]["error"] == "MEMBERSHIP_CHANGE_DENIED"
    assert p.identities.get_by_user_id(uid).tenant_id == T_A
    assert _events(url, T_A) == [], "a refused change wrote an audit event"


def test_a_disabled_tenant_fails_closed(pg):
    """The rule a foreign key cannot express: the row exists, so the constraint
    is satisfied and only the registry knows better."""
    p, url = pg
    _as_admin(); uid = _target(tenant=T_A)
    r = _post(uid, T_DISABLED)
    assert r.status_code == 400
    assert p.identities.get_by_user_id(uid).tenant_id == T_A
    assert _events(url, T_A) == []


def test_an_unknown_and_a_disabled_tenant_are_one_answer(pg):
    """Distinguishing them tells a caller which tenant ids exist.

    Compared with the tenant identifier elided: the message names the id the
    caller supplied, which tells them nothing they did not already know. What
    must not differ is everything else.
    """
    _as_admin(); uid = _target(tenant=T_A)
    unknown = _post(uid, "t-never-registered").json()["detail"]["reason"]
    disabled = _post(uid, T_DISABLED).json()["detail"]["reason"]
    assert unknown.replace("t-never-registered", "<id>") == \
        disabled.replace(T_DISABLED, "<id>"), (
            f"the refusal distinguishes unknown from disabled:\n"
            f"  {unknown}\n  {disabled}"
        )


def test_an_unknown_identity_is_refused(pg):
    _as_admin()
    assert _post("u-does-not-exist", T_B).status_code == 400


def test_a_change_that_is_not_a_change_is_refused(pg):
    """Writing a removal and an addition for the same tenant would record a
    membership change in both histories that never happened."""
    p, url = pg
    _as_admin(); uid = _target(tenant=T_A)
    assert _post(uid, T_A).status_code == 400
    assert _events(url, T_A) == []


def test_a_missing_reason_is_refused(pg):
    p, url = pg
    _as_admin(); uid = _target(tenant=T_A)
    assert _post(uid, T_B, reason="   ").status_code == 400
    assert _events(url, T_B) == []


# --- 2 · the API accepts no role parameter ---------------------------------

def test_the_request_model_has_no_role_field(pg):
    """Implemented as an ABSENCE. A field that does not exist cannot be
    supplied, and `extra=forbid` means it cannot be smuggled either."""
    fields = set(api.TenantMembershipRequest.model_fields)
    assert fields == {"tenant_id", "reason"}
    assert not any("role" in f for f in fields)


@pytest.mark.parametrize("smuggled", ["role", "actor_role", "new_role", "target_role"])
def test_a_role_field_in_the_body_is_rejected_outright(pg, smuggled):
    p, _ = pg
    _as_admin(); uid = _target(tenant=T_A, role=ROLE_OWNER)
    r = client.post(f"/api/admin/identities/{uid}/tenant",
                    json={"tenant_id": T_B, "reason": "x",
                          smuggled: ROLE_PLATFORM_ADMIN},
                    headers=HDRS)
    assert r.status_code == 422, f"{smuggled!r} was accepted by the model"
    assert p.identities.get_by_user_id(uid).role == ROLE_OWNER


def test_the_service_signature_takes_no_target_role(pg):
    """Structural: the service itself must not grow one either."""
    import inspect

    params = set(inspect.signature(TenantMembershipService.set_membership).parameters)
    assert "role" not in params
    assert params & {"target_role", "new_role"} == set()
    # `actor_role` describes the CALLER and is written only into the audit
    # record's actor field — never applied to the target.
    assert "actor_role" in params


# --- 11 · a tenant change does not alter role authority --------------------

@pytest.mark.parametrize("role", [ROLE_OWNER, ROLE_VETERINARIAN, ROLE_PLATFORM_ADMIN])
def test_a_membership_change_leaves_the_role_untouched(pg, role):
    p, _ = pg
    _as_admin(); uid = _target(tenant=T_A, role=role)
    assert _post(uid, T_B).status_code == 200
    assert p.identities.get_by_user_id(uid).role == role


def test_a_membership_change_cannot_grant_platform_admin(pg):
    """The escalation path the ruling separates the authorities to prevent."""
    p, _ = pg
    _as_admin(); uid = _target(tenant=T_A, role=ROLE_OWNER)
    assert _post(uid, T_B).status_code == 200
    assert p.identities.get_by_user_id(uid).role == ROLE_OWNER != ROLE_PLATFORM_ADMIN


def test_the_target_route_authority_is_unchanged_after_a_move(pg):
    """Behavioural, not just a stored value: the identity's access is the same
    before and after, because roles are not tenant-scoped."""
    p, _ = pg
    uid = _target(tenant=T_A, role=ROLE_OWNER)
    cookie = client.post("/api/auth/sign-in",
                         json={"email": TARGET, "password": "pw"}).cookies["petcare_session"]
    client.cookies.set("petcare_session", cookie)
    before = client.get("/audit/events").status_code   # owner: forbidden

    _as_admin()
    assert _post(uid, T_B).status_code == 200

    client.cookies.set("petcare_session", cookie)
    after = client.get("/audit/events").status_code
    assert before == after == 403


# --- 10 · direct repository mutation is not an authorized serving path -----

def test_no_route_other_than_the_governed_one_writes_tenant_membership(pg):
    """Structural. The governed path is the only serving code that changes an
    identity's tenant."""
    import ast

    src = Path(api.__file__).read_text(encoding="utf-8")
    tree = ast.parse(src)
    offenders = []
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        if node.name in {"set_tenant_membership", "read_tenant_membership"}:
            continue
        body = ast.get_source_segment(src, node) or ""
        # WRITES to the identity store, not reads into a local. `tenant_id = ...`
        # is how several routes bind the caller's own scope from the session, and
        # matching it flagged two routes that only read — a matcher that cannot
        # tell a read from a write would be widened until it meant nothing.
        writes = (
            "IDENTITY_REPO.upsert",
            "IDENTITY_REPO.create",
            "identities.upsert",
            "identities.create",
            "UPDATE user_identity",
        )
        if any(w in body for w in writes):
            offenders.append(node.name)
    assert offenders == [], f"routes writing tenant membership outside the path: {offenders}"


def test_a_direct_repository_write_produces_no_audit_event(pg):
    """Why direct access is not authorized, demonstrated rather than asserted.

    The repository still works — it is the boundary the governed service uses.
    What it does not do is produce a record, which is exactly why the ruling puts
    a service in front of it.
    """
    from dataclasses import replace

    p, url = pg
    uid = _target(tenant=T_A)
    identity = p.identities.get_by_user_id(uid)
    p.identities.upsert(replace(identity, tenant_id=T_B))

    assert p.identities.get_by_user_id(uid).tenant_id == T_B
    assert _events(url, T_A) == [] and _events(url, T_B) == [], (
        "a direct repository write produced an audit event; it must not, and "
        "that absence is why it is not an authorized operating path"
    )


# --- atomicity, chain integrity, readback ---------------------------------

def test_the_audit_chain_still_verifies_after_membership_changes(pg):
    p, _ = pg
    _as_admin(); uid = _target(tenant=T_A)
    _post(uid, T_B, reason="one")
    _post(uid, T_A, reason="two")
    _post(uid, None, reason="three")
    assert p.audit.verify_chain()["ok"] is True


def test_the_two_events_of_one_change_are_consecutive_in_the_chain(pg):
    """One transaction holds the head lock, so nothing interleaves between the
    removal and the addition of a single change."""
    p, url = pg
    _as_admin(); uid = _target(tenant=T_A)
    _post(uid, T_B)
    with psycopg.connect(url) as conn:
        rows = conn.execute(
            "SELECT event_name, chain_seq FROM audit_event "
            "WHERE resource_type = %s ORDER BY chain_seq",
            (RESOURCE_TYPE_MEMBERSHIP,),
        ).fetchall()
    assert [r[0] for r in rows] == [EVENT_MEMBERSHIP_REMOVED, EVENT_MEMBERSHIP_ADDED]
    assert rows[1][1] == rows[0][1] + 1


def test_a_failure_leaves_neither_the_identity_nor_the_log_changed(pg, monkeypatch):
    """Atomicity, armed. The identity update is made to fail after both audit
    events have been written; the transaction must roll back both."""
    p, url = pg
    _as_admin(); uid = _target(tenant=T_A)
    before_chain = p.audit.count()

    real = api.TENANT_MEMBERSHIP._apply

    def _boom(conn, **kw):
        real(conn, **kw)
        raise RuntimeError("induced failure after the writes")

    monkeypatch.setattr(api.TENANT_MEMBERSHIP, "_apply", _boom)
    r = _post(uid, T_B)
    assert r.status_code == 400

    assert p.identities.get_by_user_id(uid).tenant_id == T_A, "the identity moved"
    assert p.audit.count() == before_chain, "audit rows survived the rollback"
    assert _events(url, T_A) == [] and _events(url, T_B) == []
    assert p.audit.verify_chain()["ok"] is True


def test_the_readback_path_reports_membership_and_role(pg):
    p, _ = pg
    _as_admin(); uid = _target(tenant=T_A, role=ROLE_VETERINARIAN)
    r = client.get(f"/api/admin/identities/{uid}/tenant")
    assert r.status_code == 200
    assert r.json() == {"user_id": uid, "tenant_id": T_A, "role": ROLE_VETERINARIAN}
    assert _post(uid, T_B).status_code == 200
    assert client.get(f"/api/admin/identities/{uid}/tenant").json()["tenant_id"] == T_B


def test_the_readback_path_is_admin_gated(pg):
    p, _ = pg
    uid = _target(tenant=T_A)
    client.cookies.set("petcare_session",
                       _signed_in("ro@test.invalid", ROLE_OWNER, T_A))
    assert client.get(f"/api/admin/identities/{uid}/tenant").status_code == 403


# --- the non-durable refusal (memory mode, no pg fixture) ------------------

def test_the_governed_path_refuses_to_operate_on_a_non_durable_store():
    """A membership change that died with the process would be a governed act
    with no record — the condition this path exists to end.

    Deliberately without the `pg` fixture, so `api.TENANT_MEMBERSHIP` is the one
    built at import over the in-memory persistence.
    """
    from tenant_membership import TenantMembershipUnavailable

    service = TenantMembershipService(auth.PERSISTENCE)
    assert auth.PERSISTENCE.is_durable is False
    with pytest.raises(TenantMembershipUnavailable):
        service.set_membership(
            target_user_id="u-anyone", tenant_id="t-anything",
            actor_id="u-admin", actor_role=ROLE_PLATFORM_ADMIN,
            reason="x", correlation_id="c",
        )


def test_authorization_is_checked_before_durability():
    """A non-admin gets 403 even on a deployment that could not perform the
    change anyway — so the refusal never leaks the store's configuration to an
    unauthorised caller."""
    auth.seed_user("u-mem-owner", "mem-owner@test.invalid", "pw", ROLE_OWNER,
                   tenant_id=None)
    r = client.post("/api/auth/sign-in",
                    json={"email": "mem-owner@test.invalid", "password": "pw"})
    client.cookies.set("petcare_session", r.cookies["petcare_session"])
    denied = client.post("/api/admin/identities/u-anyone/tenant",
                         json={"tenant_id": "t-x", "reason": "x"}, headers=HDRS)
    client.cookies.clear()
    assert denied.status_code == 403

"""W0-F AC-7 — AC7-01..06, server-side session revocation.

The W0-F pack requires that introducing a session store be accompanied by an
explicit revocation path, "a decision, not a side effect". These are the armed
negative controls for that decision: each asserts a specific presentation is
DENIED.

AC7-06 is the one that gives the others their point. Before this store, the only
way to revoke a session was to rotate the signing key — which signs *everyone*
out. A revocation mechanism whose blast radius is the entire user base is one
nobody uses, so in practice sessions were not revocable at all.
"""
from datetime import datetime, timedelta, timezone

import pytest

from session_store import InMemorySessionStore, SessionDenied, SessionRecord
from tenants import InMemoryTenantRepository, Tenant

TENANT_A = "tenant-a"
TENANT_B = "tenant-b"
TTL = 8 * 60 * 60


@pytest.fixture
def store():
    # The store is given a registry holding the tenants these controls use.
    # Migration 0034 makes a tenant a governed object, and the in-memory store
    # performs the same refusal the foreign key does — so a fixture that skipped
    # it would be testing a weaker store than the one that ships.
    tenants = InMemoryTenantRepository()
    for tid in ("t1", "t2", "tenant-a", "tenant-b"):
        tenants.create(Tenant(tenant_id=tid, display_name=f"Fixture {tid}"))
    return InMemorySessionStore(tenants)


def _mk(store, user="u1", tenant=TENANT_A, role="veterinarian"):
    return store.create(user_id=user, tenant_id=tenant, role=role, ttl_seconds=TTL)


def test_baseline_a_fresh_session_is_active(store):
    """Without this, every denial below could pass because nothing ever works."""
    s = _mk(store)
    got = store.get_active(s.session_id, tenant_id=TENANT_A)
    assert got is not None and got.session_id == s.session_id


def test_ac7_01_revoked_session_is_denied(store):
    """AC7-01 (ARMED) — the core promise. A revoked session must not be honoured
    even though its cookie is still validly signed and unexpired."""
    s = _mk(store)
    assert store.revoke(s.session_id, tenant_id=TENANT_A) is True
    assert store.get_active(s.session_id, tenant_id=TENANT_A) is None


def test_ac7_02_session_from_tenant_a_is_denied_in_tenant_b(store):
    """AC7-02 (ARMED) — tenant isolation. A real, active, correctly signed
    session presented against the wrong tenant is refused."""
    s = _mk(store, tenant=TENANT_A)
    assert store.get_active(s.session_id, tenant_id=TENANT_A) is not None
    assert store.get_active(s.session_id, tenant_id=TENANT_B) is None


def test_ac7_02b_cross_tenant_revocation_is_refused(store):
    """Revoking is as privileged as reading. A caller in tenant B must not be
    able to revoke a session belonging to tenant A — denial of service across a
    tenant boundary is still a cross-tenant action."""
    s = _mk(store, tenant=TENANT_A)
    assert store.revoke(s.session_id, tenant_id=TENANT_B) is False
    assert store.get_active(s.session_id, tenant_id=TENANT_A) is not None, (
        "a cross-tenant revoke attempt affected the session anyway"
    )


def test_ac7_03_expired_session_is_denied_server_side(store):
    """AC7-03 (ARMED) — expiry is enforced by the server, not by the cookie.

    Constructed directly with a past expiry: a client that replays an old cookie
    must not be believed just because the signature still verifies.
    """
    past = datetime.now(timezone.utc) - timedelta(hours=1)
    expired = SessionRecord(
        session_id="expired-sid",
        user_id="u1",
        tenant_id=TENANT_A,
        role="veterinarian",
        issued_at=past - timedelta(hours=8),
        expires_at=past,
    )
    store._sessions[expired.session_id] = expired
    assert store.get_active("expired-sid", tenant_id=TENANT_A) is None


def test_ac7_04_unknown_session_id_is_denied(store):
    """AC7-04 (ARMED) — an id the store never issued is refused.

    This is what a forged or replayed-after-purge cookie looks like.
    """
    assert store.get_active("never-issued", tenant_id=TENANT_A) is None
    assert store.revoke("never-issued", tenant_id=TENANT_A) is False


def test_ac7_05_revoking_one_user_leaves_another_user_active(store):
    """AC7-05 (ARMED) — blast radius.

    The failure this prevents is a revocation that quietly signs out more people
    than intended, which is precisely what key rotation does.
    """
    alice_1 = _mk(store, user="alice")
    alice_2 = _mk(store, user="alice")
    bob = _mk(store, user="bob")

    revoked = store.revoke_all_for_user("alice", tenant_id=TENANT_A)
    assert revoked == 2

    assert store.get_active(alice_1.session_id, tenant_id=TENANT_A) is None
    assert store.get_active(alice_2.session_id, tenant_id=TENANT_A) is None
    assert store.get_active(bob.session_id, tenant_id=TENANT_A) is not None, (
        "revoking alice's sessions also revoked bob's"
    )


def test_ac7_05b_revoke_all_for_user_does_not_cross_tenants(store):
    """The same user id in two tenants is two subjects. Revoking one must not
    reach the other."""
    a = store.create(user_id="u1", tenant_id=TENANT_A, role="veterinarian", ttl_seconds=TTL)
    b = store.create(user_id="u1", tenant_id=TENANT_B, role="veterinarian", ttl_seconds=TTL)

    assert store.revoke_all_for_user("u1", tenant_id=TENANT_A) == 1
    assert store.get_active(a.session_id, tenant_id=TENANT_A) is None
    assert store.get_active(b.session_id, tenant_id=TENANT_B) is not None


def test_ac7_06_revocation_requires_no_key_rotation(store):
    """AC7-06 — the decision AC-7 exists to record.

    Individual and per-user revocation are properties of the STORE. Nothing here
    reads, writes or depends on the signing key, so revoking a session cannot
    require rotating it. Key rotation remains available as an emergency
    system-wide capability; it is no longer the ordinary revocation mechanism.
    """
    import inspect

    import session_store

    source = inspect.getsource(session_store)
    for forbidden in ("SECRET_KEY", "_serializer", "URLSafeTimedSerializer", "itsdangerous"):
        assert forbidden not in source, (
            f"the session store references {forbidden} — revocation must not depend "
            "on the signing key, or per-user revocation becomes global sign-out"
        )

    s = _mk(store)
    assert store.revoke(s.session_id, tenant_id=TENANT_A) is True
    assert store.get_active(s.session_id, tenant_id=TENANT_A) is None


def test_session_cannot_be_created_without_a_tenant(store):
    """W0-C. A session with no tenant could not be scoped by any later check, so
    it is refused at creation rather than becoming an unscoped session later."""
    with pytest.raises(SessionDenied):
        store.create(user_id="u1", tenant_id="", role="veterinarian", ttl_seconds=TTL)


def test_revoking_twice_is_not_an_error_and_does_not_move_the_timestamp(store):
    """Revocation is idempotent in effect. The second call reports that nothing
    changed, and must not overwrite when the session was actually revoked —
    that timestamp is the record of the act."""
    s = _mk(store)
    assert store.revoke(s.session_id, tenant_id=TENANT_A) is True
    first = store._sessions[s.session_id].revoked_at
    assert store.revoke(s.session_id, tenant_id=TENANT_A) is False
    assert store._sessions[s.session_id].revoked_at == first


def test_tenant_id_has_no_default_on_any_store_lookup():
    """The W0-I finding, applied here before it can recur.

    A permissive default is invisible at every call site that passes the
    argument — which is all of them, until the one that does not.
    """
    import inspect

    for fn in (
        InMemorySessionStore.get_active,
        InMemorySessionStore.revoke,
        InMemorySessionStore.revoke_all_for_user,
        InMemorySessionStore.create,
    ):
        param = inspect.signature(fn).parameters.get("tenant_id")
        assert param is not None, f"{fn.__name__} lost its tenant parameter"
        assert param.default is inspect.Parameter.empty, (
            f"{fn.__name__}(tenant_id=...) has a default — a caller that omits it "
            "gets an unscoped session operation"
        )

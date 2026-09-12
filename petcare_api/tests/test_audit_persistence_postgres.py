"""AUD-01..12 — the audit chain, persisted, proven against real PostgreSQL.

W0-G made tampering detectable over a list that died with the process. Its own
receipt records the one target it could not deliver:

```
| chain **persisted**  | NO — requires W0-F, Sponsor-gated |
```

These controls prove that row closed, and prove it without loosening anything
W0-G established. The security posture is preserved rather than reopened: an
unauthenticated caller still cannot choose what a record says about identity, and
persistence must not lend a forged event the credibility of a verified chain —
which is AUD-09, and is the reason a chain alone was never sufficient.

Every control runs against PostgreSQL with the adapter installed into the live
serving module, so a regression that quietly disconnected the writer would fail
here even though every in-memory chain control still passed.
"""
import os
import sys

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

psycopg = pytest.importorskip("psycopg")

import main as api  # noqa: E402
import routers.auth as auth
from tenant_fixtures import ensure_tenant  # noqa: E402
from audit_repository import AuditWriteFailed, PostgresAuditRepository  # noqa: E402
from persistence import MODE_POSTGRES, PERSISTENCE_MODE_ENV_VAR, build_persistence  # noqa: E402
from postgres_repositories import PersistenceUnavailable  # noqa: E402
from secret_provider import SECRET_MODE_ENV_VAR  # noqa: E402

client = TestClient(api.app)

PROTECTED = "/api/appointments"
BODY = {"pet_id": "p1", "owner_id": "o1", "clinic_id": "c1", "tenant_id": "t1"}
HDRS = {"X-Correlation-Id": "c-1", "X-Actor-Id": "a-1"}


@pytest.fixture()
def postgres_audit(clean_postgres):
    """Install the PostgreSQL adapter into the live serving path.

    Both `auth.PERSISTENCE` and `main.AUDIT_REPO` are replaced, because the
    serving path reads the audit repository from `main` and identity/sessions
    from `auth`. Swapping one and not the other would leave the suite proving a
    half-wired service.
    """
    env = {SECRET_MODE_ENV_VAR: "environment",
           PERSISTENCE_MODE_ENV_VAR: MODE_POSTGRES}
    persistence = build_persistence(env, connection_url=clean_postgres)
    assert isinstance(persistence.audit, PostgresAuditRepository)

    saved_auth = (auth.PERSISTENCE, auth.SESSION_STORE, auth.IDENTITY_REPO,
                  auth.INVITE_REPO)
    saved_audit = api.AUDIT_REPO
    auth.PERSISTENCE = persistence
    auth.SESSION_STORE = persistence.session_store
    auth.IDENTITY_REPO = persistence.identities
    auth.INVITE_REPO = persistence.invites
    api.AUDIT_REPO = persistence.audit
    client.cookies.clear()
    try:
        yield persistence
    finally:
        client.cookies.clear()
        (auth.PERSISTENCE, auth.SESSION_STORE, auth.IDENTITY_REPO,
         auth.INVITE_REPO) = saved_auth
        api.AUDIT_REPO = saved_audit
        if persistence.pool is not None:
            persistence.pool.close()


def _sign_in(email: str, role: str = api.ROLE_OWNER, tenant: str | None = "t1") -> str:
    ensure_tenant(tenant)
    auth.seed_user("u-" + email, email, "pw", role, tenant_id=tenant)
    r = client.post("/api/auth/sign-in", json={"email": email, "password": "pw"})
    assert r.status_code == 200, r.text
    return r.cookies["petcare_session"]


def _rows(url: str) -> list:
    with psycopg.connect(url) as conn:
        return conn.execute(
            "SELECT audit_event_id, tenant_id, actor_id, actor_role, chain_seq, "
            "       prev_hash, event_hash FROM audit_event "
            "WHERE chain_seq IS NOT NULL ORDER BY chain_seq"
        ).fetchall()


# ---------------------------------------------------------------------------
# AUD-10 / AUD-11 — the governed path actually reaches PostgreSQL
# ---------------------------------------------------------------------------

def test_aud_10_a_real_governed_route_writes_an_audit_row_to_postgres(postgres_audit):
    """RULE 16. A repository that exists but is never reached delivers nothing.

    Driven through the real sign-in and the real protected route — nothing here
    calls `_audit` directly.
    """
    url = postgres_audit.pool.conninfo
    assert _rows(url) == []

    cookie = _sign_in("aud10@t")
    client.cookies.set("petcare_session", cookie)
    r = client.post(PROTECTED, json=BODY, headers=HDRS)
    assert r.status_code in (200, 201), r.text

    rows = _rows(url)
    assert rows, "a governed route completed without writing an audit row"
    assert rows[-1][1] == "t1", "the row did not carry the server-established tenant"
    assert rows[-1][4] == len(rows), "chain_seq is not the row's position"


def test_aud_11_an_in_memory_repository_cannot_satisfy_aud_10(postgres_audit):
    """The vacuity guard for AUD-10.

    If the fixture silently failed to install the adapter, AUD-10 would pass
    against the in-memory list and prove exactly what W0-G already proved. This
    asserts the two are distinguishable, and that the durable one is installed.
    """
    from audit_repository import InMemoryAuditRepository

    assert isinstance(api.AUDIT_REPO, PostgresAuditRepository)
    assert api.AUDIT_REPO.durable is True
    assert InMemoryAuditRepository().durable is False

    url = postgres_audit.pool.conninfo
    in_memory = InMemoryAuditRepository()
    in_memory.append_event({
        "audit_event_id": "ghost", "event_name": "e", "actor_id": "a",
        "actor_role": "r", "tenant_id": "t1", "clinic_id": None,
        "resource_type": "rt", "resource_id": "ri", "action_result": "ok",
        "reason_code": None, "correlation_id": "c", "occurred_at": "2026-01-01",
    })
    assert in_memory.count() == 1
    assert all(r[0] != "ghost" for r in _rows(url)), (
        "an in-memory write reached the database"
    )


def test_the_status_endpoint_reports_durability_from_the_store(postgres_audit):
    """COMPUTED, never asserted. The fixed string this replaced would now be a
    false claim — the MVC-INC-ATTEST-001 defect inverted."""
    _sign_in("aud-status@t")
    body = client.get("/api/governance/status").json()
    assert body["audit_chain_persisted"] is True
    assert "DURABLE" in body["audit_chain_durability"]


# ---------------------------------------------------------------------------
# AUD-07 / AUD-08 — verification over persisted rows
# ---------------------------------------------------------------------------

def test_aud_07_a_legitimate_persisted_chain_verifies(postgres_audit):
    cookie = _sign_in("aud07@t")
    client.cookies.set("petcare_session", cookie)
    for _ in range(3):
        assert client.post(PROTECTED, json=BODY, headers=HDRS).status_code in (200, 201)

    result = api.AUDIT_REPO.verify_chain()
    assert result["ok"] is True, result
    assert result["events"] >= 3


def test_aud_08_modifying_a_persisted_row_breaks_verification(postgres_audit):
    """The tamper control, against the STORE rather than a list.

    A chain over a database that could not detect an `UPDATE` would be
    decorative — and an `UPDATE` is precisely the access a compromised
    application or a careless operator has.
    """
    cookie = _sign_in("aud08@t")
    client.cookies.set("petcare_session", cookie)
    for _ in range(3):
        client.post(PROTECTED, json=BODY, headers=HDRS)
    assert api.AUDIT_REPO.verify_chain()["ok"] is True

    url = postgres_audit.pool.conninfo
    with psycopg.connect(url, autocommit=True) as conn:
        changed = conn.execute(
            "UPDATE audit_event SET action_result = 'denied' WHERE chain_seq = 2"
        ).rowcount
    assert changed == 1, "the tamper did not land; the result below proves nothing"

    result = api.AUDIT_REPO.verify_chain()
    assert result["ok"] is False, "a modified stored row was not detected"
    assert result["reason"] == "hash_mismatch"
    assert result["index"] == 1


def test_removing_a_persisted_row_is_detected_as_a_gap(postgres_audit):
    cookie = _sign_in("aud-gap@t")
    client.cookies.set("petcare_session", cookie)
    for _ in range(3):
        client.post(PROTECTED, json=BODY, headers=HDRS)

    url = postgres_audit.pool.conninfo
    with psycopg.connect(url, autocommit=True) as conn:
        removed = conn.execute(
            "DELETE FROM audit_event WHERE chain_seq = 2"
        ).rowcount
    assert removed == 1, "the probe did not land; the result below proves nothing"

    result = api.AUDIT_REPO.verify_chain()
    assert result["ok"] is False, "a removed row was not detected"
    assert result["reason"] == "prev_hash_mismatch"


def test_verification_never_repairs_the_chain(postgres_audit):
    """W0-G's T-CHAIN-04, against the store. Silently rehashing a broken chain
    would destroy the only evidence that it broke."""
    cookie = _sign_in("aud-norepair@t")
    client.cookies.set("petcare_session", cookie)
    client.post(PROTECTED, json=BODY, headers=HDRS)

    url = postgres_audit.pool.conninfo
    with psycopg.connect(url, autocommit=True) as conn:
        conn.execute("UPDATE audit_event SET actor_id = 'someone-else' "
                     "WHERE chain_seq = 1")
    before = _rows(url)
    api.AUDIT_REPO.verify_chain()
    api.AUDIT_REPO.verify_chain()
    assert _rows(url) == before, "verification mutated the stored log"


# ---------------------------------------------------------------------------
# AUD-01..04, AUD-09 — authority cannot be client-supplied
# ---------------------------------------------------------------------------

def test_aud_01_an_unauthenticated_write_produces_no_authoritative_record(
    postgres_audit,
):
    """The probe endpoint is unauthenticated BY DESIGN and therefore
    unauthoritative. What it must not do is let the caller choose what the record
    says about identity — which is the property W0-G hardened and this preserves
    now that the record is durable."""
    url = postgres_audit.pool.conninfo
    client.cookies.clear()
    r = client.post("/audit/ui", json={
        "event_name": "ui.click", "surface": "s", "correlation_id": "c",
        "actor_id": "u-admin-001", "actor_role": "platform_admin",
        "tenant_id": "t1",
    })
    assert r.status_code == 200, r.text

    rows = _rows(url)
    assert len(rows) == 1
    _, tenant, actor, role, *_ = rows[0]
    assert tenant == api.UNATTRIBUTED_TENANT, "an unauthenticated caller set a tenant"
    assert actor.startswith(api.CLIENT_ASSERTED_PREFIX)
    assert role.startswith(api.CLIENT_ASSERTED_PREFIX)


def test_aud_02_a_client_supplied_tenant_cannot_override_the_session_tenant(
    postgres_audit,
):
    url = postgres_audit.pool.conninfo
    cookie = _sign_in("aud02@t", tenant="t1")
    client.cookies.set("petcare_session", cookie)
    r = client.post("/audit/ui", json={
        "event_name": "ui.click", "surface": "s", "correlation_id": "c",
        "actor_id": "x", "actor_role": "y", "tenant_id": "t2",
    })
    assert r.status_code == 200
    assert _rows(url)[-1][1] == "t1", "the caller's claimed tenant was stored"


def test_aud_03_a_client_supplied_actor_cannot_become_an_authenticated_actor(
    postgres_audit,
):
    url = postgres_audit.pool.conninfo
    client.cookies.clear()
    client.post("/audit/ui", json={
        "event_name": "e", "surface": "s", "correlation_id": "c",
        "actor_id": "u-admin-001", "actor_role": "r",
    })
    actor = _rows(url)[-1][2]
    assert actor != "u-admin-001"
    assert actor == f"{api.CLIENT_ASSERTED_PREFIX}u-admin-001"


def test_aud_04_a_client_supplied_role_can_never_match_a_real_role(postgres_audit):
    """Prefixed rather than rejected, so the claim is RECORDED and powerless. A
    stored role that matched VALID_ROLES would be indistinguishable from one the
    server established."""
    url = postgres_audit.pool.conninfo
    client.cookies.clear()
    for role in sorted(api.VALID_ROLES):
        client.post("/audit/ui", json={
            "event_name": "e", "surface": "s", "correlation_id": "c",
            "actor_id": "a", "actor_role": role,
        })
    stored = {r[3] for r in _rows(url)}
    assert stored, "no probe rows were written"
    assert not (stored & set(api.VALID_ROLES)), (
        "a client-asserted role was stored as a real role"
    )


def test_aud_09_a_forged_event_is_chained_but_never_authoritative(postgres_audit):
    """The limit of what a hash chain proves, asserted rather than assumed.

    An event filed through the unauthenticated probe is hashed and linked like
    any other, and the chain verifies — the integrity proof lends the forgery its
    own credibility. What prevents it being AUTHORITATIVE is that its identity
    fields are neutralised at the boundary, not that the chain rejected it.

    This is why W0-G's open ARCH-01 question — whether signatures or anchoring
    are required beyond a hash chain — is NOT closed by persistence.
    """
    url = postgres_audit.pool.conninfo
    client.cookies.clear()
    client.post("/audit/ui", json={
        "event_name": "privilege.grant", "surface": "s", "correlation_id": "c",
        "actor_id": "u-admin-001", "actor_role": "platform_admin",
        "tenant_id": "t1",
    })

    assert api.AUDIT_REPO.verify_chain()["ok"] is True, (
        "the forged event broke the chain — it should chain like any other"
    )
    _, tenant, actor, role, *_ = _rows(url)[-1]
    assert tenant == api.UNATTRIBUTED_TENANT
    assert role not in api.VALID_ROLES
    assert actor.startswith(api.CLIENT_ASSERTED_PREFIX)


# ---------------------------------------------------------------------------
# AUD-05 / AUD-06 — tenant authority on reads
# ---------------------------------------------------------------------------

def test_aud_05_a_tenantless_identity_cannot_read_tenant_scoped_audit(postgres_audit):
    """W0-C: an identity with no tenant assignment fails closed at the route with
    403 NO_TENANT_AUTHORITY, rather than being given a scope."""
    cookie = _sign_in("aud05@t", tenant=None)
    client.cookies.set("petcare_session", cookie)
    r = client.get("/audit/events/tenant")
    assert r.status_code == 403
    assert r.json()["detail"]["error"] == "NO_TENANT_AUTHORITY"


def test_aud_06_a_tenant_scoped_read_cannot_return_another_tenants_events(
    postgres_audit,
):
    a = _sign_in("aud06a@t", tenant="t1")
    client.cookies.set("petcare_session", a)
    client.post(PROTECTED, json=BODY, headers=HDRS)

    b = _sign_in("aud06b@t", tenant="t2")
    client.cookies.set("petcare_session", b)
    client.post(PROTECTED, json={**BODY, "tenant_id": "t2"}, headers=HDRS)

    r = client.get("/audit/events/tenant")
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["tenant_id"] == "t2"
    assert body["count"] >= 1
    assert all(e["tenant_id"] == "t2" for e in body["events"]), (
        "a tenant-scoped read returned another tenant's events"
    )


def test_aud_06b_a_query_parameter_cannot_choose_the_tenant(postgres_audit):
    """The scope comes from the session. A client-supplied one here would make
    the audit log a cross-tenant read for anyone who could name a tenant."""
    a = _sign_in("aud06c@t", tenant="t1")
    client.cookies.set("petcare_session", a)
    client.post(PROTECTED, json=BODY, headers=HDRS)

    r = client.get("/audit/events/tenant?tenant_id=t2")
    assert r.status_code == 200
    assert r.json()["tenant_id"] == "t1", "a query parameter selected the tenant"


def test_aud_06c_get_event_is_tenant_scoped_and_gives_no_oracle(postgres_audit):
    """Not found and not yours are ONE answer. Telling a caller that an id exists
    in another tenant is a small cross-tenant oracle."""
    cookie = _sign_in("aud06d@t", tenant="t1")
    client.cookies.set("petcare_session", cookie)
    client.post(PROTECTED, json=BODY, headers=HDRS)
    event_id = _rows(postgres_audit.pool.conninfo)[-1][0]

    assert api.AUDIT_REPO.get_event(event_id, tenant_id="t1") is not None
    assert api.AUDIT_REPO.get_event(event_id, tenant_id="t2") is None
    assert api.AUDIT_REPO.get_event("no-such-event", tenant_id="t1") is None


def test_the_whole_chain_route_is_admin_gated(postgres_audit):
    """Reading every tenant's events is privileged. An owner may not."""
    cookie = _sign_in("aud-nonadmin@t", role=api.ROLE_OWNER, tenant="t1")
    client.cookies.set("petcare_session", cookie)
    assert client.get("/audit/events").status_code == 403


# ---------------------------------------------------------------------------
# Durability and failure behaviour
# ---------------------------------------------------------------------------

def test_persisted_history_survives_a_new_repository(postgres_audit):
    """A restart, modelled honestly: a NEW repository over the same database.

    This is the property the in-memory list could never have, and the reason
    W0-G reported activity and durability separately.
    """
    cookie = _sign_in("aud-restart@t")
    client.cookies.set("petcare_session", cookie)
    client.post(PROTECTED, json=BODY, headers=HDRS)
    before = api.AUDIT_REPO.count()
    assert before >= 1

    fresh = PostgresAuditRepository(postgres_audit.pool)
    assert fresh.count() == before, "history did not survive a new repository"
    assert fresh.verify_chain()["ok"] is True


def test_the_chain_continues_across_repository_instances(postgres_audit):
    """The head is in the database, not in a process. A second instance must
    link to the first's last event, not start a second chain at GENESIS."""
    cookie = _sign_in("aud-continue@t")
    client.cookies.set("petcare_session", cookie)
    client.post(PROTECTED, json=BODY, headers=HDRS)

    second = PostgresAuditRepository(postgres_audit.pool)
    second.append_event({
        "audit_event_id": "second-instance", "event_name": "e", "actor_id": "a",
        "actor_role": "r", "tenant_id": "t1", "clinic_id": None,
        "resource_type": "rt", "resource_id": "ri", "action_result": "ok",
        "reason_code": None, "correlation_id": "c", "occurred_at": "2026-01-01",
    })
    assert second.verify_chain()["ok"] is True, (
        "a second repository instance forked the chain"
    )


def test_aud_12_an_unreachable_store_fails_closed_rather_than_dropping_events(
    postgres_audit,
):
    """An audit write that silently fails is an unaudited mutation, and
    afterwards it is indistinguishable from an action that never happened."""
    postgres_audit.pool.close()
    with pytest.raises(AuditWriteFailed):
        api.AUDIT_REPO.append_event({
            "audit_event_id": "e", "event_name": "e", "actor_id": "a",
            "actor_role": "r", "tenant_id": "t1", "clinic_id": None,
            "resource_type": "rt", "resource_id": "ri", "action_result": "ok",
            "reason_code": None, "correlation_id": "c", "occurred_at": "2026-01-01",
        })


def test_aud_12b_postgres_mode_with_no_store_refuses_to_build(clean_postgres):
    env = {SECRET_MODE_ENV_VAR: "environment",
           PERSISTENCE_MODE_ENV_VAR: MODE_POSTGRES}
    with pytest.raises(PersistenceUnavailable):
        build_persistence(
            env, connection_url="postgresql://nobody@127.0.0.1:1/nowhere"
                                "?connect_timeout=1"
        )


def test_only_the_governed_fields_are_hashed(postgres_audit):
    """A field that reached the stored record but not the hashed one — or the
    reverse — produces a chain that links correctly and verifies as BROKEN every
    time. W0-G's own receipt records that failure happening once."""
    from audit_repository import GOVERNED_EVENT_FIELDS, core_record

    record = {f: f"v-{f}" for f in GOVERNED_EVENT_FIELDS}
    record["chain_seq"] = 99
    record["smuggled"] = "should not be hashed"
    assert set(core_record(record)) == set(GOVERNED_EVENT_FIELDS)

    stored = api.AUDIT_REPO.append_event(record)
    assert "smuggled" not in stored
    assert api.AUDIT_REPO.verify_chain()["ok"] is True

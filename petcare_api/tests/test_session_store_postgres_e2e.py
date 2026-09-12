"""AC7-01..07 re-proven against PostgreSQL, through the governed serving path.

The previous receipt is explicit that this had not been done:

```
SESSION_STORE_BACKEND_TESTED=IN_MEMORY_ONLY
```

That matters more than it sounds. Every AC-7 control passed against a dict, and
a dict cannot disagree with itself about `NULL`, cannot have a conditional
UPDATE match zero rows, and has no notion of a transaction. The controls were
true of the semantics and silent about the implementation production will run.

So each control below drives the REAL `/api/auth/sign-in` endpoint and the REAL
protected routes with the PostgreSQL adapter installed. Nothing constructs a
cookie by hand and nothing inserts a session record directly — the same
discipline the in-memory end-to-end file keeps, for the same reason: a control
that builds its own session proves what the test can build, not what the service
accepts.

`T-SESSION-ROTATE-PG-01` is the one that could regress silently. If
`read_session` ever accepted a session on a store hit alone, per-session
revocation would still work, every other AC-7 control would still pass, and
global key rotation would quietly stop revoking anything.
"""
import os
import sys

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

pytest.importorskip("psycopg")

import main as api  # noqa: E402
import routers.auth as auth  # noqa: E402
from persistence import MODE_POSTGRES, PERSISTENCE_MODE_ENV_VAR, build_persistence  # noqa: E402
from postgres_repositories import PostgresSessionStore  # noqa: E402
from secret_provider import SECRET_MODE_ENV_VAR  # noqa: E402

client = TestClient(api.app)

PROTECTED = "/api/appointments"
BODY = {"pet_id": "p1", "owner_id": "o1", "clinic_id": "c1", "tenant_id": "t1"}
HDRS = {"X-Correlation-Id": "c-1", "X-Actor-Id": "a-1"}


@pytest.fixture()
def postgres_serving(clean_postgres):
    """Install the PostgreSQL adapter into the live serving path.

    The router reads `SESSION_STORE`, `IDENTITY_REPO` and `INVITE_REPO` from its
    own module namespace, which is the same indirection production uses — so
    replacing them here exercises the real code with the real adapter rather
    than a parallel harness.

    Built through `build_persistence`, not by constructing the classes: the
    selection logic is part of what must work.
    """
    env = {
        SECRET_MODE_ENV_VAR: "environment",
        PERSISTENCE_MODE_ENV_VAR: MODE_POSTGRES,
    }
    persistence = build_persistence(env, connection_url=clean_postgres)
    assert persistence.mode == MODE_POSTGRES
    assert persistence.is_durable is True
    assert isinstance(persistence.session_store, PostgresSessionStore)

    saved = (auth.PERSISTENCE, auth.SESSION_STORE, auth.IDENTITY_REPO, auth.INVITE_REPO)
    auth.PERSISTENCE = persistence
    auth.SESSION_STORE = persistence.session_store
    auth.IDENTITY_REPO = persistence.identities
    auth.INVITE_REPO = persistence.invites
    client.cookies.clear()
    try:
        yield persistence
    finally:
        client.cookies.clear()
        (auth.PERSISTENCE, auth.SESSION_STORE,
         auth.IDENTITY_REPO, auth.INVITE_REPO) = saved
        if persistence.pool is not None:
            persistence.pool.close()


def _sign_in(email: str, role: str = api.ROLE_OWNER, tenant: str | None = "t1") -> str:
    """Authenticate through the REAL endpoint and return the real cookie."""
    auth.seed_user("u-" + email, email, "pw", role, tenant_id=tenant)
    r = client.post("/api/auth/sign-in", json={"email": email, "password": "pw"})
    assert r.status_code == 200, r.text
    return r.cookies["petcare_session"]


def _sid_of(cookie: str) -> str:
    return auth._serializer().loads(cookie, max_age=auth.COOKIE_MAX_AGE)["sid"]


# ---------------------------------------------------------------------------
# The adapter really is the one serving
# ---------------------------------------------------------------------------

def test_the_serving_path_is_actually_backed_by_postgres(postgres_serving):
    """A vacuity guard for the whole file.

    Without it, a fixture that silently failed to install the adapter would
    leave every control below passing against the in-memory store — green, and
    proving exactly what the previous receipt already said was proven.
    """
    assert isinstance(auth.SESSION_STORE, PostgresSessionStore)
    assert auth.PERSISTENCE.is_durable is True

    cookie = _sign_in("backend@t")
    sid = _sid_of(cookie)
    # Visible in the DATABASE, not merely in an object.
    import psycopg

    with psycopg.connect(postgres_serving.pool.conninfo) as conn:
        row = conn.execute(
            "SELECT user_id, tenant_id FROM app_session WHERE session_id = %s",
            (sid,),
        ).fetchone()
    assert row is not None, "sign-in wrote no row to app_session"
    assert row == ("u-backend@t", "t1")


def test_an_identity_is_persisted_as_a_row(postgres_serving):
    _sign_in("rowcheck@t")
    import psycopg

    with psycopg.connect(postgres_serving.pool.conninfo) as conn:
        n = conn.execute(
            "SELECT count(*) FROM user_identity WHERE email = %s", ("rowcheck@t",)
        ).fetchone()[0]
    assert n == 1


# ---------------------------------------------------------------------------
# AC7-01..05 over the wire
# ---------------------------------------------------------------------------

def test_ac7_01_pg_a_revoked_session_is_denied_over_the_wire(postgres_serving):
    cookie = _sign_in("e2e-pg@t")
    sid = _sid_of(cookie)

    record = auth.SESSION_STORE.get_active(sid, tenant_id="t1")
    assert record is not None, "sign-in did not create a stored session"
    assert record.user_id == "u-e2e-pg@t"

    client.cookies.set("petcare_session", cookie)
    ok = client.post(PROTECTED, json=BODY, headers=HDRS)
    assert ok.status_code in (200, 201), ok.text

    assert auth.SESSION_STORE.revoke(sid, tenant_id="t1") is True

    denied = client.post(PROTECTED, json=BODY, headers=HDRS)
    assert denied.status_code == 401, "a revoked session was still honoured"
    assert denied.json()["detail"]["error"] == "SESSION_REVOKED_OR_EXPIRED"


def test_ac7_02_pg_a_tenant_a_session_is_denied_in_tenant_b(postgres_serving):
    cookie = _sign_in("tenant-pg@t", tenant="t1")
    client.cookies.set("petcare_session", cookie)
    r = client.post(PROTECTED, json={**BODY, "tenant_id": "t2"}, headers=HDRS)
    assert r.status_code == 403
    assert r.json()["detail"]["error"] == "TENANT_SCOPE_DENIED"


def test_ac7_03_pg_an_expired_session_is_denied_server_side(postgres_serving):
    from datetime import datetime, timedelta, timezone

    cookie = _sign_in("expiry-pg@t")
    sid = _sid_of(cookie)
    client.cookies.set("petcare_session", cookie)
    assert client.post(PROTECTED, json=BODY, headers=HDRS).status_code in (200, 201)

    # Back-dated in the STORE only; the cookie stays validly signed and within
    # its own max_age, so the denial can only come from the server-side record.
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    with auth.SESSION_STORE._pool.connection() as conn:
        changed = conn.execute(
            "UPDATE app_session SET issued_at = %s, expires_at = %s "
            "WHERE session_id = %s",
            (now - timedelta(hours=2), now - timedelta(minutes=1), sid),
        ).rowcount
    assert changed == 1, "the back-dating did not land; the result below proves nothing"

    denied = client.post(PROTECTED, json=BODY, headers=HDRS)
    assert denied.status_code == 401
    assert denied.json()["detail"]["error"] == "SESSION_REVOKED_OR_EXPIRED"


def test_ac7_04_pg_an_unknown_session_is_denied(postgres_serving):
    cookie = _sign_in("unknown-pg@t")
    sid = _sid_of(cookie)
    with auth.SESSION_STORE._pool.connection() as conn:
        removed = conn.execute(
            "DELETE FROM app_session WHERE session_id = %s", (sid,)
        ).rowcount
    assert removed == 1, "the probe did not land; the result below proves nothing"

    client.cookies.set("petcare_session", cookie)
    denied = client.post(PROTECTED, json=BODY, headers=HDRS)
    assert denied.status_code == 401
    assert denied.json()["detail"]["error"] == "SESSION_REVOKED_OR_EXPIRED"


def test_ac7_05_pg_revoking_one_users_session_leaves_another_active(postgres_serving):
    a = _sign_in("alice-pg@t")
    b = _sign_in("bob-pg@t")
    auth.SESSION_STORE.revoke(_sid_of(a), tenant_id="t1")

    client.cookies.set("petcare_session", b)
    still_ok = client.post(PROTECTED, json=BODY, headers=HDRS)
    assert still_ok.status_code in (200, 201), (
        "revoking alice's session also denied bob over the wire"
    )


def test_ac7_06_pg_individual_revocation_needs_no_key_rotation(postgres_serving):
    """The pair to AC7-07. A store satisfying only this one would silently cost
    the emergency property while every other control still passed."""
    a = _sign_in("solo-pg@t")
    b = _sign_in("other-pg@t")
    key_before = auth.SECRET_KEY

    assert auth.SESSION_STORE.revoke(_sid_of(a), tenant_id="t1") is True
    assert auth.SECRET_KEY == key_before, "revocation rotated the signing key"

    client.cookies.set("petcare_session", a)
    assert client.post(PROTECTED, json=BODY, headers=HDRS).status_code == 401
    client.cookies.set("petcare_session", b)
    assert client.post(PROTECTED, json=BODY, headers=HDRS).status_code in (200, 201)


# ---------------------------------------------------------------------------
# T-SESSION-ROTATE-PG-01 / AC7-07
# ---------------------------------------------------------------------------

def test_t_session_rotate_pg_01_key_rotation_denies_pre_rotation_sessions(
    postgres_serving, monkeypatch
):
    """AC7-07 on PostgreSQL. The denial must come from SIGNATURE VERIFICATION.

    The store record is deliberately left ACTIVE and that is asserted against
    the database before the request is made, so the denial's provenance is
    unambiguous: if the record were revoked or missing, a 401 would prove
    nothing about rotation.
    """
    cookie = _sign_in("rotate-pg@t")
    sid = _sid_of(cookie)

    client.cookies.set("petcare_session", cookie)
    ok = client.post(PROTECTED, json=BODY, headers=HDRS)
    assert ok.status_code in (200, 201), ok.text

    # Rotate the signing key in this isolated process only.
    monkeypatch.setattr(auth, "SECRET_KEY", "rotated-key-not-a-deployed-secret")

    # KEY_ROTATION_PG_STORE_RECORD_ACTIVE_DURING_TEST=YES — asserted, not assumed.
    record = auth.SESSION_STORE.describe(sid)
    assert record is not None, "the store record vanished; the denial would be ambiguous"
    assert record.revoked_at is None, (
        "the session was revoked; this control would then prove nothing"
    )
    assert auth.SESSION_STORE.get_active(sid, tenant_id="t1") is not None, (
        "the store no longer resolves the session as active"
    )

    denied = client.post(PROTECTED, json=BODY, headers=HDRS)

    assert denied.status_code == 401, "a pre-rotation session survived key rotation"
    assert denied.json()["detail"]["error"] == "INVALID_SESSION", (
        "rotation denied the session for the wrong reason — the denial must come "
        "from signature verification, not from the store"
    )


def test_signature_is_verified_before_the_postgres_store_is_consulted(postgres_serving):
    """The ordering AC7-07 depends on, asserted directly against PostgreSQL.

    A cookie signed with a different key carries a REAL, ACTIVE session id from
    the database. It must still be refused, and refused as a signature failure.
    """
    cookie = _sign_in("order-pg@t")
    sid = _sid_of(cookie)
    assert auth.SESSION_STORE.get_active(sid, tenant_id="t1") is not None

    from itsdangerous import URLSafeTimedSerializer

    forged = URLSafeTimedSerializer("a-different-key").dumps(
        {"user_id": "u-order-pg@t", "email": "order-pg@t", "role": api.ROLE_OWNER,
         "tenant_id": "t1", "sid": sid}
    )
    client.cookies.set("petcare_session", forged)
    r = client.post(PROTECTED, json=BODY, headers=HDRS)
    assert r.status_code == 401
    assert r.json()["detail"]["error"] == "INVALID_SESSION", (
        "a cookie bearing a real session id was accepted despite a bad signature"
    )


def test_a_cookie_without_a_session_id_is_refused_on_postgres(postgres_serving):
    legacy = auth._serializer().dumps(
        {"user_id": "u-legacy", "email": "legacy@t", "role": api.ROLE_OWNER,
         "tenant_id": "t1"}
    )
    client.cookies.set("petcare_session", legacy)
    r = client.post(PROTECTED, json=BODY, headers=HDRS)
    assert r.status_code == 401
    assert r.json()["detail"]["error"] == "SESSION_NOT_ESTABLISHED"


# ---------------------------------------------------------------------------
# Registration, which now mints a session record too
# ---------------------------------------------------------------------------

def test_a_registered_user_receives_a_session_that_protected_routes_accept(
    postgres_serving,
):
    """The defect W0-F's wiring exposed.

    `register` minted a cookie with no `sid`, so `read_session` refused it with
    SESSION_NOT_ESTABLISHED on every protected route — while `/api/auth/me`,
    which parses the cookie itself, answered 200. A user who had just registered
    appeared signed in and could do nothing.
    """
    auth.seed_invite_code("PG-PILOT-1", api.ROLE_OWNER)
    r = client.post("/api/auth/register", json={
        "email": "reg-pg@t", "password": "Pilot2026!",
        "invite_code": "PG-PILOT-1", "role": api.ROLE_OWNER, "name": "Reg",
    })
    assert r.status_code == 201, r.text

    payload = auth._serializer().loads(
        r.cookies["petcare_session"], max_age=auth.COOKIE_MAX_AGE
    )
    assert payload.get("sid"), "registration minted a cookie with no session id"
    assert auth.SESSION_STORE.describe(payload["sid"]) is not None

    client.cookies.set("petcare_session", r.cookies["petcare_session"])
    # No tenant assignment yet, so the tenant-scoped route refuses with 403 —
    # NOT with 401. That distinction is the whole point: the session is real and
    # established; it simply carries no tenant authority (W0-C).
    denied = client.post(PROTECTED, json=BODY, headers=HDRS)
    assert denied.status_code == 403, denied.text
    assert denied.json()["detail"]["error"] == "NO_TENANT_AUTHORITY"


def test_a_consumed_invite_code_stays_consumed_across_a_restart(postgres_serving):
    """Durability with a security consequence, not just convenience.

    `_invite_codes` was re-seeded at every process start, so a consumed pilot
    code became unconsumed on restart and registration re-opened on a code that
    was already spent.
    """
    auth.seed_invite_code("PG-PILOT-2", api.ROLE_OWNER)
    first = client.post("/api/auth/register", json={
        "email": "first-pg@t", "password": "Pilot2026!",
        "invite_code": "PG-PILOT-2", "role": api.ROLE_OWNER, "name": "First",
    })
    assert first.status_code == 201

    auth.seed_invite_code("PG-PILOT-2", api.ROLE_OWNER)  # the restart

    second = client.post("/api/auth/register", json={
        "email": "second-pg@t", "password": "Pilot2026!",
        "invite_code": "PG-PILOT-2", "role": api.ROLE_OWNER, "name": "Second",
    })
    assert second.status_code == 400, "a spent invite code was reusable after a restart"
    assert second.json()["detail"]["error"] == "INVALID_INVITE"

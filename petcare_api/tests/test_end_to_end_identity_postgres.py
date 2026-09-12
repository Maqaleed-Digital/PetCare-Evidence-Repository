"""A15 / A16 — the intended production identity path, end to end on PostgreSQL.

The path PRE-1's ruling leaves as the ONLY way a production identity comes into
existence:

```
governed invite-gated registration
  -> canonical machine role
  -> explicit tenant assignment
  -> server-side session
  -> permitted route
  -> audit_event persisted, tenant-scoped, actor server-established
```

No seed helper. No direct database fixture for the user. The identity is created
by driving `POST /api/auth/register`, because the point of this file is that the
path a deployment uses is the path under test — the blind spot CONF-01 lived in
for as long as it did was tests seeding a value no production path produced.
"""
import os
import sys

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

psycopg = pytest.importorskip("psycopg")

import main as api  # noqa: E402
import routers.auth as auth  # noqa: E402
from audit_repository import PostgresAuditRepository  # noqa: E402
from persistence import MODE_POSTGRES, PERSISTENCE_MODE_ENV_VAR, build_persistence  # noqa: E402
from roles import ROLE_OWNER  # noqa: E402
from secret_provider import SECRET_MODE_ENV_VAR  # noqa: E402
from tenants import Tenant  # noqa: E402

client = TestClient(api.app, base_url="https://testserver")

PROTECTED = "/api/appointments"
HDRS = {"X-Correlation-Id": "c-e2e", "X-Actor-Id": "a-e2e"}

TENANT = "t-e2e-synthetic"
OTHER_TENANT = "t-e2e-other"
EMAIL = "e2e-owner@test.invalid"
#: A fixture value, in a test file. It is not read by any application path and
#: no serving source contains a credential literal (SEED-02).
PASSWORD = "fixture-only-not-a-deployed-credential"
INVITE = "E2E-OWNER-INVITE"


@pytest.fixture()
def postgres_serving(clean_postgres):
    env = {SECRET_MODE_ENV_VAR: "environment",
           PERSISTENCE_MODE_ENV_VAR: MODE_POSTGRES}
    persistence = build_persistence(env, connection_url=clean_postgres)
    assert persistence.is_durable
    saved = (auth.PERSISTENCE, auth.SESSION_STORE, auth.IDENTITY_REPO,
             auth.INVITE_REPO, api.AUDIT_REPO)
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
         auth.INVITE_REPO, api.AUDIT_REPO) = saved
        if persistence.pool is not None:
            persistence.pool.close()


def test_the_full_governed_identity_path(postgres_serving):
    p = postgres_serving
    url = p.pool.conninfo

    # 1 · a synthetic tenant, created deliberately. Nothing auto-creates one.
    p.tenants.create(Tenant(tenant_id=TENANT, display_name="E2E Synthetic"))
    assert p.tenants.is_assignable(TENANT)

    # 2 · governed invite-gated registration. NOT a seed helper.
    auth.seed_invite_code(INVITE, ROLE_OWNER)
    registered = client.post("/api/auth/register", json={
        "email": EMAIL, "password": PASSWORD,
        "invite_code": INVITE, "role": ROLE_OWNER, "name": "E2E Owner",
    })
    assert registered.status_code == 201, registered.text

    # 3 · the minted role is the CANONICAL machine id — the value require_role
    #     accepts. This is the assertion CONF-01 would have failed.
    assert registered.json()["user"]["role"] == ROLE_OWNER
    identity = p.identities.get_by_email(EMAIL)
    assert identity is not None and identity.role == ROLE_OWNER
    assert identity.tenant_id is None, (
        "registration assigned a tenant; W0-C makes tenant a server-side act, "
        "never something a registration form establishes"
    )

    # 4 · explicit tenant assignment — a separate, deliberate act.
    #
    #     There is no governed API for this yet, which is a real gap and is
    #     recorded as TENANT_ASSIGNMENT_HAS_NO_GOVERNED_API. It is performed here
    #     through the repository, which is the operator-side boundary, rather
    #     than by writing SQL — a raw insert would prove the database works and
    #     nothing about the path an operator would take.
    from dataclasses import replace

    p.identities.upsert(replace(identity, tenant_id=TENANT))
    assert p.identities.get_by_email(EMAIL).tenant_id == TENANT

    # 5 · sign in through the real endpoint → a server-side session row.
    signed = client.post("/api/auth/sign-in",
                         json={"email": EMAIL, "password": PASSWORD})
    assert signed.status_code == 200, signed.text
    cookie = signed.cookies["petcare_session"]
    sid = auth._serializer().loads(cookie, max_age=auth.COOKIE_MAX_AGE)["sid"]

    with psycopg.connect(url) as conn:
        row = conn.execute(
            "SELECT user_id, tenant_id, role FROM app_session WHERE session_id = %s",
            (sid,),
        ).fetchone()
    assert row is not None, "sign-in wrote no session row"
    assert row[1] == TENANT and row[2] == ROLE_OWNER

    # 6 · a permitted route, reached with the registered vocabulary.
    client.cookies.set("petcare_session", cookie)
    ok = client.post(PROTECTED, json={
        "pet_id": "p1", "owner_id": "o1", "clinic_id": "c1", "tenant_id": TENANT,
    }, headers=HDRS)
    assert ok.status_code in (200, 201), ok.text

    # 7 · the audit event is persisted, tenant-scoped, actor server-established.
    with psycopg.connect(url) as conn:
        events = conn.execute(
            "SELECT tenant_id, actor_role, chain_seq FROM audit_event "
            "WHERE chain_seq IS NOT NULL ORDER BY chain_seq"
        ).fetchall()
    assert events, "a governed route completed without an audit row"
    assert events[-1][0] == TENANT
    assert events[-1][1] == ROLE_OWNER

    # 8 · the tenant foreign key holds on what was written.
    with psycopg.connect(url) as conn:
        assert conn.execute(
            "SELECT count(*) FROM user_identity u JOIN tenant t "
            "ON u.tenant_id = t.tenant_id WHERE u.email = %s", (EMAIL,)
        ).fetchone()[0] == 1

    # 9 · the chain verifies.
    assert PostgresAuditRepository(p.pool).verify_chain()["ok"] is True

    # 10 · cross-tenant access is refused.
    p.tenants.create(Tenant(tenant_id=OTHER_TENANT, display_name="Other"))
    denied = client.post(PROTECTED, json={
        "pet_id": "p1", "owner_id": "o1", "clinic_id": "c1",
        "tenant_id": OTHER_TENANT,
    }, headers=HDRS)
    assert denied.status_code == 403
    assert denied.json()["detail"]["error"] == "TENANT_SCOPE_DENIED"

    # 11 · revoke the session.
    assert p.session_store.revoke(sid, tenant_id=TENANT) is True

    # 12 · the same cookie is refused.
    after = client.post(PROTECTED, json={
        "pet_id": "p1", "owner_id": "o1", "clinic_id": "c1", "tenant_id": TENANT,
    }, headers=HDRS)
    assert after.status_code == 401
    assert after.json()["detail"]["error"] == "SESSION_REVOKED_OR_EXPIRED"


def test_the_registration_path_cannot_mint_a_non_canonical_role(postgres_serving):
    """An invite code is the only way to register, and its `allowed_role` is
    constrained to the canonical catalogue by migration 0033 — so a registration
    cannot introduce a role the guard would refuse."""
    from repositories import RepositoryDenied

    with pytest.raises(RepositoryDenied):
        auth.seed_invite_code("BAD-ROLE-INVITE", "pharmacy")


def test_an_identity_cannot_be_registered_into_an_unknown_tenant(postgres_serving):
    """Registration establishes no tenant at all, so the only way a tenant
    reaches an identity is the deliberate assignment above — and that assignment
    is checked against the registry."""
    from dataclasses import replace
    from tenants import TenantDenied

    p = postgres_serving
    p.tenants.create(Tenant(tenant_id=TENANT, display_name="E2E Synthetic"))
    auth.seed_invite_code(INVITE, ROLE_OWNER)
    client.post("/api/auth/register", json={
        "email": EMAIL, "password": PASSWORD,
        "invite_code": INVITE, "role": ROLE_OWNER, "name": "E2E Owner",
    })
    identity = p.identities.get_by_email(EMAIL)
    with pytest.raises(TenantDenied):
        p.identities.upsert(replace(identity, tenant_id="t-never-registered"))

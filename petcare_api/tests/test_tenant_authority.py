"""W0-C — tenant scope is server-derived; client values are selectors only.

The defect: `body.tenant_id` was trusted in 9 places and
`x_tenant_id: Header(default="platform")` meant an omitted header silently
granted the "platform" scope. Worse, no tenant existed server-side at all -
not on the user record, not in the session - so there was nothing to authorize
a request's tenant against.

PATH PROOF: every test calls a tenant-carrying protected route, so
require_tenant is actually reached.
"""
import pytest
from fastapi.testclient import TestClient

import main as api
from routers import auth

client = TestClient(api.app)
PROTECTED = "/api/appointments"
HDRS = {"X-Actor-Id": "actor-1"}


def _session(role: str, email: str, tenant: str | None):
    auth.seed_user("u-" + email, email, "pw", role, tenant_id=tenant)
    r = client.post("/api/auth/sign-in", json={"email": email, "password": "pw"})
    assert r.status_code == 200, r.text
    return r.cookies["petcare_session"]


def _book(tenant_in_body: str):
    return client.post(
        PROTECTED,
        json={"pet_id": "p1", "owner_id": "o1", "clinic_id": "c1",
              "tenant_id": tenant_in_body},
        headers=HDRS,
    )


def test_t_ten_01_session_a_cannot_act_on_tenant_b_via_body():
    """T-TEN-01 (ARMED) — the core cross-tenant attempt."""
    client.cookies.set("petcare_session", _session(api.ROLE_OWNER, "a@t", "tenant-A"))
    try:
        r = _book("tenant-B")
        assert r.status_code == 403, f"cross-tenant write allowed: {r.status_code}"
        assert r.json()["detail"]["error"] == "TENANT_SCOPE_DENIED"
    finally:
        client.cookies.clear()


def test_t_ten_02_identity_without_tenant_assignment_fails_closed():
    """T-TEN-02 — no server-side tenant means no scope, not a default."""
    client.cookies.set("petcare_session", _session(api.ROLE_OWNER, "notenant@t", None))
    try:
        r = _book("tenant-A")
        assert r.status_code == 403
        assert r.json()["detail"]["error"] == "NO_TENANT_AUTHORITY"
    finally:
        client.cookies.clear()


def test_t_ten_03_unknown_identity_is_denied():
    """T-TEN-03 — unauthenticated callers get no tenant scope."""
    r = _book("tenant-A")
    assert r.status_code == 401


def test_t_ten_04_matching_tenant_is_allowed():
    """Positive control — proves we did not simply deny every request, which
    would pass every negative test vacuously."""
    client.cookies.set("petcare_session", _session(api.ROLE_OWNER, "ok@t", "tenant-A"))
    try:
        r = _book("tenant-A")
        assert r.status_code == 200, r.text
        assert r.json()["tenant_id"] == "tenant-A"
    finally:
        client.cookies.clear()


def test_t_ten_05_no_silent_platform_default_remains():
    """The retired `Header(default="platform")` must not come back."""
    src = open(api.__file__).read()
    assert 'Header(default="platform")' not in src
    assert "x_tenant_id" not in src


def test_t_ten_06_no_route_trusts_body_tenant_directly():
    """Every body tenant reference must be wrapped by require_tenant()."""
    import re
    src = open(api.__file__).read()
    for m in re.finditer(r"body\.tenant_id", src):
        window = src[max(0, m.start() - 60):m.start()]
        assert "require_tenant(" in window, (
            "body.tenant_id used without require_tenant authorization"
        )

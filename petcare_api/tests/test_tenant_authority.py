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
from tenant_fixtures import ensure_tenant

client = TestClient(api.app)
PROTECTED = "/api/appointments"
HDRS = {"X-Actor-Id": "actor-1"}


def _session(role: str, email: str, tenant: str | None):
    ensure_tenant(tenant)
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


#: Routes where a body tenant is an ADMINISTRATIVE DESTINATION rather than the
#: caller's own scope, allowlisted by name with a reason.
#:
#: `require_tenant()` answers "which tenant may THIS CALLER act on", and wrapping
#: an administrative destination in it would be wrong twice over: it would return
#: the admin's own tenant, and the Sponsor ruling of 12 Sep 2026 §3 explicitly
#: authorises a `platform_admin` to administer membership ACROSS tenants.
#:
#: An entry here is a recorded decision. Each names the authority that replaces
#: tenant-scope authorization, and is BOUND TO the control that proves it.
BODY_TENANT_ADMIN_ROUTES: dict[str, str] = {
    "set_tenant_membership":
        "The DESTINATION tenant of a governed membership assignment, not the "
        "caller's scope. Authorised by role (`require_admin`, canonical "
        "platform_admin from the validated session) and validated against the "
        "governed tenant registry inside the same transaction — unknown and "
        "disabled tenants fail closed. "
        "BOUND TO: petcare_api/tests/test_tenant_membership_postgres.py"
        "::test_an_unknown_tenant_fails_closed",
}


def test_t_ten_06_no_route_trusts_body_tenant_directly():
    """Every body tenant reference is authorized — by tenant scope, or by a
    recorded administrative authority."""
    import ast
    import re

    src = open(api.__file__).read()
    tree = ast.parse(src)

    def enclosing_function(offset: int) -> str:
        line = src[:offset].count("\n") + 1
        best = ""
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if node.lineno <= line <= (node.end_lineno or node.lineno):
                    best = node.name
        return best

    for m in re.finditer(r"body\.tenant_id", src):
        window = src[max(0, m.start() - 60):m.start()]
        if "require_tenant(" in window:
            continue
        fn = enclosing_function(m.start())
        assert fn in BODY_TENANT_ADMIN_ROUTES, (
            f"body.tenant_id used in {fn!r} without require_tenant authorization "
            "and without a recorded administrative authority"
        )


def test_every_body_tenant_exemption_names_the_route_and_binds_to_a_control():
    """An exemption whose route has moved protects nothing while reading as a
    considered decision."""
    import re

    src = open(api.__file__).read()
    for name, reason in BODY_TENANT_ADMIN_ROUTES.items():
        assert re.search(rf"^def {re.escape(name)}\(", src, re.M), (
            f"exempted route {name!r} no longer exists in main.py"
        )
        assert "BOUND TO:" in reason, f"{name} has no bound control"
        assert "require_admin" in reason, (
            f"{name}'s exemption does not name the authority that replaces "
            "tenant-scope authorization"
        )

"""W0-B — authorization derives from the validated session, never a header.

The defect: require_role() read `X-Petcare-Role` and only checked the string
was a known role name, so any caller could assert any role and every
`if role != ROLE_X` guard rested on a value the caller chose.

PATH PROOF. The pre-existing suite passes both before and after this change
because none of its 17 tests ever calls a protected endpoint — it exercises
sign-in/register only. A green suite was therefore NOT evidence that W0-B
works. Every test below calls a require_role-protected route so the guard is
actually reached.
"""
import pytest
from fastapi.testclient import TestClient

import main as api
from routers import auth

client = TestClient(api.app)

PROTECTED = "/api/appointments"
BODY = {"pet_id": "p1", "owner_id": "o1", "clinic_id": "c1", "tenant_id": "t1"}
HDRS = {"X-Actor-Id": "actor-1"}


def _session_for(role: str, email: str) -> str:
    """A genuine signed session cookie, minted the way sign-in mints it.

    W0-C made tenant authority a server-side attribute of identity, so a user
    seeded without one now correctly fails closed with NO_TENANT_AUTHORITY.
    These fixtures carry a tenant because they test the ROLE guard, not the
    tenant guard - which has its own suite.
    """
    auth.seed_user("u-" + role, email, "pw", role, tenant_id="t1")
    r = client.post("/api/auth/sign-in", json={"email": email, "password": "pw"})
    assert r.status_code == 200, r.text
    return r.cookies["petcare_session"]


def test_t_auth_01_unauthenticated_with_privileged_header_is_denied():
    """T-AUTH-01 (ARMED) — the original bypass. No session, admin header."""
    r = client.post(PROTECTED, json=BODY,
                    headers={**HDRS, "X-Petcare-Role": api.ROLE_PLATFORM_ADMIN})
    assert r.status_code == 401, (
        f"header-asserted role was honoured without a session: {r.status_code}"
    )


def test_t_auth_02_header_cannot_elevate_a_low_role_session():
    """T-AUTH-02 (ARMED) — veterinarian session + admin header must not elevate.

    Booking is restricted to OWNER/PLATFORM_ADMIN. A veterinarian session that
    claims admin via header must still be refused.
    """
    tok = _session_for(api.ROLE_VETERINARIAN, "vet-elev@test")
    client.cookies.set("petcare_session", tok)
    try:
        r = client.post(PROTECTED, json=BODY,
                        headers={**HDRS, "X-Petcare-Role": api.ROLE_PLATFORM_ADMIN})
        assert r.status_code == 403, (
            f"header elevated a veterinarian session to admin: {r.status_code}"
        )
    finally:
        client.cookies.clear()


def test_t_auth_03_unknown_or_forged_session_is_denied():
    """T-AUTH-03 — a garbage cookie must not authenticate."""
    client.cookies.set("petcare_session", "not-a-valid-signed-token")
    try:
        r = client.post(PROTECTED, json=BODY,
                        headers={**HDRS, "X-Petcare-Role": api.ROLE_OWNER})
        assert r.status_code == 401
    finally:
        client.cookies.clear()


def test_t_auth_04_valid_session_is_allowed_its_permitted_action():
    """Positive control — an OWNER session may book. Proves we did not simply
    deny everything, which would pass every negative test vacuously."""
    tok = _session_for(api.ROLE_OWNER, "owner-ok@test")
    client.cookies.set("petcare_session", tok)
    try:
        r = client.post(PROTECTED, json=BODY, headers=HDRS)
        assert r.status_code == 200, r.text
        assert r.json()["appointment_id"]
    finally:
        client.cookies.clear()


def test_t_auth_05_session_role_wins_when_header_disagrees():
    """An OWNER session with a conflicting header still acts as OWNER."""
    tok = _session_for(api.ROLE_OWNER, "owner-conflict@test")
    client.cookies.set("petcare_session", tok)
    try:
        r = client.post(PROTECTED, json=BODY,
                        headers={**HDRS, "X-Petcare-Role": api.ROLE_PHARMACY_OPERATOR})
        assert r.status_code == 200, "session role must win over the header"
    finally:
        client.cookies.clear()


def test_t_auth_06_require_role_never_reads_the_header():
    """Source-level: the header must not appear in the authorization path."""
    import inspect
    src = inspect.getsource(api.require_role)
    assert "x_petcare_role" not in src.lower().replace("`x-petcare-role`", "")

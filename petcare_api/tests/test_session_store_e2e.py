"""W0-F AC-7 integration — the store reached through the governed login path.

The module-level controls in `test_session_revocation.py` prove the store's
semantics. They do **not** prove the store is wired: every one of them constructs
a store directly. A store with perfect semantics that nothing consults enforces
nothing.

These controls close that gap. Each drives the real `/api/auth/sign-in` endpoint
and the real protected routes, so a regression that quietly disconnected
`read_session` from the store would fail here even though every module-level
control still passed.

Two properties are asserted that pull in opposite directions and must both hold:

* **AC7-01 via the wire** — revoking a stored session denies a cookie that is
  still validly signed and unexpired. Validity is not integrity.
* **AC7-07** — rotating the signing key still denies every pre-rotation session,
  even though its store record is untouched and active. The emergency
  system-wide revocation property must survive the introduction of the store.

The second is the one that could regress silently. If `read_session` ever
accepted a session on a store hit *alone*, per-session revocation would still
work, every AC7 control would still pass, and global key rotation would quietly
stop revoking anything.
"""
import pytest
from fastapi.testclient import TestClient

import main as api
import routers.auth as auth

client = TestClient(api.app)

PROTECTED = "/api/appointments"
BODY = {"pet_id": "p1", "owner_id": "o1", "clinic_id": "c1", "tenant_id": "t1"}
HDRS = {"X-Correlation-Id": "c-1", "X-Actor-Id": "a-1"}


def _sign_in(email: str, role: str = api.ROLE_OWNER, tenant: str | None = "t1") -> str:
    """Authenticate through the REAL endpoint and return the real cookie.

    Deliberately not a fixture that builds a cookie or inserts a record: the
    point of this file is that nothing here bypasses the governed path.
    """
    auth.seed_user("u-" + email, email, "pw", role, tenant_id=tenant)
    r = client.post("/api/auth/sign-in", json={"email": email, "password": "pw"})
    assert r.status_code == 200, r.text
    return r.cookies["petcare_session"]


def _sid_of(cookie: str) -> str:
    return auth._serializer().loads(cookie, max_age=auth.COOKIE_MAX_AGE)["sid"]


@pytest.fixture(autouse=True)
def _clean_cookies():
    client.cookies.clear()
    yield
    client.cookies.clear()


def test_t_session_store_e2e_01_signin_creates_a_stored_session_and_revocation_denies_it():
    """T-SESSION-STORE-E2E-01 — the wiring proof.

    Sign in for real, confirm a server-side record exists, use the real cookie on
    a protected route, revoke that record, and confirm the same cookie is now
    refused.
    """
    cookie = _sign_in("e2e@t")
    sid = _sid_of(cookie)

    # 2 · the governed login path created a server-side record
    record = auth.SESSION_STORE.get_active(sid, tenant_id="t1")
    assert record is not None, "sign-in did not create a stored session"
    assert record.user_id == "u-e2e@t"
    assert record.tenant_id == "t1"

    # 3 · the real cookie works on a protected route
    client.cookies.set("petcare_session", cookie)
    ok = client.post(PROTECTED, json=BODY, headers=HDRS)
    assert ok.status_code in (200, 201), ok.text

    # 4 · revoke the stored session
    assert auth.SESSION_STORE.revoke(sid, tenant_id="t1") is True

    # 5 · the SAME cookie — still validly signed, still unexpired — is refused
    denied = client.post(PROTECTED, json=BODY, headers=HDRS)
    assert denied.status_code == 401, (
        f"a revoked session was still honoured: {denied.status_code}"
    )
    assert denied.json()["detail"]["error"] == "SESSION_REVOKED_OR_EXPIRED"


def test_t_session_rotate_01_key_rotation_denies_pre_rotation_sessions(monkeypatch):
    """T-SESSION-ROTATE-01 / AC7-07 — rotation must still revoke everything.

    Introducing a store must not cost the emergency property. The denial here has
    to come from signature verification, because the store record is deliberately
    left active — so this fails if `read_session` ever accepts on a store hit
    alone.
    """
    cookie = _sign_in("rotate@t")
    sid = _sid_of(cookie)

    client.cookies.set("petcare_session", cookie)
    ok = client.post(PROTECTED, json=BODY, headers=HDRS)
    assert ok.status_code in (200, 201), ok.text

    # 4 · rotate the signing key in this isolated process only
    monkeypatch.setattr(auth, "SECRET_KEY", "rotated-key-not-a-deployed-secret")

    # the record is untouched and still active — the denial must not come from it
    assert auth.SESSION_STORE._sessions[sid].revoked_at is None, (
        "the fixture revoked the session; this control would then prove nothing"
    )

    # 5 · present the pre-rotation cookie again
    denied = client.post(PROTECTED, json=BODY, headers=HDRS)

    # 6 · required result
    assert denied.status_code == 401, (
        f"a pre-rotation session survived key rotation: {denied.status_code}"
    )
    assert denied.json()["detail"]["error"] == "INVALID_SESSION", (
        "rotation denied the session for the wrong reason — the denial must come "
        "from signature verification, not from the store"
    )


def test_signature_is_verified_before_the_store_is_consulted():
    """The ordering AC7-07 depends on, asserted directly.

    A cookie signed with a different key carries a REAL, ACTIVE session id. It
    must still be refused, and refused as a signature failure — which is only
    true if the signature check runs first and is never skipped.
    """
    cookie = _sign_in("order@t")
    sid = _sid_of(cookie)
    assert auth.SESSION_STORE.get_active(sid, tenant_id="t1") is not None

    from itsdangerous import URLSafeTimedSerializer

    forged = URLSafeTimedSerializer("a-different-key").dumps(
        {"user_id": "u-order@t", "email": "order@t", "role": api.ROLE_OWNER,
         "tenant_id": "t1", "sid": sid}
    )
    client.cookies.set("petcare_session", forged)
    r = client.post(PROTECTED, json=BODY, headers=HDRS)
    assert r.status_code == 401
    assert r.json()["detail"]["error"] == "INVALID_SESSION", (
        "a cookie bearing a real session id was accepted despite a bad signature"
    )


def test_a_cookie_without_a_session_id_is_refused():
    """No legacy acceptance path. A correctly signed cookie minted before the
    store existed carries no `sid`, and must be refused rather than admitted on
    its signature alone — a fallback would be a second, ungoverned way in."""
    legacy = auth._serializer().dumps(
        {"user_id": "u-legacy", "email": "legacy@t", "role": api.ROLE_OWNER,
         "tenant_id": "t1"}
    )
    client.cookies.set("petcare_session", legacy)
    r = client.post(PROTECTED, json=BODY, headers=HDRS)
    assert r.status_code == 401
    assert r.json()["detail"]["error"] == "SESSION_NOT_ESTABLISHED"


def test_revoking_one_users_session_does_not_affect_another_over_the_wire():
    """AC7-05 through the real path, not just against the store object."""
    a = _sign_in("alice-e2e@t")
    b = _sign_in("bob-e2e@t")

    auth.SESSION_STORE.revoke(_sid_of(a), tenant_id="t1")

    client.cookies.set("petcare_session", b)
    still_ok = client.post(PROTECTED, json=BODY, headers=HDRS)
    assert still_ok.status_code in (200, 201), (
        "revoking alice's session also denied bob over the wire"
    )

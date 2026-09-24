"""FR-09 — language choice survives a new session (AC-FR-09-02; MVC-BUILD-RUNNER-001 U3).

Driven through the SERVED app (`main.app`). "A new session" is a fresh sign-in
that issues a fresh session cookie — the browser-local store plays no part.
"""
import os
import sys

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import main as api  # noqa: E402
from routers import auth  # noqa: E402
from tenant_fixtures import ensure_tenant  # noqa: E402

pytestmark = pytest.mark.served_app
T_A = "t-lang-alpha"


def _new_session(client: TestClient, user_id: str, role: str = "owner", seed: bool = True) -> None:
    ensure_tenant(T_A)
    if seed:
        auth.seed_user(user_id, f"{user_id}@lang.test", "pw", role, tenant_id=T_A)
    client.cookies.clear()
    r = client.post("/api/auth/sign-in", json={"email": f"{user_id}@lang.test", "password": "pw"})
    assert r.status_code == 200, r.text
    client.cookies.set("petcare_session", r.cookies["petcare_session"])


def test_default_is_arabic_for_a_new_identity():
    c = TestClient(api.app)
    _new_session(c, "u-lang-1")
    assert c.get("/api/me/preferences/language").json() == {"language": "ar", "source": "default"}


def test_choice_survives_a_new_session():
    first = TestClient(api.app)
    _new_session(first, "u-lang-2")
    assert first.put("/api/me/preferences/language", json={"language": "en"}).status_code == 200
    second = TestClient(api.app)                       # a different client: nothing carried over
    _new_session(second, "u-lang-2", seed=False)
    assert second.get("/api/me/preferences/language").json() == {"language": "en", "source": "stored"}


def test_choice_is_per_identity():
    a, b = TestClient(api.app), TestClient(api.app)
    _new_session(a, "u-lang-3")
    _new_session(b, "u-lang-4")
    a.put("/api/me/preferences/language", json={"language": "en"})
    assert b.get("/api/me/preferences/language").json()["language"] == "ar"


def test_unknown_language_is_refused_and_unauthenticated_is_rejected():
    c = TestClient(api.app)
    _new_session(c, "u-lang-5")
    assert c.put("/api/me/preferences/language", json={"language": "fr"}).status_code == 400
    anon = TestClient(api.app)
    assert anon.get("/api/me/preferences/language").status_code == 401
    assert anon.put("/api/me/preferences/language", json={"language": "en"}).status_code == 401


def test_change_is_audited_as_the_session_actor():
    c = TestClient(api.app)
    _new_session(c, "u-lang-6")
    c.put("/api/me/preferences/language", json={"language": "en"}, headers={"X-Actor-Id": "u-spoof"})
    ev = [e for e in c.get("/audit/events/tenant", params={"limit": 1000}).json()["events"]
          if e["event_name"] == "user.preference.language.set" and e["resource_id"] == "u-lang-6"]
    assert ev and ev[-1]["actor_id"] == "u-lang-6", ev

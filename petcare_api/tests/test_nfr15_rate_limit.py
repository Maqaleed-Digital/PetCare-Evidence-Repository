"""NFR-15 API rate limiting — through the SERVED app with the DEFAULT (ratified) policy (MVC-BUILD-RUNNER-001 v1.2 U24).

Ratified: 100 requests/minute per authenticated principal, 30/minute per anonymous client IP, excess -> 429, limits
configurable and auditable. The served limiter is swapped for one with the default policy and a fresh counter, and the
clock is pinned so window boundaries are deterministic.
"""
import os
import sys

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import main as api  # noqa: E402
import ratelimit as rl  # noqa: E402
from repositories import RepositoryDenied  # noqa: E402
from routers import auth  # noqa: E402
from tenant_fixtures import ensure_tenant  # noqa: E402

pytestmark = pytest.mark.served_app
T = "t-nfr15"
NOW = [1_900_000_040.0]  # 20 s into a minute window


@pytest.fixture(autouse=True)
def default_policy(monkeypatch):
    monkeypatch.setattr(api, "RATE_LIMITER", rl.Limiter(repo=rl.InMemoryRateLimitRepository(), policy=rl.Policy.from_env({})))
    monkeypatch.setattr(api, "_rate_clock", lambda: NOW[0])
    NOW[0] = 1_900_000_040.0


def _signed_in(user_id, role="owner"):
    ensure_tenant(T)
    auth.seed_user(user_id, f"{user_id}@nfr15.test", "pw", role, tenant_id=T)
    c = TestClient(api.app)
    r = c.post("/api/auth/sign-in", json={"email": f"{user_id}@nfr15.test", "password": "pw"})
    assert r.status_code == 200, r.text
    c.cookies.set("petcare_session", r.cookies["petcare_session"])
    return c


def test_the_default_policy_is_the_ratified_one_and_configuration_is_validated():
    p = rl.Policy.from_env({})
    assert (p.principal_per_min, p.anonymous_per_min, p.trusted_proxies, p.source) == (100, 30, frozenset(), "default")
    assert rl.Policy.from_env({rl.ENV_PRINCIPAL: "150"}).principal_per_min == 150
    for bad in ("0", "-5", "lots"):
        with pytest.raises(RepositoryDenied):
            rl.Policy.from_env({rl.ENV_PRINCIPAL: bad})
    admin = _signed_in("u-nfr15-admin", "platform_admin")
    eff = admin.get("/api/admin/rate-limits").json()
    assert (eff["principal_per_minute"], eff["anonymous_per_minute"], eff["source"]) == (100, 30, "default")


def test_an_authenticated_principal_gets_100_per_minute_then_429_and_others_are_unaffected():
    a, b = _signed_in("u-nfr15-a"), _signed_in("u-nfr15-b")
    for i in range(100):
        r = a.get("/api/pets", headers={"X-Actor-Id": f"spoof-{i}"})   # a header-supplied identity changes nothing
        assert r.status_code == 200, (i, r.status_code)
    over = a.get("/api/pets")
    assert over.status_code == 429 and over.json()["detail"]["error"] == "RATE_LIMITED"
    assert over.headers["Retry-After"] == "40"                           # 20 s into the window
    assert b.get("/api/pets").status_code == 200                        # principal isolation
    NOW[0] += 40                                                         # the next window
    assert a.get("/api/pets").status_code == 200
    ev = b.get("/audit/events/tenant", params={"limit": 5000}).json()["events"]
    throttled = [e for e in ev if e["event_name"] == "rate_limit.throttled" and e["actor_id"] == "u-nfr15-a"]
    assert len(throttled) == 1 and throttled[0]["reason_code"] == "101>100/min"


def test_an_anonymous_client_gets_30_per_minute_and_a_spoofed_forwarded_for_is_ignored():
    c = TestClient(api.app)
    for i in range(30):
        assert c.get("/health", headers={"X-Forwarded-For": f"10.0.0.{i}"}).status_code == 200, i
    r = c.get("/health", headers={"X-Forwarded-For": "10.9.9.9"})
    assert r.status_code == 429 and int(r.headers["Retry-After"]) > 0


def test_forwarded_for_is_honoured_only_from_a_trusted_proxy(monkeypatch):
    monkeypatch.setattr(api, "RATE_LIMITER", rl.Limiter(repo=rl.InMemoryRateLimitRepository(),
                                                        policy=rl.Policy(trusted_proxies=frozenset({"testclient"}))))
    c = TestClient(api.app)
    for _ in range(30):
        assert c.get("/health", headers={"X-Forwarded-For": "203.0.113.7"}).status_code == 200
    assert c.get("/health", headers={"X-Forwarded-For": "203.0.113.7"}).status_code == 429
    assert c.get("/health", headers={"X-Forwarded-For": "203.0.113.8"}).status_code == 200   # a different client
    assert rl.client_ip("198.51.100.1", "203.0.113.7", frozenset()) == "198.51.100.1"

"""AC-FR-02-04 — POST /api/pets is attributed to the SESSION actor (MVC-BUILD-RUNNER-001 U1).

Ratified criterion (MVC-ACCEPT-PACK-P1): "Every profile create and change is attributed
in the audit chain to the session actor." Fails if "a profile mutation is written with a
client-supplied actor or without an audit event." Every test drives the SERVED app
(`main.app`); none assembles its own.
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

client = TestClient(api.app)
T_A = "t-petaudit-alpha"
T_B = "t-petaudit-beta"


def _login(user_id: str, email: str, tenant: str, role: str = "owner") -> None:
    ensure_tenant(tenant)
    auth.seed_user(user_id, email, "pw", role, tenant_id=tenant)
    r = client.post("/api/auth/sign-in", json={"email": email, "password": "pw"})
    assert r.status_code == 200, r.text
    client.cookies.set("petcare_session", r.cookies["petcare_session"])


def _pet_events(pet_id: str) -> list:
    r = client.get("/audit/events/tenant", params={"limit": 1000})
    assert r.status_code == 200, r.text
    return [e for e in r.json()["events"]
            if e["event_name"] == "pet.profile.created" and e["resource_id"] == pet_id]


@pytest.fixture(autouse=True)
def _clean():
    client.cookies.clear()
    yield
    client.cookies.clear()


def _create(tenant: str, **headers) -> dict:
    r = client.post("/api/pets",
                    json={"tenant_id": tenant, "owner_id": "owner-x", "name": "Luna", "species": "cat"},
                    headers=headers)
    assert r.status_code == 200, r.text
    return r.json()


def test_e1_client_supplied_actor_has_no_effect_on_audit_record():
    _login("u-petaudit-a", "a@petaudit.test", T_A)
    pet = _create(T_A, **{"X-Actor-Id": "u-petaudit-b"})
    events = _pet_events(pet["pet_id"])
    assert len(events) == 1, events
    assert events[0]["actor_id"] == "u-petaudit-a", events[0]
    assert events[0]["actor_role"] == "owner", events[0]


def test_e2_audit_record_is_in_session_tenant_and_invisible_to_other_tenant():
    _login("u-petaudit-a2", "a2@petaudit.test", T_A)
    pet = _create(T_A)
    events = _pet_events(pet["pet_id"])
    assert len(events) == 1 and events[0]["tenant_id"] == T_A, events
    client.cookies.clear()
    _login("u-petaudit-b2", "b2@petaudit.test", T_B)
    assert _pet_events(pet["pet_id"]) == []


def test_e3_unauthenticated_create_is_rejected_and_writes_no_audit():
    before = len(api.AUDIT_REPO.query_events_for_tenant(T_A, limit=100000))
    r = client.post("/api/pets", json={"tenant_id": T_A, "owner_id": "o", "name": "n", "species": "cat"},
                    headers={"X-Actor-Id": "u-intruder"})
    assert r.status_code == 401, r.text
    after = len(api.AUDIT_REPO.query_events_for_tenant(T_A, limit=100000))
    assert after == before


def test_e4_create_without_actor_header_succeeds_and_is_audited():
    """The removed header is no longer required; an omitted actor is not an unaudited write."""
    _login("u-petaudit-a4", "a4@petaudit.test", T_A)
    pet = _create(T_A)
    events = _pet_events(pet["pet_id"])
    assert len(events) == 1 and events[0]["actor_id"] == "u-petaudit-a4", events

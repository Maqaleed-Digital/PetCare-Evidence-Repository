"""AC-FR-01-02 — regulated acts need a LIVE practitioner authority attribute (MVC-BUILD-RUNNER-001 U5).

Fails if "any permission check resolves a regulated act from a role, group, permission
string or token claim without reading a live authority attribute" (REQ-MVC-8.32). Every
test drives the SERVED app (`main.app`) and uses the governed grant/revoke routes.
"""
import os
import sys
from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import main as api  # noqa: E402
from routers import auth  # noqa: E402
from tenant_fixtures import ensure_tenant  # noqa: E402

pytestmark = pytest.mark.served_app
T_A, T_B = "t-auth-alpha", "t-auth-beta"
RX = {"pet_id": "p1", "session_id": "s1", "medication_name": "amoxicillin", "dosage": "50mg",
      "instructions": "twice daily"}


def _client(user_id: str, tenant: str, role: str) -> TestClient:
    ensure_tenant(tenant)
    auth.seed_user(user_id, f"{user_id}@auth.test", "pw", role, tenant_id=tenant)
    c = TestClient(api.app)
    r = c.post("/api/auth/sign-in", json={"email": f"{user_id}@auth.test", "password": "pw"})
    assert r.status_code == 200, r.text
    c.cookies.set("petcare_session", r.cookies["petcare_session"])
    return c


def _grant(admin: TestClient, vet_id: str, **extra) -> dict:
    r = admin.post(f"/api/admin/practitioners/{vet_id}/authority", json={"licence_ref": "MEWA-123", **extra})
    assert r.status_code == 200, r.text
    return r.json()


def test_role_alone_is_refused_and_the_refusal_names_the_attribute():
    vet = _client("u-auth-vet1", T_A, "veterinarian")
    r = vet.post("/api/prescriptions", json={**RX, "tenant_id": T_A})
    assert r.status_code == 403
    assert r.json()["detail"]["error"] == "PRACTITIONER_AUTHORITY_REQUIRED"
    assert r.json()["detail"]["attribute"] == "VETERINARIAN"


def test_a_grant_in_force_permits_the_act_and_the_audit_records_it():
    admin = _client("u-auth-admin2", T_A, "platform_admin")
    vet = _client("u-auth-vet2", T_A, "veterinarian")
    g = _grant(admin, "u-auth-vet2")
    rx = vet.post("/api/prescriptions", json={**RX, "tenant_id": T_A})
    assert rx.status_code == 200, rx.text
    ev = [e for e in vet.get("/audit/events/tenant", params={"limit": 2000}).json()["events"]
          if e["event_name"] == "prescription.issued" and e["resource_id"] == rx.json()["prescription_id"]]
    assert ev and ev[0]["reason_code"] == f"authority:{g['grant_id']}" and ev[0]["actor_id"] == "u-auth-vet2"
    granted = [e for e in admin.get("/audit/events/tenant", params={"limit": 2000}).json()["events"]
               if e["event_name"] == "practitioner.authority.granted" and e["resource_id"] == g["grant_id"]]
    assert granted and granted[0]["actor_id"] == "u-auth-admin2"


def test_revocation_takes_effect_at_the_moment_of_the_next_act():
    admin = _client("u-auth-admin3", T_A, "platform_admin")
    vet = _client("u-auth-vet3", T_A, "veterinarian")
    g = _grant(admin, "u-auth-vet3")
    rx = vet.post("/api/prescriptions", json={**RX, "tenant_id": T_A}).json()
    assert admin.post(f"/api/admin/practitioners/authority/{g['grant_id']}/revoke").status_code == 200
    r = vet.post(f"/api/prescriptions/{rx['prescription_id']}/verify")
    assert r.status_code == 403 and r.json()["detail"]["reason"].startswith("revoked at")


def test_an_expired_grant_is_refused_naming_its_expiry():
    admin = _client("u-auth-admin4", T_A, "platform_admin")
    vet = _client("u-auth-vet4", T_A, "veterinarian")
    past = datetime.now(timezone.utc) - timedelta(days=2)
    _grant(admin, "u-auth-vet4", effective_from=past.isoformat(),
           expires_at=(past + timedelta(days=1)).isoformat())
    r = vet.post("/api/prescriptions", json={**RX, "tenant_id": T_A})
    assert r.status_code == 403 and r.json()["detail"]["reason"].startswith("expired at")


def test_a_grant_in_another_tenant_confers_nothing():
    admin_b = _client("u-auth-admin5", T_B, "platform_admin")
    vet_b = _client("u-auth-vet5", T_B, "veterinarian")
    _grant(admin_b, "u-auth-vet5")
    vet_a = _client("u-auth-vet5a", T_A, "veterinarian")
    assert vet_a.post("/api/prescriptions", json={**RX, "tenant_id": T_A}).status_code == 403
    assert vet_b.post("/api/prescriptions", json={**RX, "tenant_id": T_B}).status_code == 200
    admin_a = _client("u-auth-admin5a", T_A, "platform_admin")
    assert admin_a.post("/api/admin/practitioners/u-auth-vet5/authority",
                        json={"licence_ref": "X"}).status_code == 404


def test_administration_is_admin_only_and_never_self_granted():
    vet = _client("u-auth-vet6", T_A, "veterinarian")
    assert vet.post("/api/admin/practitioners/u-auth-vet6/authority", json={"licence_ref": "X"}).status_code == 403
    admin = _client("u-auth-admin6", T_A, "platform_admin")
    assert admin.post("/api/admin/practitioners/u-auth-admin6/authority",
                      json={"licence_ref": "X"}).status_code == 403
    owner = _client("u-auth-owner6", T_A, "owner")
    assert admin.post("/api/admin/practitioners/u-auth-owner6/authority",
                      json={"licence_ref": "X"}).status_code == 404
    mine = vet.get("/api/practitioners/me/authority").json()
    assert mine["in_force"] is False and mine["grants"] == []

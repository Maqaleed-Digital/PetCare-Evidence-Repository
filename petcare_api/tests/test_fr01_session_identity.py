"""AC-FR-01-01 — accounts per BRD role; every request authorised from the signed session
(MVC-BUILD-RUNNER-001 U4). All tests drive the SERVED app (`main.app`).

Fails if "any served route accepts a role, actor or tenant asserted by the client in
place of the signed session; or a registered identity cannot sign in and reach the
surface of its role."
"""
import dataclasses
import os
import sys
import uuid

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import main as api  # noqa: E402
from routers import auth  # noqa: E402
from tenant_fixtures import ensure_tenant, grant_practitioner_authority  # noqa: E402

pytestmark = pytest.mark.served_app
T_A, T_B = "t-fr01-alpha", "t-fr01-beta"


def _client_for(user_id: str, tenant: str, role: str, seed: bool = True) -> TestClient:
    ensure_tenant(tenant)
    if seed:
        auth.seed_user(user_id, f"{user_id}@fr01.test", "pw", role, tenant_id=tenant)
        if role == "veterinarian":  # FR-05 (U10): clinical acts need a verified licence (live grant)
            grant_practitioner_authority(user_id, tenant)
    c = TestClient(api.app)
    r = c.post("/api/auth/sign-in", json={"email": f"{user_id}@fr01.test", "password": "pw"})
    assert r.status_code == 200, r.text
    c.cookies.set("petcare_session", r.cookies["petcare_session"])
    return c


def _register(role: str) -> str:
    code = f"FR01-{role.upper()}-{uuid.uuid4().hex[:8]}"
    auth.seed_invite_code(code, role)
    email = f"new-{uuid.uuid4().hex[:8]}@fr01.test"
    c = TestClient(api.app)
    # FR-05 (U10): a veterinarian registers with licence details.
    licence = ({"licence": {"licence_number": "MEWA-FR01-1", "issuing_authority": "MEWA",
                            "expires_on": "2099-12-31"}} if role == "veterinarian" else {})
    r = c.post("/api/auth/register", json={"email": email, "password": "Pw-long-enough-1",
                                           "invite_code": code, "role": role, "name": role, **licence})
    assert r.status_code == 201, r.text
    return email


def _signin(email: str, password: str = "Pw-long-enough-1") -> TestClient:
    c = TestClient(api.app)
    r = c.post("/api/auth/sign-in", json={"email": email, "password": password})
    assert r.status_code == 200, r.text
    c.cookies.set("petcare_session", r.cookies["petcare_session"])
    return c


def test_registered_owner_and_vet_and_governed_admin_reach_their_surfaces():
    admin = _client_for("u-fr01-admin", T_A, "platform_admin")
    for role in ("owner", "veterinarian"):
        email = _register(role)
        # Tenant assignment is a durable governed act: the served route refuses in
        # memory mode by design (503) and is proven against PostgreSQL in
        # test_tenant_membership_postgres.py. Here the assignment is a fixture; what
        # this test proves is register -> sign in -> the role's surface.
        ident = auth.IDENTITY_REPO.get_by_email(email)
        auth.IDENTITY_REPO.upsert(dataclasses.replace(ident, tenant_id=T_A))
        c = _signin(email)
        me = c.get("/api/auth/me").json()
        assert me["role"] == role, me
        if role == "owner":
            assert c.post("/api/pets", json={"name": "Luna", "species": "cat"}).status_code == 200
        else:
            assert c.get("/api/prescriptions/queue/awaiting-dispense").status_code == 200
    assert admin.get("/audit/events").status_code == 200


def test_registration_role_is_bound_to_the_invite():
    code = f"FR01-OWN-{uuid.uuid4().hex[:8]}"
    auth.seed_invite_code(code, "owner")
    r = TestClient(api.app).post("/api/auth/register", json={
        "email": f"x-{uuid.uuid4().hex[:6]}@fr01.test", "password": "Pw-long-enough-1",
        "invite_code": code, "role": "platform_admin", "name": "x"})
    assert r.status_code == 400, r.text


def _events(c: TestClient, name: str, resource_id: str) -> list:
    return [e for e in c.get("/audit/events/tenant", params={"limit": 2000}).json()["events"]
            if e["event_name"] == name and e["resource_id"] == resource_id]


def test_client_actor_header_is_ignored_on_appointments_and_consultations():
    spoof = {"X-Actor-Id": "u-spoofed"}
    owner = _client_for("u-fr01-owner", T_A, "owner")
    appt = owner.post("/api/appointments", headers=spoof, json={
        "pet_id": "p1", "owner_id": "u-fr01-owner", "clinic_id": "c1", "tenant_id": T_A}).json()
    assert _events(owner, "appointment.booked", appt["appointment_id"])[0]["actor_id"] == "u-fr01-owner"
    vet = _client_for("u-fr01-vet", T_A, "veterinarian")
    sess = vet.post("/api/consultations", headers=spoof, json={
        "pet_id": "p1", "owner_id": "u-fr01-owner", "veterinarian_id": "u-fr01-vet", "tenant_id": T_A}).json()
    assert _events(vet, "consultation.session.requested", sess["session_id"])[0]["actor_id"] == "u-fr01-vet"
    note = vet.post(f"/api/consultations/{sess['session_id']}/notes", headers=spoof, json={
        "session_id": sess["session_id"], "pet_id": "p1", "content": "ok", "tenant_id": T_A}).json()
    assert note["veterinarian_id"] == "u-fr01-vet"
    signed = vet.post(f"/api/consultations/notes/{note['note_id']}/sign", headers=spoof).json()
    assert signed["signed_by_actor_id"] == "u-fr01-vet"
    assert _events(vet, "consultation.note.signed", note["note_id"])[0]["actor_id"] == "u-fr01-vet"
    viewed = vet.get(f"/api/consultations/{sess['session_id']}", headers=spoof)
    assert viewed.status_code == 200
    assert _events(vet, "consultation.session.viewed", sess["session_id"])[-1]["actor_id"] == "u-fr01-vet"


def test_appointment_and_consultation_records_are_tenant_scoped():
    owner = _client_for("u-fr01-owner2", T_A, "owner")
    appt = owner.post("/api/appointments", json={
        "pet_id": "p1", "owner_id": "u-fr01-owner2", "clinic_id": "c1", "tenant_id": T_A}).json()
    vet_a = _client_for("u-fr01-vet2", T_A, "veterinarian")
    sess = vet_a.post("/api/consultations", json={
        "pet_id": "p1", "owner_id": "o", "veterinarian_id": "u-fr01-vet2", "tenant_id": T_A}).json()
    note = vet_a.post(f"/api/consultations/{sess['session_id']}/notes", json={
        "session_id": sess["session_id"], "pet_id": "p1", "content": "ok", "tenant_id": T_A}).json()
    vet_b = _client_for("u-fr01-vet-b", T_B, "veterinarian")
    admin_b = _client_for("u-fr01-admin-b", T_B, "platform_admin")
    assert admin_b.get(f"/api/appointments/{appt['appointment_id']}").status_code == 404
    assert vet_b.get(f"/api/consultations/{sess['session_id']}").status_code == 404
    assert vet_b.post(f"/api/consultations/{sess['session_id']}/notes", json={
        "session_id": sess["session_id"], "pet_id": "p1", "content": "x", "tenant_id": T_B}).status_code == 404
    assert vet_b.post(f"/api/consultations/notes/{note['note_id']}/sign").status_code == 404


def test_client_supplied_role_header_carries_no_authority():
    owner = _client_for("u-fr01-owner3", T_A, "owner")
    assert owner.get("/audit/events", headers={"X-Petcare-Role": "platform_admin"}).status_code == 403

"""FR-02 pet profile — AC-FR-02-01/02/03 through the SERVED app (MVC-BUILD-RUNNER-001 U2).

Every test drives `main.app`. Durability against real PostgreSQL is proven
separately in test_pet_profile_postgres.py (second-instance read-back).
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
T_A, T_B = "t-petprof-alpha", "t-petprof-beta"
BRD_FIELDS = {"name": "Luna", "species": "cat", "breed": "Siamese", "birth_date": "2021-04-02",
              "weight_kg": 4.2, "medical_conditions": "asthma", "allergies": "penicillin"}


def _login(user_id: str, tenant: str, role: str) -> None:
    client.cookies.clear()
    ensure_tenant(tenant)
    auth.seed_user(user_id, f"{user_id}@petprof.test", "pw", role, tenant_id=tenant)
    r = client.post("/api/auth/sign-in", json={"email": f"{user_id}@petprof.test", "password": "pw"})
    assert r.status_code == 200, r.text
    client.cookies.set("petcare_session", r.cookies["petcare_session"])


@pytest.fixture(autouse=True)
def _clean():
    client.cookies.clear()
    yield
    client.cookies.clear()


def _create(tenant: str, **extra) -> dict:
    r = client.post("/api/pets", json={"tenant_id": tenant, **BRD_FIELDS, **extra})
    assert r.status_code == 200, r.text
    return r.json()


# AC-FR-02-01 --------------------------------------------------------------

def test_ac01_every_brd_field_is_recorded_and_read_back():
    _login("u-pp-owner1", T_A, "owner")
    pet = _create(T_A)
    got = client.get(f"/api/pets/{pet['pet_id']}")
    assert got.status_code == 200, got.text
    prof = got.json()["profile"]
    for k, v in BRD_FIELDS.items():
        assert prof[k] == v, (k, prof[k])
    assert prof["owner_id"] == "u-pp-owner1" and prof["tenant_id"] == T_A


def test_ac01_owner_cannot_create_for_someone_else():
    _login("u-pp-owner1b", T_A, "owner")
    pet = _create(T_A, owner_id="u-someone-else")
    assert pet["owner_id"] == "u-pp-owner1b"


def test_ac01_profile_is_unreadable_from_another_tenant():
    _login("u-pp-owner2", T_A, "owner")
    pet = _create(T_A)
    _login("u-pp-vet-b", T_B, "veterinarian")
    assert client.get(f"/api/pets/{pet['pet_id']}").status_code == 404
    assert all(p["pet_id"] != pet["pet_id"] for p in client.get("/api/pets").json())


def test_ac01_owner_cannot_read_another_owners_pet_in_same_tenant():
    _login("u-pp-owner3", T_A, "owner")
    pet = _create(T_A)
    _login("u-pp-owner4", T_A, "owner")
    assert client.get(f"/api/pets/{pet['pet_id']}").status_code == 404
    assert all(p["pet_id"] != pet["pet_id"] for p in client.get("/api/pets").json())


def test_ac01_unknown_profile_field_is_refused():
    _login("u-pp-owner5", T_A, "owner")
    r = client.post("/api/pets", json={"tenant_id": T_A, "name": "x", "species": "dog", "health_score": 9})
    assert r.status_code == 422


# AC-FR-02-02 --------------------------------------------------------------

def test_ac02_history_shows_lab_result_and_prescription():
    _login("u-pp-owner6", T_A, "owner")
    pet = _create(T_A)
    _login("u-pp-vet6", T_A, "veterinarian")
    lab = client.post(f"/api/pets/{pet['pet_id']}/medical-records",
                      json={"record_type": "LAB_RESULT", "title": "CBC", "detail": "within range"})
    assert lab.status_code == 200, lab.text
    rx = client.post("/api/prescriptions", json={
        "pet_id": pet["pet_id"], "session_id": "sess-pp", "tenant_id": T_A, "clinic_id": "c-1",
        "medication_name": "amoxicillin", "dosage": "50mg", "instructions": "twice daily"})
    assert rx.status_code == 200, rx.text
    hist = client.get(f"/api/pets/{pet['pet_id']}").json()["medical_history"]
    assert [r["title"] for r in hist["records"]] == ["CBC"]
    assert [p["prescription_id"] for p in hist["prescriptions"]] == [rx.json()["prescription_id"]]


def test_ac02_owner_preferences_are_stored_and_shown():
    _login("u-pp-owner7", T_A, "owner")
    pet = _create(T_A)
    r = client.patch(f"/api/pets/{pet['pet_id']}", json={"preferences": "contact by SMS; female vet"})
    assert r.status_code == 200, r.text
    assert client.get(f"/api/pets/{pet['pet_id']}").json()["profile"]["preferences"] == "contact by SMS; female vet"


def test_ac02_only_a_veterinarian_records_medical_history():
    _login("u-pp-owner8", T_A, "owner")
    pet = _create(T_A)
    r = client.post(f"/api/pets/{pet['pet_id']}/medical-records",
                    json={"record_type": "LAB_RESULT", "title": "self-reported"})
    assert r.status_code == 403


# AC-FR-02-03 --------------------------------------------------------------

def test_ac03_identification_is_structured_and_optional():
    _login("u-pp-owner9", T_A, "owner")
    pet = _create(T_A)
    assert client.get(f"/api/pets/{pet['pet_id']}").json()["identifications"] == []
    r = client.post(f"/api/pets/{pet['pet_id']}/identifications", json={
        "id_type": "MICROCHIP", "id_value": "982000123456789", "captured_at": "2024-02-01",
        "capture_method": "scanner"})
    assert r.status_code == 200, r.text
    ident = client.get(f"/api/pets/{pet['pet_id']}").json()["identifications"]
    assert len(ident) == 1
    assert {k: ident[0][k] for k in ("id_type", "id_value", "captured_at")} == {
        "id_type": "MICROCHIP", "id_value": "982000123456789", "captured_at": "2024-02-01"}


def test_ac03_identification_is_never_free_text():
    _login("u-pp-owner10", T_A, "owner")
    r = client.post("/api/pets", json={"tenant_id": T_A, "name": "x", "species": "dog",
                                       "microchip": "chip 123 somewhere"})
    assert r.status_code == 422
    pet = _create(T_A)
    bad_type = client.post(f"/api/pets/{pet['pet_id']}/identifications", json={
        "id_type": "NOTE", "id_value": "chip 123", "captured_at": "2024-02-01", "capture_method": "x"})
    assert bad_type.status_code == 400
    other_no_scheme = client.post(f"/api/pets/{pet['pet_id']}/identifications", json={
        "id_type": "OTHER", "id_value": "X-1", "captured_at": "2024-02-01", "capture_method": "x"})
    assert other_no_scheme.status_code == 400


# AC-FR-02-04 (change path) -------------------------------------------------

def test_ac04_profile_change_is_audited_as_session_actor():
    _login("u-pp-owner11", T_A, "owner")
    pet = _create(T_A)
    r = client.patch(f"/api/pets/{pet['pet_id']}", json={"weight_kg": 4.5},
                     headers={"X-Actor-Id": "u-spoof"})
    assert r.status_code == 200, r.text
    ev = [e for e in client.get("/audit/events/tenant", params={"limit": 1000}).json()["events"]
          if e["event_name"] == "pet.profile.updated" and e["resource_id"] == pet["pet_id"]]
    assert len(ev) == 1 and ev[0]["actor_id"] == "u-pp-owner11", ev

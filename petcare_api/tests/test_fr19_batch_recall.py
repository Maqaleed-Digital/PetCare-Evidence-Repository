"""FR-19 SFDA batch tracking and recall notifications — ratified AC-FR-19-01/02 through the SERVED app
(MVC-BUILD-RUNNER-001 U13). AC-FR-19-03/04 (EXTERNAL:SFDA_API): the ingestion boundary refuses a recall
without product and batch; the SFDA interface contract is not held and nothing is registered for it."""
import os
import sys
from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import main as api  # noqa: E402
from inventory import REGISTRATION_SOURCE, ProductRegistration  # noqa: E402
from routers import auth  # noqa: E402
from tenant_fixtures import ensure_tenant, grant_practitioner_authority, stock_origin  # noqa: E402

pytestmark = pytest.mark.served_app
T_A, T_B = "t-fr19-alpha", "t-fr19-beta"


def _client(user_id, tenant, role):
    ensure_tenant(tenant)
    auth.seed_user(user_id, f"{user_id}@fr19.test", "pw", role, tenant_id=tenant)
    if role == "veterinarian":
        grant_practitioner_authority(user_id, tenant)
    c = TestClient(api.app)
    r = c.post("/api/auth/sign-in", json={"email": f"{user_id}@fr19.test", "password": "pw"})
    assert r.status_code == 200, r.text
    c.cookies.set("petcare_session", r.cookies["petcare_session"])
    return c


def _events(c, name):
    return [e for e in c.get("/audit/events/tenant", params={"limit": 5000}).json()["events"] if e["event_name"] == name]


def _dispense(vet, owner, tenant, product, batch, *, stored_pet=True):
    pet_id = owner.post("/api/pets", json={"name": "Luna", "species": "cat"}).json()["pet_id"] if stored_pet else "free-text-pet"
    rx = vet.post("/api/prescriptions", json={"pet_id": pet_id, "session_id": "s", "medication_name": product,
                                              "dosage": "1", "instructions": "i"}).json()["prescription_id"]
    assert vet.post(f"/api/prescriptions/{rx}/verify").status_code == 200
    r = vet.post(f"/api/prescriptions/{rx}/dispense", json=stock_origin(tenant, product_id=product, batch=batch))
    assert r.status_code == 200, r.text
    return rx, pet_id, r.json()


# --------------------------------------------------------------------------- AC-FR-19-01
def test_every_movement_and_dispense_records_the_batch():
    vet = _client("u-fr19-vet", T_A, "veterinarian")
    owner = _client("u-fr19-owner", T_A, "owner")
    admin = _client("u-fr19-admin", T_A, "partner_clinic_admin")
    rx, _pet, body = _dispense(vet, owner, T_A, "amoxi-19", "LOT-A")
    assert body["status"] == "DISPENSED" and body["dispensed_batch"] == "LOT-A"
    ledger = [m for m in api.INVENTORY_REPO.movements(tenant_id=T_A) if m.movement_id == body["movement_id"]]
    assert len(ledger) == 1 and (ledger[0].reason, ledger[0].batch, ledger[0].prescription_id) == ("SUPPLY", "LOT-A", rx)
    assert ledger[0].quantity_delta == -1
    # A verified prescription is never dispensed without a stock origin (no batch, no dispense).
    rx2 = vet.post("/api/prescriptions", json={"pet_id": "p", "session_id": "s", "medication_name": "m", "dosage": "d",
                                               "instructions": "i"}).json()["prescription_id"]
    vet.post(f"/api/prescriptions/{rx2}/verify")
    assert vet.post(f"/api/prescriptions/{rx2}/dispense").status_code == 400
    assert vet.get(f"/api/prescriptions/{rx2}").json()["status"] == "VET_VERIFIED"
    # A receipt records the batch expiry; one without it is refused. A movement without a batch is refused.
    loc = admin.post("/api/inventory/locations", json={"name": "Batch shelf"}).json()["location_id"]
    api.INVENTORY_REPO.register_product(ProductRegistration(product_id="gauze-19", name="g", supply_class="GENERAL",
                                                            source=REGISTRATION_SOURCE,
                                                            registered_at=datetime.now(timezone.utc)))
    base = {"location_id": loc, "product_id": "gauze-19", "quantity_delta": 5, "reason": "RECEIPT"}
    assert admin.post("/api/inventory/movements", json={**base, "batch": "G1"}).status_code == 400
    assert admin.post("/api/inventory/movements", json={**base, "batch": "  ", "batch_expiry": "2030-01-01"}).status_code == 400
    ok = admin.post("/api/inventory/movements", json={**base, "batch": "G1", "batch_expiry": "2030-01-01"})
    assert ok.status_code == 200 and ok.json()[0]["batch_expiry"] == "2030-01-01"
    stock = admin.get("/api/inventory/stock", params={"product_id": "gauze-19"}).json()["locations"]
    assert [b["batch_expiry"] for x in stock if x["location_id"] == loc for b in x["stock"]] == ["2030-01-01"]
    audited = [e for e in _events(admin, "inventory.movement.recorded") if e["resource_id"] == body["movement_id"]]
    assert audited and "batch:LOT-A" in audited[0]["reason_code"] and audited[0]["actor_id"] == "u-fr19-vet"


# --------------------------------------------------------------------------- AC-FR-19-02
def test_a_recall_resolves_through_stored_relationships_and_notifies_every_affected_owner():
    vet = _client("u-fr19-vet2", T_A, "veterinarian")
    owner1 = _client("u-fr19-owner1", T_A, "owner")
    owner2 = _client("u-fr19-owner2", T_A, "owner")
    bystander = _client("u-fr19-owner3", T_A, "owner")
    admin = _client("u-fr19-admin2", T_A, "partner_clinic_admin")
    rx1, pet1, d1 = _dispense(vet, owner1, T_A, "vax-19", "BAD-1")
    rx2, pet2, d2 = _dispense(vet, owner2, T_A, "vax-19", "BAD-1")
    _rx3, _p3, d3 = _dispense(vet, owner1, T_A, "vax-19", "BAD-1", stored_pet=False)   # pet named by free text
    _dispense(vet, bystander, T_A, "vax-19", "GOOD-2")                                 # another batch
    r = admin.post("/api/recalls", json={"product_id": "vax-19", "batch": "BAD-1", "reason": "potency failure"})
    assert r.status_code == 200, r.text
    res = r.json()
    assert {(x["owner_id"], x["prescription_id"], x["pet_id"]) for x in res["resolved"]} == {
        ("u-fr19-owner1", rx1, pet1), ("u-fr19-owner2", rx2, pet2)}
    assert res["indeterminate"] == [{"movement_id": d3["movement_id"], "reason": "PET_NOT_STORED",
                                     "prescription_id": _rx3}]
    comp = res["completeness"]
    assert (comp["supplies_of_batch"], comp["resolved"], comp["indeterminate"], comp["complete"]) == (3, 2, 1, False)
    assert "3 supply movement(s)" in comp["statement"] and "1 indeterminate" in comp["statement"]
    assert res["notified_owners"] == ["u-fr19-owner1", "u-fr19-owner2"]
    for o in (owner1, owner2):
        notices = o.get("/api/me/recall-notices").json()
        assert notices and all("BAD-1" in n["body"] for n in notices)
    assert bystander.get("/api/me/recall-notices").json() == []
    again = admin.get(f"/api/recalls/{res['recall_id']}").json()
    assert again["completeness"]["statement"] == comp["statement"] and "indeterminate" in again
    notified = [e for e in _events(admin, "recall.owner_notified")]
    assert {e["reason_code"] for e in notified} >= {"owner:u-fr19-owner1", "owner:u-fr19-owner2"}
    assert [e["actor_id"] for e in _events(admin, "recall.created") if e["resource_id"] == res["recall_id"]] == ["u-fr19-admin2"]


def test_a_recall_never_crosses_tenants():
    vet_a = _client("u-fr19-vet4", T_A, "veterinarian")
    owner_a = _client("u-fr19-owner4", T_A, "owner")
    admin_b = _client("u-fr19-admin4b", T_B, "partner_clinic_admin")
    _dispense(vet_a, owner_a, T_A, "vax-19b", "LOT-X")
    res = admin_b.post("/api/recalls", json={"product_id": "vax-19b", "batch": "LOT-X", "reason": "r"}).json()
    assert res["resolved"] == [] and res["indeterminate"] == [] and res["completeness"]["supplies_of_batch"] == 0
    assert owner_a.get("/api/me/recall-notices").json() == []
    assert _client("u-fr19-admin4", T_A, "partner_clinic_admin").get(f"/api/recalls/{res['recall_id']}").status_code == 404


# --------------------------------------------------------------------------- AC-FR-19-03 (boundary; not evidence)
@pytest.mark.parametrize("body", [{"product_id": "", "batch": "B", "reason": "r"},
                                  {"product_id": "P", "batch": " ", "reason": "r"}])
def test_a_recall_without_product_and_batch_is_refused(body):
    admin = _client("u-fr19-admin5", T_A, "partner_clinic_admin")
    assert admin.post("/api/recalls", json=body).status_code == 400

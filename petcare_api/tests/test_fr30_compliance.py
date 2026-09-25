"""FR-30 SFDA compliance reporting automation — ratified AC-FR-30-01/02/03 through the SERVED app
(MVC-BUILD-RUNNER-001 U16). AC-FR-30-04/05 (EXTERNAL:SFDA) — regulator submission — are not built."""
import os
import sys
from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import main as api  # noqa: E402
from compliance import NotifiableDisease  # noqa: E402
from inventory import REGISTRATION_SOURCE, ProductRegistration, StockMovement  # noqa: E402
from routers import auth  # noqa: E402
from tenant_fixtures import ensure_tenant, grant_practitioner_authority, stock_origin  # noqa: E402

pytestmark = pytest.mark.served_app
T_A, T_B = "t-fr30-alpha", "t-fr30-beta"


def _client(user_id, tenant, role):
    ensure_tenant(tenant)
    auth.seed_user(user_id, f"{user_id}@fr30.test", "pw", role, tenant_id=tenant)
    if role == "veterinarian":
        grant_practitioner_authority(user_id, tenant)
    c = TestClient(api.app)
    r = c.post("/api/auth/sign-in", json={"email": f"{user_id}@fr30.test", "password": "pw"})
    assert r.status_code == 200, r.text
    c.cookies.set("petcare_session", r.cookies["petcare_session"])
    return c


def _register(product_id, klass="POM", agent=None, agent_class=None):
    if product_id not in api.INVENTORY_REPO._products:
        api.INVENTORY_REPO.register_product(ProductRegistration(
            product_id=product_id, name=product_id, supply_class=klass, source=REGISTRATION_SOURCE,
            registered_at=datetime.now(timezone.utc), antimicrobial_agent=agent, antimicrobial_class=agent_class))


def _window():
    now = datetime.now(timezone.utc)
    return {"period_from": (now - timedelta(hours=1)).isoformat(), "period_to": (now + timedelta(hours=1)).isoformat()}


def _issue(vet, pet_id, product_id=None, med="m"):
    body = {"pet_id": pet_id, "session_id": "s", "medication_name": med, "dosage": "d", "instructions": "i"}
    if product_id:
        body["product_id"] = product_id
    r = vet.post("/api/prescriptions", json=body)
    assert r.status_code == 200, r.text
    return r.json()["prescription_id"]


# --------------------------------------------------------------------------- AC-FR-30-01
def test_the_controlled_substance_report_is_generated_from_recorded_events_and_traces_to_them():
    vet = _client("u-fr30-vet", T_A, "veterinarian")
    owner = _client("u-fr30-owner", T_A, "owner")
    admin_b = _client("u-fr30-admin-b", T_B, "partner_clinic_admin")
    _register("keta-30", "CONTROLLED")
    # FR-04 AC-FR-04-02 (U17): the served app can no longer create CONTROLLED movements while EV-11 is open, so the
    # recorded controlled history is written at the repository layer — the report must still be generated from it.
    origin = stock_origin(T_A, product_id="keta-30", batch="K1")          # RECEIPT +1000 CONTROLLED (recorded)
    pet = owner.post("/api/pets", json={"name": "Luna", "species": "cat"}).json()["pet_id"]
    rx = _issue(vet, pet, "keta-30")
    assert vet.post(f"/api/prescriptions/{rx}/verify").status_code == 200
    assert vet.post(f"/api/prescriptions/{rx}/dispense", json={**origin, "quantity": 2}).status_code == 403

    def _hist(delta, reason, rx_id=None):
        api.INVENTORY_REPO.record([StockMovement(
            movement_id=f"hist-{reason}-{delta}-{datetime.now(timezone.utc).timestamp()}", tenant_id=T_A,
            location_id=origin["location_id"], product_id="keta-30", batch="K1", quantity_delta=delta, reason=reason,
            supply_class="CONTROLLED", actor_id="u-fr30-vet", actor_role="veterinarian",
            created_at=datetime.now(timezone.utc), prescription_id=rx_id)])

    _hist(-2, "SUPPLY", rx)
    _hist(-3, "ADJUSTMENT")
    r = vet.post("/api/compliance/reports/controlled-substances", json=_window())
    assert r.status_code == 200, r.text
    rep = r.json()
    ledger = {m.movement_id: m for m in api.INVENTORY_REPO.movements(tenant_id=T_A)}
    assert [x["reason"] for x in rep["rows"]] == ["RECEIPT", "SUPPLY", "ADJUSTMENT"]
    assert all(x["movement_id"] in ledger and ledger[x["movement_id"]].supply_class == "CONTROLLED" for x in rep["rows"])
    (total,) = rep["totals"]
    assert total["net_quantity"] == 1000 - 2 - 3 == sum(ledger[i].quantity_delta for i in total["movement_ids"])
    assert [x["prescription_id"] for x in rep["rows"] if x["reason"] == "SUPPLY"] == [rx]
    again = vet.get(f"/api/compliance/reports/{rep['report_id']}").json()
    assert again["reproduces"] is True and again["content_sha256"] == rep["content_sha256"]
    _hist(-1, "ADJUSTMENT")
    assert vet.get(f"/api/compliance/reports/{rep['report_id']}").json()["reproduces"] is False  # the check is live
    audited = [e for e in vet.get("/audit/events/tenant", params={"limit": 5000}).json()["events"]
               if e["event_name"] == "compliance.report.generated" and e["resource_id"] == rep["report_id"]]
    assert len(audited) == 1 and audited[0]["actor_id"] == "u-fr30-vet"
    assert admin_b.post("/api/compliance/reports/controlled-substances", json=_window()).json()["rows"] == []
    assert admin_b.get(f"/api/compliance/reports/{rep['report_id']}").status_code == 404


# --------------------------------------------------------------------------- AC-FR-30-02
def test_antimicrobial_prescribing_aggregates_by_agent_class_species_practitioner_and_period():
    vet1 = _client("u-fr30-vet1", T_A, "veterinarian")
    vet2 = _client("u-fr30-vet2", T_A, "veterinarian")
    owner = _client("u-fr30-owner2", T_A, "owner")
    admin = _client("u-fr30-admin", T_A, "partner_clinic_admin")
    _register("amoxi-30", agent="amoxicillin", agent_class="penicillin")
    _register("enro-30", agent="enrofloxacin", agent_class="fluoroquinolone")
    _register("nsaid-30")
    cat = owner.post("/api/pets", json={"name": "Cat", "species": "cat"}).json()["pet_id"]
    dog = owner.post("/api/pets", json={"name": "Dog", "species": "dog"}).json()["pet_id"]
    before = admin.get("/api/compliance/antimicrobials", params={"group_by": "agent"}).json()["coverage"]
    ids = [_issue(vet1, cat, "amoxi-30"), _issue(vet1, dog, "amoxi-30"), _issue(vet1, cat, "enro-30"),
           _issue(vet2, cat, "amoxi-30"), _issue(vet2, "free-text-pet", "amoxi-30")]
    _issue(vet1, cat, "nsaid-30")                               # not antimicrobial
    _issue(vet1, cat, None, med="amoxicillin 50mg")             # free text only: never counted by text search
    full = admin.get("/api/compliance/antimicrobials").json()
    mine = [r for r in full["rows"] if set(r["prescription_ids"]) & set(ids)]
    key = {(r["agent"], r["agent_class"], r["species"], r["practitioner"]): r["prescriptions"] for r in mine}
    assert key == {("amoxicillin", "penicillin", "cat", "u-fr30-vet1"): 1, ("amoxicillin", "penicillin", "dog", "u-fr30-vet1"): 1,
                   ("enrofloxacin", "fluoroquinolone", "cat", "u-fr30-vet1"): 1,
                   ("amoxicillin", "penicillin", "cat", "u-fr30-vet2"): 1,
                   ("amoxicillin", "penicillin", "UNRESOLVED", "u-fr30-vet2"): 1}
    assert all(r["period"] == datetime.now(timezone.utc).strftime("%Y-%m") for r in mine)
    by_agent = admin.get("/api/compliance/antimicrobials", params={"group_by": "agent"}).json()
    cov = by_agent["coverage"]
    assert cov["antimicrobial_prescriptions"] - before["antimicrobial_prescriptions"] == 5
    assert ids[4] in cov["species_unresolved"] and "UNRESOLVED" in cov["statement"]
    assert admin.get("/api/compliance/antimicrobials", params={"group_by": "colour"}).status_code == 400


# --------------------------------------------------------------------------- AC-FR-30-03
def test_a_notifiable_case_carries_its_statutory_clock_from_detection():
    vet = _client("u-fr30-vet3", T_A, "veterinarian")
    owner = _client("u-fr30-owner3", T_A, "owner")
    admin = _client("u-fr30-admin3", T_A, "partner_clinic_admin")
    if api.COMPLIANCE_REPO.disease("RABIES-30") is None:
        api.COMPLIANCE_REPO.register_disease(NotifiableDisease("RABIES-30", "Rabies", 24, "test register"))
    pet = owner.post("/api/pets", json={"name": "Rex", "species": "dog"}).json()["pet_id"]
    detected = datetime.now(timezone.utc) - timedelta(hours=2)
    r = vet.post(f"/api/pets/{pet}/notifiable-cases", json={"disease_code": "RABIES-30", "detected_at": detected.isoformat()})
    assert r.status_code == 200, r.text
    c = r.json()
    assert c["clock"]["detected_at"] == detected.isoformat()
    assert c["clock"]["report_due_at"] == (detected + timedelta(hours=24)).isoformat()
    assert c["clock"]["status"] == "OPEN" and 21.5 < c["clock"]["hours_remaining"] <= 22
    assert vet.post(f"/api/pets/{pet}/notifiable-cases", json={"disease_code": "NOT-LISTED",
                                                               "detected_at": detected.isoformat()}).status_code == 400
    listed = [x for x in admin.get("/api/compliance/notifiable-cases").json() if x["case_id"] == c["case_id"]]
    assert listed and listed[0]["clock"]["report_due_at"] == c["clock"]["report_due_at"]
    assert admin.post(f"/api/compliance/notifiable-cases/{c['case_id']}/reported", json={"reference": "MEWA-REP-1"}).status_code == 200
    assert [x["clock"]["status"] for x in admin.get("/api/compliance/notifiable-cases").json()
            if x["case_id"] == c["case_id"]] == ["REPORTED"]
    ev = [e for e in admin.get("/audit/events/tenant", params={"limit": 5000}).json()["events"]
          if e["resource_id"] == c["case_id"]]
    rec = [e for e in ev if e["event_name"] == "notifiable.case.recorded"]
    assert rec and rec[0]["actor_id"] == "u-fr30-vet3" and "due:" in rec[0]["reason_code"]
    assert [e["actor_id"] for e in ev if e["event_name"] == "notifiable.case.reported"] == ["u-fr30-admin3"]

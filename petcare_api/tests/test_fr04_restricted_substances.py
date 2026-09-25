"""FR-04 KYC verification for controlled medication purchases — ratified AC-FR-04-01/02/03 through the SERVED
app (MVC-BUILD-RUNNER-001 U17).

AC-FR-04-02: until counsel resolves EV-11 and L-2 the restricted-substance workflow (dispensing, register,
wastage) is DISABLED in every environment and nothing — flag, admin action or configuration — enables it.
AC-FR-04-01 (dependency COUNSEL:EV-11): no path supplies a RESTRICTED/CONTROLLED product without a recorded
passed verification — today no path supplies one at all; the dependency itself is not evidenced.
AC-FR-04-03: supply class comes only from product registration; an unregistered medicine is POM.
AC-FR-04-04/05 (EXTERNAL:KYC_PROVIDER) are not built.
"""
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import inventory  # noqa: E402
import main as api  # noqa: E402
from inventory import REGISTRATION_SOURCE, ProductRegistration  # noqa: E402
from routers import auth  # noqa: E402
from tenant_fixtures import ensure_tenant, grant_practitioner_authority  # noqa: E402

pytestmark = pytest.mark.served_app
T_A, T_B = "t-fr04-alpha", "t-fr04-beta"
ROOT = Path(__file__).resolve().parents[2]
ENABLING_ATTEMPTS = {"PETCARE_RESTRICTED_SUBSTANCE_WORKFLOW": "enabled", "PETCARE_ENABLE_CONTROLLED": "1",
                     "FEATURE_RESTRICTED_SUBSTANCES": "true", "EV11_RESOLVED": "true", "L2_RESOLVED": "true"}


def _client(user_id, tenant, role):
    ensure_tenant(tenant)
    auth.seed_user(user_id, f"{user_id}@fr04.test", "pw", role, tenant_id=tenant)
    if role == "veterinarian":
        grant_practitioner_authority(user_id, tenant)
    c = TestClient(api.app)
    r = c.post("/api/auth/sign-in", json={"email": f"{user_id}@fr04.test", "password": "pw"})
    assert r.status_code == 200, r.text
    c.cookies.set("petcare_session", r.cookies["petcare_session"])
    return c


def _register(product_id, klass):
    if product_id not in api.INVENTORY_REPO._products:
        api.INVENTORY_REPO.register_product(ProductRegistration(product_id=product_id, name=product_id, supply_class=klass,
                                                                source=REGISTRATION_SOURCE,
                                                                registered_at=datetime.now(timezone.utc)))


def _disabled(r):
    detail = r.json().get("detail") if r.status_code == 403 else None
    return isinstance(detail, dict) and detail.get("error") == "RESTRICTED_SUBSTANCE_WORKFLOW_DISABLED"


# --------------------------------------------------------------------------- AC-FR-04-02 (+ AC-FR-04-01)
@pytest.mark.parametrize("klass", ["RESTRICTED", "CONTROLLED"])
def test_the_restricted_substance_workflow_is_disabled_on_every_path_and_nothing_enables_it(klass, monkeypatch):
    for k, v in ENABLING_ATTEMPTS.items():
        monkeypatch.setenv(k, v)
    vet = _client("u-fr04-vet", T_A, "veterinarian")
    clinic = _client("u-fr04-admin", T_A, "partner_clinic_admin")
    product = f"{klass.lower()}-04"
    _register(product, klass)
    loc = clinic.post("/api/inventory/locations", json={"name": f"Shelf {klass}"}).json()["location_id"]
    other = clinic.post("/api/inventory/locations", json={"name": f"Shelf2 {klass}"}).json()["location_id"]
    rx = vet.post("/api/prescriptions", json={"pet_id": "p", "session_id": "s", "medication_name": product,
                                              "dosage": "d", "instructions": "i"}).json()["prescription_id"]
    assert vet.post(f"/api/prescriptions/{rx}/verify").status_code == 200
    move = {"location_id": loc, "product_id": product, "batch": "B"}
    attempts = {
        "register (receipt)": lambda c: c.post("/api/inventory/movements", json={**move, "quantity_delta": 5,
                                                                              "reason": "RECEIPT",
                                                                              "batch_expiry": "2030-01-01"}),
        "wastage (adjustment)": lambda c: c.post("/api/inventory/movements", json={**move, "quantity_delta": -1,
                                                                                "reason": "ADJUSTMENT"}),
        "transfer": lambda c: c.post("/api/inventory/movements", json={**move, "quantity_delta": 1,
                                                                    "reason": "TRANSFER_OUT", "to_location_id": other}),
        "supply without verification": lambda c: c.post("/api/inventory/supplies", json={**move, "quantity": 1}),
        "supply with prescription": lambda c: c.post("/api/inventory/supplies", json={**move, "quantity": 1,
                                                                                    "prescription_id": rx}),
        "dispense": lambda c: c.post(f"/api/prescriptions/{rx}/dispense", json={**move, "quantity": 1}),
    }
    for who in (vet, clinic):
        for name, attempt in attempts.items():
            r = attempt(who)
            assert _disabled(r) or (who is clinic and r.status_code == 403), (name, r.status_code, r.text)
    assert all(_disabled(attempts[n](vet)) for n in attempts), "the veterinarian is refused on every path"
    assert vet.get(f"/api/prescriptions/{rx}").json()["status"] == "VET_VERIFIED"
    assert not api.INVENTORY_REPO.movements(tenant_id=T_A, location_id=loc)
    refused = [e for e in vet.get("/audit/events/tenant", params={"limit": 5000}).json()["events"]
               if e.get("reason_code") == "RESTRICTED_SUBSTANCE_WORKFLOW_DISABLED:EV-11" and e["actor_id"] == "u-fr04-vet"]
    assert len(refused) >= len(attempts) and all(e["action_result"] == "denied" for e in refused)


# --------------------------------------------------------------------------- AC-FR-04-03
def test_supply_class_comes_only_from_registration_and_an_unregistered_medicine_is_pom():
    vet = _client("u-fr04-vet3", T_A, "veterinarian")
    clinic = _client("u-fr04-admin3", T_A, "partner_clinic_admin")
    clinic_b = _client("u-fr04-admin3b", T_B, "partner_clinic_admin")
    loc = clinic.post("/api/inventory/locations", json={"name": "Unclassified"}).json()["location_id"]
    base = {"location_id": loc, "product_id": "mystery-med-04", "batch": "M", "quantity_delta": 5, "reason": "RECEIPT",
            "batch_expiry": "2030-01-01"}
    # No served route sets a class; a body that tries is refused, in any tenant.
    for c in (clinic, clinic_b):
        assert c.post("/api/inventory/movements", json={**base, "supply_class": "GENERAL"}).status_code == 422
    main_src = (ROOT / "petcare_api" / "main.py").read_text("utf-8")
    assert "register_product(" not in main_src
    # Unregistered => POM: tenant staff may not receive it, a vet may, and supply needs a prescription.
    assert clinic.post("/api/inventory/movements", json=base).status_code == 403
    ok = vet.post("/api/inventory/movements", json=base)
    assert ok.status_code == 200 and ok.json()[0]["supply_class"] == "POM"
    r = vet.post("/api/inventory/supplies", json={"location_id": loc, "product_id": "mystery-med-04", "batch": "M",
                                                  "quantity": 1})
    assert r.status_code == 403 and r.json()["detail"]["error"] == "PRESCRIPTION_REQUIRED"
    audit = [e for e in vet.get("/audit/events/tenant", params={"limit": 5000}).json()["events"]
             if e["event_name"] == "inventory.movement.recorded" and e["resource_id"] == ok.json()[0]["movement_id"]]
    assert audit and audit[0]["reason_code"] == "RECEIPT:POM"
    assert not [m for m in api.INVENTORY_REPO.movements(tenant_id=T_B) if m.product_id == "mystery-med-04"]

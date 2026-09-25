"""FR-27 AC-FR-27-02 (dependency COUNSEL:L-2) — the internal part, through the SERVED app (MVC-BUILD-RUNNER-001 U21).

"Actions taken from the dashboard are limited by supply class: GENERAL/OTC actions by a class-scoped actor, POM
dispense by a veterinarian only until counsel." Fails if a non-veterinarian completes a POM dispense from the
dashboard, or an actor acts on a class outside its scope. The dashboard's users are the tenant's clinic
administrators and veterinarians. The class-scoped pharmacy actor itself awaits counsel (L-2) and is not evidenced.
"""
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
T = "t-fr27-scope"


def _client(user_id, role):
    ensure_tenant(T)
    auth.seed_user(user_id, f"{user_id}@fr27s.test", "pw", role, tenant_id=T)
    if role == "veterinarian":
        grant_practitioner_authority(user_id, T)
    c = TestClient(api.app)
    r = c.post("/api/auth/sign-in", json={"email": f"{user_id}@fr27s.test", "password": "pw"})
    assert r.status_code == 200, r.text
    c.cookies.set("petcare_session", r.cookies["petcare_session"])
    return c


def _register(product, klass):
    if product not in api.INVENTORY_REPO._products:
        api.INVENTORY_REPO.register_product(ProductRegistration(product_id=product, name=product, supply_class=klass,
                                                                source=REGISTRATION_SOURCE,
                                                                registered_at=datetime.now(timezone.utc)))


def _verified_rx(vet, product):
    rx = vet.post("/api/prescriptions", json={"pet_id": "p", "session_id": "s", "medication_name": product,
                                              "dosage": "d", "instructions": "i", "product_id": product}).json()["prescription_id"]
    assert vet.post(f"/api/prescriptions/{rx}/verify").status_code == 200
    return rx


def test_dashboard_actions_are_limited_by_supply_class():
    vet = _client("u-fr27s-vet", "veterinarian")
    dash = _client("u-fr27s-clinic", "partner_clinic_admin")     # the dashboard user who is not a veterinarian
    for p, k in (("pom-27", "POM"), ("res-27", "RESTRICTED"), ("ctl-27", "CONTROLLED"), ("gen-27", "GENERAL")):
        _register(p, k)
    # 1. A non-veterinarian cannot complete a POM dispense from the dashboard — directly or via a supply.
    rx = _verified_rx(vet, "pom-27")
    assert rx in [q["prescription_id"] for q in dash.get("/api/prescriptions/queue/awaiting-dispense").json()]
    origin = stock_origin(T, product_id="pom-27", batch="P1")
    assert dash.post(f"/api/prescriptions/{rx}/dispense", json=origin).status_code == 403
    assert dash.post("/api/inventory/supplies", json={**{k: origin[k] for k in ("location_id", "product_id", "batch")},
                                                      "quantity": 1, "prescription_id": rx}).status_code == 403
    assert vet.get(f"/api/prescriptions/{rx}").json()["status"] == "VET_VERIFIED"
    # 2. No actor acts on a class outside its scope: RESTRICTED/CONTROLLED are outside every actor's scope today.
    for product in ("res-27", "ctl-27"):
        rx2 = _verified_rx(vet, product)
        for who in (dash, vet):
            r = who.post(f"/api/prescriptions/{rx2}/dispense", json={**origin, "product_id": product})
            assert r.status_code == 403, (product, r.text)
    # 3. GENERAL/OTC actions remain open to dashboard staff (the scope they hold).
    loc = dash.post("/api/inventory/locations", json={"name": "Dashboard shelf"}).json()["location_id"]
    assert dash.post("/api/inventory/movements", json={"location_id": loc, "product_id": "gen-27", "batch": "G",
                                                       "quantity_delta": 5, "reason": "RECEIPT",
                                                       "batch_expiry": "2030-01-01"}).status_code == 200
    assert dash.post("/api/inventory/supplies", json={"location_id": loc, "product_id": "gen-27", "batch": "G",
                                                      "quantity": 1}).status_code == 200
    # Every refusal is audited under the actor who attempted it.
    ev = dash.get("/audit/events/tenant", params={"limit": 5000}).json()["events"]
    denied = [e for e in ev if e["action_result"] == "denied" and e["event_name"] in
              ("prescription.dispense_denied", "inventory.supply.refused")]
    assert {e["actor_id"] for e in denied} >= {"u-fr27s-clinic", "u-fr27s-vet"}
    assert any(e["actor_id"] == "u-fr27s-clinic" and e["resource_id"] == rx for e in denied)

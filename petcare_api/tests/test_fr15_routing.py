"""FR-15 smart order routing — ratified AC-FR-15-01/04 through the SERVED app (MVC-BUILD-RUNNER-001 U18).

AC-FR-15-01 (dependency COUNSEL:MVC-PHARM-001 §6c): the ratified text says step 1 (licensed for the supply class)
is evidenced with TEST FIXTURES until establishment licences are defined — the licence register is written here
at the repository layer, never by a served route. ETA/distance come from a maps CONTRACT DOUBLE installed
in-process: maps availability (AC-FR-15-02/03, EXTERNAL:MAPS_API) is separately evidenced and not claimed.
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
from tenant_fixtures import ensure_tenant  # noqa: E402

pytestmark = pytest.mark.served_app
T_A, T_B = "t-fr15-alpha", "t-fr15-beta"
OWNER_AT = {"latitude": 24.7136, "longitude": 46.6753}


def _client(user_id, tenant, role):
    ensure_tenant(tenant)
    auth.seed_user(user_id, f"{user_id}@fr15.test", "pw", role, tenant_id=tenant)
    c = TestClient(api.app)
    r = c.post("/api/auth/sign-in", json={"email": f"{user_id}@fr15.test", "password": "pw"})
    assert r.status_code == 200, r.text
    c.cookies.set("petcare_session", r.cookies["petcare_session"])
    return c


def _register(product_id):
    if product_id not in api.INVENTORY_REPO._products:
        api.INVENTORY_REPO.register_product(ProductRegistration(product_id=product_id, name=product_id,
                                                                supply_class="GENERAL", source=REGISTRATION_SOURCE,
                                                                registered_at=datetime.now(timezone.utc)))


class _MapsDouble:
    """Contract double: (eta_seconds, distance_metres) per destination; records that the owner's origin was used."""

    def __init__(self, table):
        self.table, self.origins = table, []

    def route(self, *, origin, destination):
        self.origins.append(origin)
        return self.table[destination]


def _pharmacy(admin, name, lat, lng, *, licensed=True, stock=None):
    loc = admin.post("/api/inventory/locations", json={"name": name, "latitude": lat, "longitude": lng}).json()["location_id"]
    if licensed:
        api.ROUTING_REPO.license(loc, "GENERAL")  # fixture: MVC-PHARM-001 §6c undefined
    for product, qty in (stock or {}).items():
        _register(product)  # GENERAL: an unregistered product would be POM, which a clinic admin may not receive
        r = admin.post("/api/inventory/movements", json={"location_id": loc, "product_id": product, "batch": "R1",
                                                         "quantity_delta": qty, "reason": "RECEIPT",
                                                         "batch_expiry": "2030-01-01"})
        assert r.status_code == 200, r.text
    return loc


def _order(owner, admin, lines):
    for p in lines:
        _register(p)
        admin.post("/api/catalog/prices", json={"product_id": p, "unit_price_halalas": 1000})
    r = owner.post("/api/orders", json={"lines": [{"product_id": p, "quantity": q} for p, q in lines.items()],
                                        "payment_method": "COD"})
    assert r.status_code == 200, r.text
    return r.json()["order_id"]


# --------------------------------------------------------------------------- AC-FR-15-01
def test_an_order_is_routed_by_licence_then_basket_then_eta_then_distance_then_id(monkeypatch):
    admin = _client("u-fr15-admin", T_A, "partner_clinic_admin")
    owner = _client("u-fr15-owner", T_A, "owner")
    admin_b = _client("u-fr15-admin-b", T_B, "partner_clinic_admin")
    basket = {"food-15": 2, "toy-15": 1}
    unlicensed = _pharmacy(admin, "Unlicensed (nearest)", 24.71, 46.67, licensed=False, stock={"food-15": 9, "toy-15": 9})
    partial = _pharmacy(admin, "Partial basket", 24.72, 46.68, stock={"food-15": 9})
    slow = _pharmacy(admin, "Slower", 24.73, 46.69, stock={"food-15": 9, "toy-15": 9})
    far_tie = _pharmacy(admin, "Same ETA, farther", 24.74, 46.70, stock={"food-15": 9, "toy-15": 9})
    best = _pharmacy(admin, "Same ETA, nearer", 24.75, 46.71, stock={"food-15": 9, "toy-15": 9})
    _pharmacy(admin_b, "Other tenant (fastest)", 24.7136, 46.6753, stock={"food-15": 9, "toy-15": 9})
    table = {(24.71, 46.67): (60, 500), (24.72, 46.68): (120, 900), (24.73, 46.69): (900, 1000),
             (24.74, 46.70): (600, 3000), (24.75, 46.71): (600, 2500), (24.7136, 46.6753): (1, 1)}
    double = _MapsDouble(table)
    monkeypatch.setattr(api, "MAPS_PORT", double)
    oid = _order(owner, admin, basket)
    r = owner.post(f"/api/orders/{oid}/route", json=OWNER_AT)
    assert r.status_code == 200, r.text
    d = r.json()
    assert d["chosen_location_id"] == best and d["chosen_pharmacy"] == "Same ETA, nearer"
    flags = {c["location_id"]: (c["licensed"], c["has_basket"]) for c in d["candidates"]}
    assert flags[unlicensed] == (False, True) and flags[partial] == (True, False) and flags[slow] == (True, True)
    assert far_tie in flags and len(flags) == 5                      # tenant B's pharmacy is never a candidate
    assert set(double.origins) == {(OWNER_AT["latitude"], OWNER_AT["longitude"])}  # the owner's location is used
    # Exact tie on ETA and distance: the stable identifier decides.
    tie = _pharmacy(admin, "Exact tie", 24.76, 46.72, stock={"food-15": 9, "toy-15": 9})
    double.table[(24.76, 46.72)] = (600, 2500)
    again = owner.post(f"/api/orders/{_order(owner, admin, basket)}/route", json=OWNER_AT).json()
    assert again["chosen_location_id"] == min(best, tie)
    assert admin_b.post(f"/api/orders/{oid}/route", json=OWNER_AT).status_code == 404


def test_routing_fails_closed_without_maps_or_without_a_licensed_pharmacy(monkeypatch):
    tenant = "t-fr15-failclosed"  # its own tenant: candidates are the tenant's pharmacies
    admin = _client("u-fr15-admin2", tenant, "partner_clinic_admin")
    owner = _client("u-fr15-owner2", tenant, "owner")
    loc = _pharmacy(admin, "Only", 24.8, 46.8, stock={"food-15b": 5})
    oid = _order(owner, admin, {"food-15b": 1})
    r = owner.post(f"/api/orders/{oid}/route", json=OWNER_AT)            # served default: no maps provider
    assert r.status_code == 503 and r.json()["detail"]["error"] == "ROUTING_UNAVAILABLE"
    monkeypatch.setattr(api, "MAPS_PORT", _MapsDouble({(24.8, 46.8): (100, 100)}))
    monkeypatch.setattr(api.ROUTING_REPO, "_licences", set())            # production today: nobody is licensed
    r = owner.post(f"/api/orders/{oid}/route", json=OWNER_AT)
    assert r.status_code == 409 and r.json()["detail"]["error"] == "NO_QUALIFYING_PHARMACY"
    assert r.json()["detail"]["decision"]["candidates"][0]["location_id"] == loc


# --------------------------------------------------------------------------- AC-FR-15-04
def test_every_routing_decision_is_recorded_with_its_inputs_and_shown_to_the_owner(monkeypatch):
    tenant = "t-fr15-record"  # its own tenant: candidates are the tenant's pharmacies
    admin = _client("u-fr15-admin3", tenant, "partner_clinic_admin")
    owner = _client("u-fr15-owner3", tenant, "owner")
    stranger = _client("u-fr15-owner3x", tenant, "owner")
    a = _pharmacy(admin, "North", 24.9, 46.9, stock={"food-15c": 5})
    b = _pharmacy(admin, "South", 24.1, 46.1, stock={"food-15c": 5})
    monkeypatch.setattr(api, "MAPS_PORT", _MapsDouble({(24.9, 46.9): (300, 2000), (24.1, 46.1): (200, 3000)}))
    oid = _order(owner, admin, {"food-15c": 1})
    d = owner.post(f"/api/orders/{oid}/route", json=OWNER_AT).json()
    seen = owner.get(f"/api/orders/{oid}/routing").json()
    assert seen["decision_id"] == d["decision_id"] and seen["chosen_pharmacy"] == "South"
    assert seen["owner_location"] == OWNER_AT and seen["rule_version"].startswith("OPTIMAL_ROUTING_RULE")
    assert {c["location_id"]: (c["eta_seconds"], c["distance_metres"]) for c in seen["candidates"]} == {a: (300, 2000),
                                                                                                        b: (200, 3000)}
    assert [o["fulfilled_by"]["name"] for o in owner.get("/api/orders").json() if o["order_id"] == oid] == ["South"]
    assert stranger.get(f"/api/orders/{oid}/routing").status_code == 404
    audited = [e for e in owner.get("/audit/events/tenant", params={"limit": 5000}).json()["events"]
               if e["event_name"] == "order.routed" and e["resource_id"] == d["decision_id"]]
    assert len(audited) == 1 and audited[0]["actor_id"] == "u-fr15-owner3" and f"chosen:{b}" in audited[0]["reason_code"]
    # Delivery must come from the routed pharmacy.
    wrong = admin.post(f"/api/orders/{oid}/deliver", json={"location_id": a, "batches": {"food-15c": "R1"},
                                                           "collected_amount_halalas": 1000, "collection_reference": "C"})
    assert wrong.status_code == 409 and wrong.json()["detail"]["error"] == "NOT_THE_ROUTED_PHARMACY"

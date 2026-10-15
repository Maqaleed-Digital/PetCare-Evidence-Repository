"""MVC-EPC-D-001 D2n — J-O9 internal order tracking (R19.5 item 4; R18.4). Every order view carries `tracking`: the lifecycle
PLACED -> ROUTED -> DELIVERED -> RECEIPT_ISSUED derived ONLY from the platform's own records (order, FR-15 routing decision,
FR-20 collection, receipt). `carrier` is always None: no carrier reading, ETA or courier status exists or is invented
(EXTERNAL:LOGISTICS_PARTNER). ROUTED needs the maps provider (EXTERNAL:MAPS_API): proven here with the FR-15 maps CONTRACT
DOUBLE, and shown to stay not-done (fail closed) with the served app's unavailable adapter."""
import os
import sys
import uuid
from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import main as api  # noqa: E402
from establishment_fixtures import licensed_location  # noqa: E402
from inventory import REGISTRATION_SOURCE, ProductRegistration  # noqa: E402
from routers import auth  # noqa: E402
from tenant_fixtures import ensure_tenant  # noqa: E402

pytestmark = pytest.mark.served_app
PRODUCT = "shampoo-jo9"
OWNER_AT = {"latitude": 24.7136, "longitude": 46.6753}
STEPS = ["PLACED", "ROUTED", "DELIVERED", "RECEIPT_ISSUED"]


def _client(user_id, tenant, role):
    ensure_tenant(tenant)
    auth.seed_user(user_id, f"{user_id}@jo9.test", "pw", role, tenant_id=tenant)
    c = TestClient(api.app)
    r = c.post("/api/auth/sign-in", json={"email": f"{user_id}@jo9.test", "password": "pw"})
    assert r.status_code == 200, r.text
    c.cookies.set("petcare_session", r.cookies["petcare_session"])
    return c


class _MapsDouble:
    """The FR-15 contract double (EXTERNAL:MAPS_API is not claimed): a fixed ETA/distance for any destination."""

    def route(self, *, origin, destination):
        return 600, 2500


@pytest.fixture()
def w():
    tag = uuid.uuid4().hex[:6]
    t = f"t-d2n-jo9-{tag}"
    w = {"admin": _client(f"u-jo9-adm-{tag}", t, "partner_clinic_admin"), "owner": _client(f"u-jo9-own-{tag}", t, "owner"),
         "other": _client(f"u-jo9-oth-{tag}", t, "owner")}
    if PRODUCT not in api.INVENTORY_REPO._products:
        api.INVENTORY_REPO.register_product(ProductRegistration(product_id=PRODUCT, name="شامبو", supply_class="GENERAL",
                                                                source=REGISTRATION_SOURCE, registered_at=datetime.now(timezone.utc)))
    assert w["admin"].post("/api/catalog/prices", json={"product_id": PRODUCT, "unit_price_halalas": 1000}).status_code == 200
    w["loc"] = w["admin"].post("/api/inventory/locations", json={"name": f"Pharmacy {tag}", "latitude": 24.70,
                                                                 "longitude": 46.68}).json()["location_id"]
    api.ROUTING_REPO.license(w["loc"], "GENERAL")                     # FR-15 routing fixture, as in test_fr15_routing.py
    assert w["admin"].post("/api/inventory/movements", json={"location_id": w["loc"], "product_id": PRODUCT, "batch": "J9",
                                                             "quantity_delta": 20, "reason": "RECEIPT",
                                                             "batch_expiry": "2032-06-30"}).status_code == 200
    licensed_location(w["admin"], w["loc"])                           # X-30 establishment licence (R19.2 record)
    return w


def _order(w):
    r = w["owner"].post("/api/orders", json={"payment_method": "COD", "lines": [{"product_id": PRODUCT, "quantity": 1}]})
    assert r.status_code == 200, r.text
    return r.json()


def _view(w, order_id, who="owner"):
    return next(o for o in w[who].get("/api/orders").json() if o["order_id"] == order_id)


def _done(view):
    return {s["step"]: s["done"] for s in view["tracking"]["steps"]}


def _deliver(w, o):
    return w["admin"].post(f"/api/orders/{o['order_id']}/deliver", json={
        "location_id": w["loc"], "batches": {PRODUCT: "J9"}, "collected_amount_halalas": o["total_halalas"],
        "collection_reference": "COD-JO9"})


def test_a_new_order_is_tracked_as_placed_only_and_claims_no_carrier(w):
    o = _order(w)
    t = o["tracking"]
    assert [s["step"] for s in t["steps"]] == STEPS
    assert _done(o) == {"PLACED": True, "ROUTED": False, "DELIVERED": False, "RECEIPT_ISSUED": False}
    assert t["steps"][0]["at"] == o["created_at"] and all(s["at"] is None for s in t["steps"][1:])
    assert t["carrier"] is None


def test_the_full_internal_lifecycle_placed_routed_delivered_receipt_in_order(w, monkeypatch):
    o = _order(w)
    monkeypatch.setattr(api, "MAPS_PORT", _MapsDouble())
    r = w["owner"].post(f"/api/orders/{o['order_id']}/route", json=OWNER_AT)
    assert r.status_code == 200, r.text
    assert _done(_view(w, o["order_id"])) == {"PLACED": True, "ROUTED": True, "DELIVERED": False, "RECEIPT_ISSUED": False}
    assert _deliver(w, o).status_code == 200
    v = _view(w, o["order_id"])
    assert _done(v) == dict.fromkeys(STEPS, True)
    times = [datetime.fromisoformat(s["at"]) for s in v["tracking"]["steps"]]
    assert times == sorted(times)                                     # each step happened after the one before
    rec = w["owner"].get(f"/api/orders/{o['order_id']}/receipt").json()
    assert v["tracking"]["steps"][3]["at"] == rec["issued_at"]        # derived from the record, not computed
    assert v["tracking"]["carrier"] is None
    assert _view(w, o["order_id"], "admin")["tracking"] == v["tracking"]     # staff see the same lifecycle


def test_with_the_served_maps_adapter_routing_fails_closed_and_routed_stays_not_done(w):
    o = _order(w)
    r = w["owner"].post(f"/api/orders/{o['order_id']}/route", json=OWNER_AT)
    assert r.status_code == 503 and r.json()["detail"]["error"] == "ROUTING_UNAVAILABLE"
    assert _done(_view(w, o["order_id"]))["ROUTED"] is False
    assert _deliver(w, o).status_code == 200                          # an unrouted order still completes; ROUTED stays false
    assert _done(_view(w, o["order_id"])) == {"PLACED": True, "ROUTED": False, "DELIVERED": True, "RECEIPT_ISSUED": True}


def test_a_refused_delivery_moves_no_step(w):
    o = _order(w)
    other = w["admin"].post("/api/inventory/locations", json={"name": "Unlicensed"}).json()["location_id"]
    r = w["admin"].post(f"/api/orders/{o['order_id']}/deliver", json={"location_id": other, "batches": {PRODUCT: "J9"},
                                                                     "collected_amount_halalas": o["total_halalas"],
                                                                     "collection_reference": "COD-X"})
    assert r.status_code == 409
    assert _done(_view(w, o["order_id"])) == {"PLACED": True, "ROUTED": False, "DELIVERED": False, "RECEIPT_ISSUED": False}


def test_an_owner_never_sees_another_owners_tracking(w):
    o = _order(w)
    assert all(x["order_id"] != o["order_id"] for x in w["other"].get("/api/orders").json())

"""FR-20 cash on delivery with digital receipting — ratified AC-FR-20-01/02 through the SERVED app
(MVC-BUILD-RUNNER-001 U14). AC-FR-20-03/04 (EXTERNAL:LOGISTICS_PARTNER): the rule that an order is paid
only with a collection confirmation of its exact total is tested, but the partner's confirmation
interface is not held and no evidence is registered for those criteria."""
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
T_A, T_B = "t-fr20-alpha", "t-fr20-beta"


def _client(user_id, tenant, role):
    ensure_tenant(tenant)
    auth.seed_user(user_id, f"{user_id}@fr20.test", "pw", role, tenant_id=tenant)
    c = TestClient(api.app)
    r = c.post("/api/auth/sign-in", json={"email": f"{user_id}@fr20.test", "password": "pw"})
    assert r.status_code == 200, r.text
    c.cookies.set("petcare_session", r.cookies["petcare_session"])
    return c


def _register(product_id, klass="GENERAL"):
    if product_id not in api.INVENTORY_REPO._products:
        api.INVENTORY_REPO.register_product(ProductRegistration(product_id=product_id, name=product_id, supply_class=klass,
                                                                source=REGISTRATION_SOURCE,
                                                                registered_at=datetime.now(timezone.utc)))


def _shop(admin, product="shampoo-20", price=4550, stock=50):
    _register(product)
    assert admin.post("/api/catalog/prices", json={"product_id": product, "unit_price_halalas": price}).status_code == 200
    loc = admin.post("/api/inventory/locations", json={"name": f"Shop {product}"}).json()["location_id"]
    assert admin.post("/api/inventory/movements", json={"location_id": loc, "product_id": product, "batch": "S1",
                                                        "quantity_delta": stock, "reason": "RECEIPT",
                                                        "batch_expiry": "2030-06-30"}).status_code == 200
    return loc


def _deliver(admin, order, loc, amount=None, ref="COD-REF-1"):
    return admin.post(f"/api/orders/{order['order_id']}/deliver", json={
        "location_id": loc, "batches": {l["product_id"]: "S1" for l in order["lines"]},
        "collected_amount_halalas": order["total_halalas"] if amount is None else amount, "collection_reference": ref})


def _events(c, name):
    return [e for e in c.get("/audit/events/tenant", params={"limit": 5000}).json()["events"] if e["event_name"] == name]


# --------------------------------------------------------------------------- AC-FR-20-01
def test_an_owner_chooses_cash_on_delivery_and_the_order_records_it():
    admin = _client("u-fr20-admin", T_A, "partner_clinic_admin")
    owner = _client("u-fr20-owner", T_A, "owner")
    _shop(admin)
    _register("amoxi-20", "POM")
    admin.post("/api/catalog/prices", json={"product_id": "amoxi-20", "unit_price_halalas": 1000})
    listed = owner.get("/api/catalog/prices").json()
    assert {x["product_id"] for x in listed} >= {"shampoo-20"} and "amoxi-20" not in {x["product_id"] for x in listed}
    r = owner.post("/api/orders", json={"lines": [{"product_id": "shampoo-20", "quantity": 2}], "payment_method": "COD"})
    assert r.status_code == 200, r.text
    o = r.json()
    assert (o["payment_method"], o["status"], o["paid"], o["total_halalas"], o["owner_id"]) == ("COD", "PLACED", False,
                                                                                               9100, "u-fr20-owner")
    mine = [x for x in owner.get("/api/orders").json() if x["order_id"] == o["order_id"]]
    assert mine and mine[0]["payment_method"] == "COD"
    assert owner.post("/api/orders", json={"lines": [{"product_id": "shampoo-20", "quantity": 1, "unit_price_halalas": 1}],
                                           "payment_method": "COD"}).status_code == 422  # no client price
    assert owner.post("/api/orders", json={"lines": [{"product_id": "shampoo-20", "quantity": 1}],
                                           "payment_method": "CARD"}).status_code == 400
    assert owner.post("/api/orders", json={"lines": [{"product_id": "amoxi-20", "quantity": 1}],
                                           "payment_method": "COD"}).status_code == 409
    _register("unpriced-20")  # GENERAL but not priced (an unregistered product is POM: refused 409 above)
    assert owner.post("/api/orders", json={"lines": [{"product_id": "unpriced-20", "quantity": 1}],
                                           "payment_method": "COD"}).status_code == 400
    assert admin.post("/api/orders", json={"lines": [{"product_id": "shampoo-20", "quantity": 1}],
                                           "payment_method": "COD"}).status_code == 403
    assert [e["actor_id"] for e in _events(owner, "order.placed") if e["resource_id"] == o["order_id"]] == ["u-fr20-owner"]


# --------------------------------------------------------------------------- AC-FR-20-02
def test_on_delivery_the_owner_receives_a_receipt_in_their_language_retrievable_later():
    admin = _client("u-fr20-admin2", T_A, "partner_clinic_admin")
    owner_ar = _client("u-fr20-owner-ar", T_A, "owner")
    owner_en = _client("u-fr20-owner-en", T_A, "owner")
    assert owner_en.put("/api/me/preferences/language", json={"language": "en"}).status_code == 200
    loc = _shop(admin, "collar-20", 2500)
    got = {}
    for key, c in (("ar", owner_ar), ("en", owner_en)):
        o = c.post("/api/orders", json={"lines": [{"product_id": "collar-20", "quantity": 1}], "payment_method": "COD"}).json()
        assert c.get(f"/api/orders/{o['order_id']}/receipt").status_code == 404  # none before delivery
        d = _deliver(admin, o, loc, ref=f"CASH-{key}")
        assert d.status_code == 200, d.text
        assert d.json()["status"] == "DELIVERED" and d.json()["paid"] is True
        got[key] = c.get(f"/api/orders/{o['order_id']}/receipt").json()
        assert c.get("/api/orders").json()[-1]["receipt"]["receipt_id"] == got[key]["receipt_id"]
        assert owner_ar.get(f"/api/orders/{o['order_id']}/receipt").status_code == (200 if key == "ar" else 404)
    assert got["ar"]["language"] == "ar" and "إيصال رقمي" in got["ar"]["rendered"] and "25.00" in got["ar"]["rendered"]
    assert got["en"]["language"] == "en" and got["en"]["rendered"].startswith("Digital receipt")
    stock = admin.get("/api/inventory/stock", params={"product_id": "collar-20"}).json()["locations"]
    assert [b["quantity"] for x in stock if x["location_id"] == loc for b in x["stock"]] == [48]
    assert len([e for e in _events(admin, "order.receipt_issued")]) >= 2


# --------------------------------------------------------------------------- AC-FR-20-03 rule (not registered)
def test_an_order_is_never_marked_paid_without_a_confirmation_of_its_exact_total():
    admin = _client("u-fr20-admin3", T_A, "partner_clinic_admin")
    owner = _client("u-fr20-owner3", T_A, "owner")
    admin_b = _client("u-fr20-admin3b", T_B, "partner_clinic_admin")
    loc = _shop(admin, "brush-20", 1200)
    o = owner.post("/api/orders", json={"lines": [{"product_id": "brush-20", "quantity": 3}], "payment_method": "COD"}).json()
    assert _deliver(admin, o, loc, amount=3500).status_code == 409
    assert _deliver(admin, o, loc, ref="  ").status_code == 409
    assert _deliver(admin_b, o, loc).status_code == 404
    assert [x["paid"] for x in owner.get("/api/orders").json() if x["order_id"] == o["order_id"]] == [False]
    assert _deliver(admin, o, loc).status_code == 200
    assert _deliver(admin, o, loc, ref="again").status_code == 409

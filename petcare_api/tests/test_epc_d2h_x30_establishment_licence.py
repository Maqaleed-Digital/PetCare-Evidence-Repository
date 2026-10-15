"""MVC-EPC-D-001 D2h — X-30 (Sponsor ruling R18.3): an order is fulfilled (POST /api/orders/{id}/deliver, the regulated
dispensing act) only when its supplying location holds a licence of the SAME tenant valid on the Asia/Riyadh date of the act.
Absent, expired and wrong-tenant licences are refused (409 ESTABLISHMENT_LICENCE_INVALID), audited, and nothing moves.
Licences are entity data recorded through the governed admin route (R18.2)."""
import os
import sys
import uuid
from datetime import date, datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import establishment_licences as est  # noqa: E402
import main as api  # noqa: E402
from establishment_fixtures import licensed_location  # noqa: E402
from inventory import REGISTRATION_SOURCE, ProductRegistration  # noqa: E402
from ksa_calendar import ksa_date  # noqa: E402
from routers import auth  # noqa: E402
from tenant_fixtures import ensure_tenant  # noqa: E402

pytestmark = pytest.mark.served_app
PRODUCT = "shampoo-x30"


def _client(user_id, tenant, role):
    ensure_tenant(tenant)
    auth.seed_user(user_id, f"{user_id}@x30.test", "pw", role, tenant_id=tenant)
    c = TestClient(api.app)
    r = c.post("/api/auth/sign-in", json={"email": f"{user_id}@x30.test", "password": "pw"})
    assert r.status_code == 200, r.text
    c.cookies.set("petcare_session", r.cookies["petcare_session"])
    return c


@pytest.fixture()
def w():
    tag = uuid.uuid4().hex[:6]
    t = f"t-d2h-x30-{tag}"
    w = {"t": t, "admin": _client(f"u-x30-adm-{tag}", t, "partner_clinic_admin"), "owner": _client(f"u-x30-own-{tag}", t, "owner"),
         "platform": _client(f"u-x30-pa-{tag}", t, "platform_admin")}
    if PRODUCT not in api.INVENTORY_REPO._products:
        api.INVENTORY_REPO.register_product(ProductRegistration(product_id=PRODUCT, name=PRODUCT, supply_class="GENERAL",
                                                                source=REGISTRATION_SOURCE, registered_at=datetime.now(timezone.utc)))
    assert w["admin"].post("/api/catalog/prices", json={"product_id": PRODUCT, "unit_price_halalas": 1000}).status_code == 200
    w["loc"] = w["admin"].post("/api/inventory/locations", json={"name": f"Shop {tag}"}).json()["location_id"]
    assert w["admin"].post("/api/inventory/movements", json={"location_id": w["loc"], "product_id": PRODUCT, "batch": "S1",
                                                             "quantity_delta": 50, "reason": "RECEIPT",
                                                             "batch_expiry": "2032-06-30"}).status_code == 200
    return w


def _order(w):
    r = w["owner"].post("/api/orders", json={"payment_method": "COD", "lines": [{"product_id": PRODUCT, "quantity": 1}]})
    assert r.status_code == 200, r.text
    return r.json()


def _deliver(w, order):
    return w["admin"].post(f"/api/orders/{order['order_id']}/deliver", json={
        "location_id": w["loc"], "batches": {PRODUCT: "S1"}, "collected_amount_halalas": order["total_halalas"],
        "collection_reference": "COD-X30"})


def _refused(r):
    return r.status_code == 409 and r.json()["detail"]["error"] == "ESTABLISHMENT_LICENCE_INVALID"


def _today():
    return ksa_date(datetime.now(timezone.utc))


def test_a_location_with_a_valid_licence_fulfils_the_order(w):
    licensed_location(w["admin"], w["loc"], expires_on=(_today() + timedelta(days=30)).isoformat())
    r = _deliver(w, _order(w))
    assert r.status_code == 200, r.text


def test_a_location_with_no_licence_is_refused_audited_and_nothing_moves(w):
    order = _order(w)
    assert _refused(_deliver(w, order))
    ev = [e for e in w["platform"].get("/audit/events/tenant", params={"limit": 5000}).json()["events"]
          if e["event_name"] == "order.delivery.refused" and e["resource_id"] == order["order_id"]]
    assert [e["reason_code"] for e in ev] == ["ESTABLISHMENT_LICENCE_INVALID"]
    licensed_location(w["admin"], w["loc"])
    assert _deliver(w, order).status_code == 200              # the refused attempt left the order undelivered


def test_an_expired_licence_is_refused(w):
    licensed_location(w["admin"], w["loc"], expires_on=(_today() - timedelta(days=1)).isoformat())
    assert _refused(_deliver(w, _order(w)))


def test_another_tenants_licence_for_the_location_is_refused(w):
    api.ESTABLISHMENT_LICENCE_REPO.record(est.EstablishmentLicence(
        licence_id=str(uuid.uuid4()), tenant_id="t-some-other-tenant", location_id=w["loc"], licence_number="SFDA-EST-X",
        issuing_authority="SFDA", expires_on=date(2099, 12, 31), basis="wrong tenant", recorded_by_actor_id="u-x",
        recorded_at=datetime.now(timezone.utc)))
    assert _refused(_deliver(w, _order(w)))


@pytest.mark.parametrize("cell,instant,allowed", [
    ("D-2359-riyadh", datetime(2031, 3, 10, 20, 59, tzinfo=timezone.utc), True),
    ("D+1-0000-riyadh", datetime(2031, 3, 10, 21, 0, tzinfo=timezone.utc), False),
    ("D+1-0259-riyadh", datetime(2031, 3, 10, 23, 59, tzinfo=timezone.utc), False),
])
def test_the_licence_is_valid_through_its_expiry_day_on_the_riyadh_calendar(w, monkeypatch, cell, instant, allowed):
    licensed_location(w["admin"], w["loc"], expires_on="2031-03-10")
    order = _order(w)
    real = datetime

    class _Pinned(real):
        @classmethod
        def now(cls, tz=None):
            return instant.astimezone(tz) if tz is not None else instant.astimezone().replace(tzinfo=None)

    monkeypatch.setattr(api, "datetime", _Pinned)
    r = _deliver(w, order)
    assert (r.status_code == 200) if allowed else _refused(r), (cell, r.status_code, r.text)


def test_only_a_platform_administrator_records_a_licence_for_a_location_of_its_tenant(w):
    body = {"location_id": w["loc"], "licence_number": "N", "issuing_authority": "SFDA", "expires_on": "2099-12-31", "basis": "seen"}
    assert w["admin"].post("/api/admin/establishment-licences", json=body).status_code == 403
    assert w["platform"].post("/api/admin/establishment-licences", json={**body, "location_id": "no-such"}).status_code == 404
    assert w["platform"].post("/api/admin/establishment-licences", json={**body, "basis": "  "}).status_code == 400
    assert w["platform"].post("/api/admin/establishment-licences", json={**body, "expires_on": "31/12/2099"}).status_code == 400
    ok = w["platform"].post("/api/admin/establishment-licences", json=body)
    assert ok.status_code == 201 and ok.json()["location_id"] == w["loc"]
    assert [l["licence_id"] for l in w["platform"].get("/api/admin/establishment-licences").json()] == [ok.json()["licence_id"]]

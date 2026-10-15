"""MVC-EPC-D-001 D2k — Sponsor ruling R19.2 (licence record completeness) on the served app.

The record supports licence type/scope (X-31), issuer and licence number, an evidence-document reference (X-32), recorded-by and
recorded-at audit, and more than one licence per location. A licence missing an R19.2 field never validates a delivery; with no
complete licence valid on the Asia/Riyadh calendar date the order is refused (R19.1). R19.3: the read model never claims
registry verification (X-33 is an external dependency)."""
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
from inventory import REGISTRATION_SOURCE, ProductRegistration  # noqa: E402
from ksa_calendar import ksa_date  # noqa: E402
from repositories import RepositoryDenied  # noqa: E402
from routers import auth  # noqa: E402
from tenant_fixtures import ensure_tenant  # noqa: E402

pytestmark = pytest.mark.served_app
PRODUCT = "shampoo-r19-2"
ROUTE = "/api/admin/establishment-licences"


def _client(user_id, tenant, role):
    ensure_tenant(tenant)
    auth.seed_user(user_id, f"{user_id}@r192.test", "pw", role, tenant_id=tenant)
    c = TestClient(api.app)
    r = c.post("/api/auth/sign-in", json={"email": f"{user_id}@r192.test", "password": "pw"})
    assert r.status_code == 200, r.text
    c.cookies.set("petcare_session", r.cookies["petcare_session"])
    return c


@pytest.fixture()
def w():
    tag = uuid.uuid4().hex[:6]
    t = f"t-d2k-r192-{tag}"
    w = {"t": t, "admin": _client(f"u-r192-adm-{tag}", t, "partner_clinic_admin"),
         "owner": _client(f"u-r192-own-{tag}", t, "owner"), "pa_id": f"u-r192-pa-{tag}"}
    w["platform"] = _client(w["pa_id"], t, "platform_admin")
    if PRODUCT not in api.INVENTORY_REPO._products:
        api.INVENTORY_REPO.register_product(ProductRegistration(product_id=PRODUCT, name=PRODUCT, supply_class="GENERAL",
                                                                source=REGISTRATION_SOURCE, registered_at=datetime.now(timezone.utc)))
    assert w["admin"].post("/api/catalog/prices", json={"product_id": PRODUCT, "unit_price_halalas": 1000}).status_code == 200
    w["loc"] = w["admin"].post("/api/inventory/locations", json={"name": f"Shop {tag}"}).json()["location_id"]
    assert w["admin"].post("/api/inventory/movements", json={"location_id": w["loc"], "product_id": PRODUCT, "batch": "S1",
                                                             "quantity_delta": 50, "reason": "RECEIPT",
                                                             "batch_expiry": "2032-06-30"}).status_code == 200
    return w


def _today():
    return ksa_date(datetime.now(timezone.utc))


def _body(w, **over):
    return {"location_id": w["loc"], "licence_number": f"SFDA-EST-{uuid.uuid4().hex[:6]}", "issuing_authority": "SFDA",
            "expires_on": (_today() + timedelta(days=30)).isoformat(), "basis": "certificate sighted (test entity data)",
            "licence_type": "PHARMACY_ESTABLISHMENT", "scope": "veterinary medicines retail supply",
            "evidence_document_ref": "DOC-TEST-0001", **over}


def _order(w):
    r = w["owner"].post("/api/orders", json={"payment_method": "COD", "lines": [{"product_id": PRODUCT, "quantity": 1}]})
    assert r.status_code == 200, r.text
    return r.json()


def _deliver(w, order=None):
    o = order or _order(w)
    return w["admin"].post(f"/api/orders/{o['order_id']}/deliver", json={
        "location_id": w["loc"], "batches": {PRODUCT: "S1"}, "collected_amount_halalas": o["total_halalas"],
        "collection_reference": "COD-R192"})


def _refused(r):
    return r.status_code == 409 and r.json()["detail"]["error"] == "ESTABLISHMENT_LICENCE_INVALID"


def test_the_record_carries_every_r19_2_field_and_its_audit(w):
    before = datetime.now(timezone.utc)
    r = w["platform"].post(ROUTE, json=_body(w))
    assert r.status_code == 201, r.text
    lic = r.json()
    assert lic["licence_type"] == "PHARMACY_ESTABLISHMENT" and lic["scope"] == "veterinary medicines retail supply"   # X-31
    assert lic["issuing_authority"] == "SFDA" and lic["licence_number"].startswith("SFDA-EST-")                     # issuer, number
    assert lic["evidence_document_ref"] == "DOC-TEST-0001"                                                          # X-32
    assert lic["recorded_by_actor_id"] == w["pa_id"] and datetime.fromisoformat(lic["recorded_at"]) >= before       # audit fields
    assert lic["complete"] is True and lic["registry_verified"] is False                                            # R19.3
    ev = [e for e in w["platform"].get("/audit/events/tenant", params={"limit": 5000}).json()["events"]
          if e["event_name"] == "establishment.licence.recorded" and e["resource_id"] == lic["licence_id"]]
    assert len(ev) == 1 and ev[0]["actor_id"] == w["pa_id"]


@pytest.mark.parametrize("field", ["licence_type", "scope", "evidence_document_ref"])
def test_each_r19_2_field_is_required_and_may_not_be_blank(w, field):
    missing = {k: v for k, v in _body(w).items() if k != field}
    assert w["platform"].post(ROUTE, json=missing).status_code == 422
    assert w["platform"].post(ROUTE, json=_body(w, **{field: "   "})).status_code == 400
    assert w["platform"].post(ROUTE, json=_body(w, **{field: "x" * 201})).status_code == 400
    assert [l for l in w["platform"].get(ROUTE).json() if l["location_id"] == w["loc"]] == []     # nothing was recorded


def test_a_location_holds_more_than_one_licence_and_any_valid_one_suffices(w):
    old = w["platform"].post(ROUTE, json=_body(w, expires_on=(_today() - timedelta(days=1)).isoformat()))
    new = w["platform"].post(ROUTE, json=_body(w, licence_type="VETERINARY_MEDICINES_STORE", scope="cold-chain storage"))
    assert old.status_code == new.status_code == 201
    listed = [l for l in w["platform"].get(ROUTE).json() if l["location_id"] == w["loc"]]
    assert sorted(l["licence_id"] for l in listed) == sorted([old.json()["licence_id"], new.json()["licence_id"]])
    assert _deliver(w).status_code == 200                              # the expired one does not block; the valid one admits


def test_with_several_licences_none_valid_on_the_riyadh_date_the_order_is_refused(w):
    for days in (1, 40):
        assert w["platform"].post(ROUTE, json=_body(w, expires_on=(_today() - timedelta(days=days)).isoformat())).status_code == 201
    assert _refused(_deliver(w))


@pytest.mark.parametrize("cell,instant,allowed", [
    ("D-2359-riyadh", datetime(2031, 3, 10, 20, 59, tzinfo=timezone.utc), True),
    ("D+1-0000-riyadh", datetime(2031, 3, 10, 21, 0, tzinfo=timezone.utc), False),
    ("D+1-0259-riyadh", datetime(2031, 3, 10, 23, 59, tzinfo=timezone.utc), False),
])
def test_two_licences_the_later_expiry_governs_on_the_riyadh_calendar(w, monkeypatch, cell, instant, allowed):
    assert w["platform"].post(ROUTE, json=_body(w, expires_on="2031-03-09")).status_code == 201
    assert w["platform"].post(ROUTE, json=_body(w, expires_on="2031-03-10")).status_code == 201
    order = _order(w)
    real = datetime

    class _Pinned(real):
        @classmethod
        def now(cls, tz=None):
            return instant.astimezone(tz) if tz is not None else instant.astimezone().replace(tzinfo=None)

    monkeypatch.setattr(api, "datetime", _Pinned)
    r = _deliver(w, order)
    assert (r.status_code == 200) if allowed else _refused(r), (cell, r.status_code, r.text)


def test_an_incomplete_licence_never_validates_a_delivery(w):
    """A row lacking an R19.2 field (the shape of a row recorded before migration 0061) is readable but fails closed, and the
    governed record path refuses to store one."""
    legacy = est.EstablishmentLicence(licence_id=str(uuid.uuid4()), tenant_id=w["t"], location_id=w["loc"],
                                      licence_number="SFDA-LEGACY", issuing_authority="SFDA", expires_on=date(2099, 12, 31),
                                      basis="pre-0061 row", recorded_by_actor_id="u-x", recorded_at=datetime.now(timezone.utc))
    assert not legacy.is_complete() and est.valid_on([legacy], _today()) is None
    with pytest.raises(RepositoryDenied):
        api.ESTABLISHMENT_LICENCE_REPO.record(legacy)
    api.ESTABLISHMENT_LICENCE_REPO._rows[legacy.licence_id] = legacy          # as a pre-0061 row would be read back
    listed = [l for l in w["platform"].get(ROUTE).json() if l["licence_id"] == legacy.licence_id]
    assert listed and listed[0]["complete"] is False
    assert _refused(_deliver(w))

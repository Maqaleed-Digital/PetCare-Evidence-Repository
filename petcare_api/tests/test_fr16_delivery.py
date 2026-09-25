"""FR-16 temperature-controlled delivery tracking — ratified AC-FR-16-01/04 through the SERVED app
(MVC-BUILD-RUNNER-001 U12). AC-FR-16-02/03 (EXTERNAL:LOGISTICS_PARTNER): the adapter boundary's
refusals are exercised, but the partner's interface contract is not held and nothing is registered."""
import os
import sys
from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import main as api  # noqa: E402
from inventory import REGISTRATION_SOURCE, ProductRegistration  # noqa: E402
from routers import auth  # noqa: E402
from tenant_fixtures import ensure_tenant  # noqa: E402

pytestmark = pytest.mark.served_app
T_A, T_B = "t-fr16-alpha", "t-fr16-beta"


def _client(user_id, tenant, role):
    ensure_tenant(tenant)
    auth.seed_user(user_id, f"{user_id}@fr16.test", "pw", role, tenant_id=tenant)
    c = TestClient(api.app)
    r = c.post("/api/auth/sign-in", json={"email": f"{user_id}@fr16.test", "password": "pw"})
    assert r.status_code == 200, r.text
    c.cookies.set("petcare_session", r.cookies["petcare_session"])
    return c


def _register(product_id, lo=None, hi=None):
    """Stands in for the registration feed (BRD P393 storage requirement). No served route does this."""
    if product_id not in api.INVENTORY_REPO._products:  # served tests run in memory mode
        api.INVENTORY_REPO.register_product(ProductRegistration(
            product_id=product_id, name=product_id, supply_class="GENERAL", source=REGISTRATION_SOURCE,
            registered_at=datetime.now(timezone.utc), storage_min_c=lo, storage_max_c=hi))


def _ts(minutes=0):
    return (datetime.now(timezone.utc) + timedelta(minutes=minutes)).isoformat()


def _events(c, name):
    return [e for e in c.get("/audit/events/tenant", params={"limit": 5000}).json()["events"] if e["event_name"] == name]


# --------------------------------------------------------------------------- AC-FR-16-01
def test_a_cold_chain_delivery_carries_a_temperature_log_the_owner_sees():
    staff = _client("u-fr16-admin", T_A, "partner_clinic_admin")
    owner = _client("u-fr16-owner", T_A, "owner")
    stranger = _client("u-fr16-owner-x", T_A, "owner")
    _register("vaccine-cold", 2.0, 8.0)
    d = staff.post("/api/deliveries", json={"owner_id": "u-fr16-owner", "product_id": "vaccine-cold"}).json()
    assert d["cold_chain"] is True and (d["temp_min_c"], d["temp_max_c"]) == (2.0, 8.0)
    did = d["delivery_id"]
    assert staff.post(f"/api/deliveries/{did}/complete").status_code == 409  # no log yet
    for m, c in ((0, 4.1), (10, 5.0)):
        assert staff.post(f"/api/deliveries/{did}/readings", json={"recorded_at": _ts(m), "celsius": c}).status_code == 200
    assert staff.post(f"/api/deliveries/{did}/complete").json()["status"] == "DELIVERED"
    seen = [x for x in owner.get("/api/deliveries").json() if x["delivery_id"] == did]
    assert len(seen) == 1 and [r["celsius"] for r in seen[0]["temperature_log"]] == [4.1, 5.0]
    assert owner.get(f"/api/deliveries/{did}").status_code == 200
    assert stranger.get(f"/api/deliveries/{did}").status_code == 404
    assert did not in [x["delivery_id"] for x in stranger.get("/api/deliveries").json()]
    assert owner.post(f"/api/deliveries/{did}/readings", json={"recorded_at": _ts(), "celsius": 3}).status_code == 403


def test_an_ambient_delivery_needs_no_temperature_log():
    staff = _client("u-fr16-admin2", T_A, "partner_clinic_admin")
    _client("u-fr16-owner2", T_A, "owner")
    _register("collar-ambient")
    d = staff.post("/api/deliveries", json={"owner_id": "u-fr16-owner2", "product_id": "collar-ambient"}).json()
    assert d["cold_chain"] is False
    assert staff.post(f"/api/deliveries/{d['delivery_id']}/complete").status_code == 200


# --------------------------------------------------------------------------- AC-FR-16-04
def test_an_out_of_range_reading_raises_an_audited_alert_to_the_pharmacy_only():
    staff = _client("u-fr16-admin3", T_A, "partner_clinic_admin")
    vet = _client("u-fr16-vet3", T_A, "veterinarian")
    _client("u-fr16-owner3", T_A, "owner")
    staff_b = _client("u-fr16-admin3b", T_B, "partner_clinic_admin")
    _register("insulin-cold", 2.0, 8.0)
    did = staff.post("/api/deliveries", json={"owner_id": "u-fr16-owner3", "product_id": "insulin-cold"}).json()["delivery_id"]
    ok = staff.post(f"/api/deliveries/{did}/readings", json={"recorded_at": _ts(), "celsius": 6.5}).json()
    assert ok["alert_raised"] is False
    hot = staff.post(f"/api/deliveries/{did}/readings", json={"recorded_at": _ts(5), "celsius": 11.2}).json()
    assert hot["alert_raised"] is True
    assert [r["out_of_range"] for r in hot["temperature_log"]] == [False, True]  # kept, never dropped
    alerts = [a for a in vet.get("/api/deliveries/alerts").json() if a["delivery_id"] == did]
    assert len(alerts) == 1 and alerts[0]["kind"] == "TEMPERATURE_OUT_OF_RANGE"
    audited = [e for e in _events(staff, "delivery.temperature.alert") if e["resource_id"] == alerts[0]["alert_id"]]
    assert len(audited) == 1 and audited[0]["actor_id"] == "u-fr16-admin3" and "11.2C" in audited[0]["reason_code"]
    assert did not in [a["delivery_id"] for a in staff_b.get("/api/deliveries/alerts").json()]
    assert staff_b.get(f"/api/deliveries/{did}").status_code == 404
    assert staff_b.post(f"/api/deliveries/{did}/readings", json={"recorded_at": _ts(), "celsius": 20}).status_code == 404


# --------------------------------------------------------------------------- AC-FR-16-02 (adapter boundary; not evidence)
@pytest.mark.parametrize("body", [{"celsius": 4.0}, {"recorded_at": "2026-09-25T10:00:00Z"},
                                  {"recorded_at": "2026-09-25T10:00:00", "celsius": 4.0},
                                  {"recorded_at": "not a time", "celsius": 4.0}])
def test_a_reading_without_a_timestamp_or_value_is_refused(body):
    staff = _client("u-fr16-admin4", T_A, "partner_clinic_admin")
    _client("u-fr16-owner4", T_A, "owner")
    _register("serum-cold", 2.0, 8.0)
    did = staff.post("/api/deliveries", json={"owner_id": "u-fr16-owner4", "product_id": "serum-cold"}).json()["delivery_id"]
    assert staff.post(f"/api/deliveries/{did}/readings", json=body).status_code == 400

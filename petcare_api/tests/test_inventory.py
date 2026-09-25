"""FR-13 real-time multi-location inventory — ratified AC-FR-13-01/02/04 through the SERVED app
(MVC-BUILD-RUNNER-001 U8).

AC-FR-13-01 (ACCEPT_WITH_THRESHOLD, REAL_TIME_BOUND = 5 s): stock is visible per location for
every location of the tenant; a committed change at location A reaches another authorised
session of the same tenant with p95 <= 5 s over at least 100 events; another tenant never sees
it. The UI re-reads the served stock every INVENTORY_REFRESH_MS (petcare_web/lib/inventory.ts),
so the asserted bound is p95(server visibility latency) + INVENTORY_REFRESH_MS <= 5 s.
AC-FR-13-02: an immutable movement ledger with a derived balance; every movement is audited
with the SESSION actor.
AC-FR-13-04 (MVC-PHARM-001 §5; dependency COUNSEL:L-2 — the dependency itself is not evidenced
here): a non-veterinarian cannot move or adjust POM/RESTRICTED/CONTROLLED stock.
"""
import os
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import main as api  # noqa: E402
from inventory import REGISTRATION_SOURCE, ProductRegistration  # noqa: E402
from routers import auth  # noqa: E402
from tenant_fixtures import ensure_tenant, grant_practitioner_authority  # noqa: E402

pytestmark = pytest.mark.served_app
T_A, T_B = "t-inv-alpha", "t-inv-beta"
EVENTS = 100
BOUND_S = 5.0
REFRESH = Path(__file__).resolve().parents[2] / "petcare_web" / "lib" / "inventory.ts"


def _refresh_seconds() -> float:
    m = re.search(r"INVENTORY_REFRESH_MS\s*=\s*(\d+)", REFRESH.read_text(encoding="utf-8"))
    assert m, "INVENTORY_REFRESH_MS not found"
    return int(m.group(1)) / 1000.0


def _client(user_id: str, tenant: str, role: str, *, authority: bool = True) -> TestClient:
    ensure_tenant(tenant)
    auth.seed_user(user_id, f"{user_id}@inv.test", "pw", role, tenant_id=tenant)
    if role == "veterinarian" and authority:
        grant_practitioner_authority(user_id, tenant)
    c = TestClient(api.app)
    r = c.post("/api/auth/sign-in", json={"email": f"{user_id}@inv.test", "password": "pw"})
    assert r.status_code == 200, r.text
    c.cookies.set("petcare_session", r.cookies["petcare_session"])
    return c


def _register(product_id: str, supply_class: str) -> None:
    """Stands in for the SFDA registration feed (AC-FR-04-03). No served route can do this."""
    if api.INVENTORY_REPO.supply_class_of(product_id) == supply_class:
        return
    api.INVENTORY_REPO.register_product(ProductRegistration(
        product_id=product_id, name=product_id, supply_class=supply_class, source=REGISTRATION_SOURCE,
        registered_at=datetime.now(timezone.utc)))


def _location(admin: TestClient, name: str) -> str:
    r = admin.post("/api/inventory/locations", json={"name": name})
    assert r.status_code == 200, r.text
    return r.json()["location_id"]


def _move(c: TestClient, **body):
    return c.post("/api/inventory/movements", json=body)


def _stock(c: TestClient, location_id: str, product_id: str) -> int:
    r = c.get("/api/inventory/stock")
    assert r.status_code == 200, r.text
    loc = next(x for x in r.json()["locations"] if x["location_id"] == location_id)
    return sum(b["quantity"] for b in loc["stock"] if b["product_id"] == product_id)


def _events(c: TestClient, name: str) -> list:
    r = c.get("/audit/events/tenant", params={"limit": 5000})
    assert r.status_code == 200, r.text
    return [e for e in r.json()["events"] if e["event_name"] == name]


# --------------------------------------------------------------------------- AC-FR-13-01
def test_stock_is_visible_per_location_for_every_location_of_the_tenant():
    admin = _client("u-inv-admin-1", T_A, "partner_clinic_admin")
    vet = _client("u-inv-vet-1", T_A, "veterinarian")
    _register("gauze-01", "GENERAL")
    north, south = _location(admin, "Riyadh North"), _location(admin, "Riyadh South")
    assert _move(admin, location_id=north, product_id="gauze-01", batch="B1", quantity_delta=40,
                 reason="RECEIPT").status_code == 200
    assert _move(admin, location_id=north, product_id="gauze-01", batch="B1", quantity_delta=15,
                 reason="TRANSFER_OUT", to_location_id=south).status_code == 200
    # Another authorised user of the tenant sees both locations and the stock at each.
    ids = {x["location_id"] for x in vet.get("/api/inventory/stock").json()["locations"]}
    assert {north, south} <= ids
    assert (_stock(vet, north, "gauze-01"), _stock(vet, south, "gauze-01")) == (25, 15)
    # The inventory check for one product across locations.
    per_product = vet.get("/api/inventory/stock", params={"product_id": "gauze-01"}).json()
    assert sorted((x["location_id"], [b["quantity"] for b in x["stock"]]) for x in per_product["locations"]
                  if x["location_id"] in (north, south)) == sorted([(north, [25]), (south, [15])])


def test_stock_change_visible_to_another_session_within_bound_p95_over_100_events():
    admin = _client("u-inv-admin-rt", T_A, "partner_clinic_admin")
    viewer = _client("u-inv-vet-rt", T_A, "veterinarian")
    _register("syringe-rt", "OTC")
    loc = _location(admin, "Jeddah Central")
    latencies = []
    for i in range(EVENTS):
        assert _move(admin, location_id=loc, product_id="syringe-rt", batch="RT", quantity_delta=1,
                     reason="RECEIPT").status_code == 200
        committed = time.perf_counter()
        deadline = committed + BOUND_S
        while _stock(viewer, loc, "syringe-rt") < i + 1:
            assert time.perf_counter() < deadline, f"event {i} not visible within {BOUND_S}s"
        latencies.append(time.perf_counter() - committed)
    assert len(latencies) >= 100
    s = sorted(latencies)
    p95 = s[max(0, int(round(0.95 * len(s))) - 1)]
    assert p95 + _refresh_seconds() <= BOUND_S, (p95, _refresh_seconds())


def test_another_tenant_never_sees_or_moves_the_tenants_stock():
    admin_a = _client("u-inv-admin-iso", T_A, "partner_clinic_admin")
    admin_b = _client("u-inv-admin-iso-b", T_B, "partner_clinic_admin")
    _register("gauze-iso", "GENERAL")
    loc_a = _location(admin_a, "Dammam")
    assert _move(admin_a, location_id=loc_a, product_id="gauze-iso", batch="I", quantity_delta=9,
                 reason="RECEIPT").status_code == 200
    seen_b = admin_b.get("/api/inventory/stock").json()["locations"]
    assert loc_a not in {x["location_id"] for x in seen_b}
    assert all(b["product_id"] != "gauze-iso" for x in seen_b for b in x["stock"])
    assert loc_a not in {x["location_id"] for x in admin_b.get("/api/inventory/locations").json()}
    # Tenant B naming tenant A's location moves nothing.
    assert _move(admin_b, location_id=loc_a, product_id="gauze-iso", batch="I", quantity_delta=-9,
                 reason="ADJUSTMENT").status_code == 400
    assert _stock(admin_a, loc_a, "gauze-iso") == 9


def test_owners_have_no_inventory_surface():
    owner = _client("u-inv-owner", T_A, "owner")
    assert owner.get("/api/inventory/stock").status_code == 403


# --------------------------------------------------------------------------- AC-FR-13-02
def test_every_movement_is_audited_with_the_session_actor_and_client_identity_is_refused():
    admin = _client("u-inv-admin-aud", T_A, "partner_clinic_admin")
    _register("gauze-aud", "GENERAL")
    loc = _location(admin, "Audit Street")
    r = admin.post("/api/inventory/movements", headers={"X-Actor-Id": "u-somebody-else"},
                   json={"location_id": loc, "product_id": "gauze-aud", "batch": "A", "quantity_delta": 3,
                         "reason": "RECEIPT"})
    assert r.status_code == 200, r.text
    mid = r.json()[0]["movement_id"]
    assert r.json()[0]["actor_id"] == "u-inv-admin-aud"
    ev = [e for e in _events(admin, "inventory.movement.recorded") if e["resource_id"] == mid]
    assert len(ev) == 1 and ev[0]["actor_id"] == "u-inv-admin-aud" and ev[0]["tenant_id"] == T_A
    # A body that tries to name the actor, tenant or class is refused outright.
    for extra in ({"actor_id": "u-x"}, {"tenant_id": T_B}, {"supply_class": "GENERAL"}):
        bad = admin.post("/api/inventory/movements", json={"location_id": loc, "product_id": "gauze-aud",
                                                           "batch": "A", "quantity_delta": 1, "reason": "RECEIPT",
                                                           **extra})
        assert bad.status_code == 422, extra


def test_balance_is_reproduced_by_summing_the_movements_and_cannot_go_negative():
    admin = _client("u-inv-admin-sum", T_A, "partner_clinic_admin")
    _register("gauze-sum", "GENERAL")
    loc = _location(admin, "Sum Lane")
    for d, reason in ((20, "RECEIPT"), (-4, "ADJUSTMENT"), (7, "RECEIPT"), (-3, "ADJUSTMENT")):
        assert _move(admin, location_id=loc, product_id="gauze-sum", batch="S", quantity_delta=d,
                     reason=reason).status_code == 200
    ledger = api.INVENTORY_REPO.movements(tenant_id=T_A, location_id=loc)
    assert _stock(admin, loc, "gauze-sum") == sum(m.quantity_delta for m in ledger) == 20
    assert _move(admin, location_id=loc, product_id="gauze-sum", batch="S", quantity_delta=-21,
                 reason="ADJUSTMENT").status_code == 400
    assert _stock(admin, loc, "gauze-sum") == 20


def test_no_code_path_updates_or_deletes_a_movement():
    """Static half of AC-FR-13-02 (the database half is the trigger, proven against PostgreSQL)."""
    rx = re.compile(r"(?i)(UPDATE\s+stock_movement|DELETE\s+FROM\s+stock_movement)")
    assert rx.search("DELETE FROM stock_movement WHERE 1=1")  # the probe discriminates
    root = Path(__file__).resolve().parents[1]
    hits = [str(p) for p in root.rglob("*.py") if "tests" not in p.parts and rx.search(p.read_text("utf-8"))]
    assert hits == []
    for repo in (type(api.INVENTORY_REPO),):
        assert not [n for n in dir(repo) if re.search(r"update|delete|remove|set_", n)]


# --------------------------------------------------------------------------- AC-FR-13-04
@pytest.mark.parametrize("product,klass", [("amoxi-pom", "POM"), ("keta-res", "RESTRICTED"),
                                           ("bupre-ctl", "CONTROLLED"), ("unregistered-med", None)])
def test_non_veterinarian_cannot_move_or_adjust_veterinarian_only_stock(product, klass):
    admin = _client("u-inv-admin-pharm", T_A, "partner_clinic_admin")
    vet = _client("u-inv-vet-pharm", T_A, "veterinarian")
    lapsed = _client("u-inv-vet-lapsed", T_A, "veterinarian", authority=False)
    if klass:
        _register(product, klass)
    loc = _location(admin, f"Class {product}")
    for c in (admin, lapsed):
        for reason, d in (("RECEIPT", 5), ("ADJUSTMENT", -1)):
            r = _move(c, location_id=loc, product_id=product, batch="P", quantity_delta=d, reason=reason)
            assert r.status_code == 403, (reason, r.text)
    assert _stock(admin, loc, product) == 0
    refused = [e for e in _events(admin, "inventory.movement.refused") if e["resource_id"] == product]
    assert {e["actor_id"] for e in refused} >= {"u-inv-admin-pharm", "u-inv-vet-lapsed"}
    assert all(e["action_result"] == "denied" for e in refused)
    # A veterinarian with a live practitioner authority handles it, audited under their own identity.
    ok = _move(vet, location_id=loc, product_id=product, batch="P", quantity_delta=5, reason="RECEIPT")
    assert ok.status_code == 200, ok.text
    assert ok.json()[0]["supply_class"] == (klass or "POM")
    assert any(e["resource_id"] == ok.json()[0]["movement_id"] and e["actor_id"] == "u-inv-vet-pharm"
               for e in _events(vet, "inventory.movement.recorded"))


@pytest.mark.parametrize("product,klass", [("gauze-gen", "GENERAL"), ("shampoo-otc", "OTC")])
def test_general_and_otc_stock_is_handled_by_tenant_staff(product, klass):
    admin = _client("u-inv-admin-gen", T_A, "partner_clinic_admin")
    _register(product, klass)
    loc = _location(admin, f"Class {product}")
    assert _move(admin, location_id=loc, product_id=product, batch="G", quantity_delta=6,
                 reason="RECEIPT").status_code == 200
    assert _move(admin, location_id=loc, product_id=product, batch="G", quantity_delta=-2,
                 reason="ADJUSTMENT").status_code == 200
    assert _stock(admin, loc, product) == 4

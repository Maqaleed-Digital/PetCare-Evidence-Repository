"""MVC-EPC-D-001 D2n — PostgreSQL: J-O9 internal tracking is derived from durable records. After a second instance reads the
order, the routing decision, the collection and the receipt back, `orders.tracking_view` reports every step done at the stored
times, in order, and never a carrier; a routing REFUSAL (no chosen location) is not a route."""
import os
import sys
from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

psycopg = pytest.importorskip("psycopg")

import routers.auth as auth  # noqa: E402,F401
from inventory import InventoryLocation  # noqa: E402
from orders import Collection, Order, OrderLine, Receipt, tracking_view  # noqa: E402
from persistence import MODE_POSTGRES, PERSISTENCE_MODE_ENV_VAR, build_persistence  # noqa: E402
from repositories import UserIdentity  # noqa: E402
from routing import RULE_VERSION, RoutingDecision  # noqa: E402
from secret_provider import SECRET_MODE_ENV_VAR  # noqa: E402
from tenants import Tenant  # noqa: E402

T = "t-d2n-pg"
ENV = {SECRET_MODE_ENV_VAR: "environment", PERSISTENCE_MODE_ENV_VAR: MODE_POSTGRES}
CAND = ({"location_id": "ph-1", "name": "North", "licensed": True, "has_basket": True, "eta_seconds": 300,
         "distance_metres": 2000},)


def test_tracking_is_derived_from_the_stored_lifecycle_records(clean_postgres):
    p = build_persistence(ENV, connection_url=clean_postgres)
    p.tenants.create(Tenant(tenant_id=T, display_name=T))
    p.identities.create(UserIdentity(user_id="u-own", email="o@t", password_hash="x", role="owner", full_name="o", tenant_id=T))
    t0 = datetime(2031, 3, 1, 6, 0, tzinfo=timezone.utc)
    p.inventory.add_location(InventoryLocation(location_id="ph-1", tenant_id=T, name="North", created_at=t0, latitude=24.9,
                                               longitude=46.9))
    o = p.orders.create(Order(order_id=str(uuid4()), tenant_id=T, owner_id="u-own", payment_method="COD",
                              lines=(OrderLine("food", 1, 1000),), created_at=t0))
    p.routing.record(RoutingDecision(decision_id="d-1", order_id=o.order_id, tenant_id=T, owner_latitude=24.7, owner_longitude=46.6,
                                     candidates=CAND, chosen_location_id="ph-1", rule_version=RULE_VERSION, decided_by="u-own",
                                     decided_at=t0 + timedelta(minutes=5)))
    p.orders.deliver(Collection(order_id=o.order_id, tenant_id=T, amount_halalas=1000, reference="CASH-1", source="STAFF",
                                confirmed_by="u-staff", confirmed_at=t0 + timedelta(hours=2)),
                     Receipt(receipt_id=str(uuid4()), order_id=o.order_id, tenant_id=T, owner_id="u-own", language="ar",
                             rendered="إيصال رقمي", total_halalas=1000, issued_at=t0 + timedelta(hours=2, seconds=1)))
    q = build_persistence(ENV, connection_url=clean_postgres)
    v = tracking_view(q.orders.get(o.order_id, tenant_id=T), q.routing.latest_for(o.order_id, tenant_id=T),
                      q.orders.collection_of(o.order_id, tenant_id=T), q.orders.receipt_of(o.order_id, tenant_id=T))
    assert [(s["step"], s["done"]) for s in v["steps"]] == [("PLACED", True), ("ROUTED", True), ("DELIVERED", True),
                                                            ("RECEIPT_ISSUED", True)]
    got = [datetime.fromisoformat(s["at"]).astimezone(timezone.utc) for s in v["steps"]]
    assert got == [t0, t0 + timedelta(minutes=5), t0 + timedelta(hours=2), t0 + timedelta(hours=2, seconds=1)]
    assert v["carrier"] is None
    # a second, undelivered order with only a REFUSED routing decision: placed, not routed
    o2 = q.orders.create(Order(order_id=str(uuid4()), tenant_id=T, owner_id="u-own", payment_method="COD",
                               lines=(OrderLine("food", 1, 1000),), created_at=t0))
    q.routing.record(RoutingDecision(decision_id="d-2", order_id=o2.order_id, tenant_id=T, owner_latitude=24.7, owner_longitude=46.6,
                                     candidates=CAND, chosen_location_id=None, rule_version=RULE_VERSION, decided_by="u-own",
                                     decided_at=t0))
    v2 = tracking_view(q.orders.get(o2.order_id, tenant_id=T), q.routing.latest_for(o2.order_id, tenant_id=T),
                       q.orders.collection_of(o2.order_id, tenant_id=T), q.orders.receipt_of(o2.order_id, tenant_id=T))
    assert [s["done"] for s in v2["steps"]] == [True, False, False, False]
    p.pool.close(); q.pool.close()

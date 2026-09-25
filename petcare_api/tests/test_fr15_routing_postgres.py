"""FR-15 AC-FR-15-04 (U18) — routing decisions, their inputs and the pharmacy positions are durable in PostgreSQL;
the database refuses a decision that records no candidates."""
import os
import sys
from datetime import datetime, timezone
from uuid import uuid4

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

psycopg = pytest.importorskip("psycopg")

import routers.auth as auth  # noqa: E402,F401
from inventory import InventoryLocation  # noqa: E402
from orders import Order, OrderLine  # noqa: E402
from persistence import MODE_POSTGRES, PERSISTENCE_MODE_ENV_VAR, build_persistence  # noqa: E402
from repositories import UserIdentity  # noqa: E402
from routing import RULE_VERSION, RoutingDecision  # noqa: E402
from secret_provider import SECRET_MODE_ENV_VAR  # noqa: E402
from tenants import Tenant  # noqa: E402

T = "t-fr15-pg"
_ENV = {SECRET_MODE_ENV_VAR: "environment", PERSISTENCE_MODE_ENV_VAR: MODE_POSTGRES}


@pytest.fixture()
def pg(clean_postgres):
    p = build_persistence(_ENV, connection_url=clean_postgres)
    p.tenants.create(Tenant(tenant_id=T, display_name=T))
    p.identities.create(UserIdentity(user_id="u-own", email="o@t", password_hash="x", role="owner", full_name="o", tenant_id=T))
    yield clean_postgres, p
    p.pool.close()


def test_a_routing_decision_and_its_inputs_survive_a_second_instance(pg):
    url, p = pg
    now = datetime.now(timezone.utc)
    loc = p.inventory.add_location(InventoryLocation(location_id="ph-1", tenant_id=T, name="North", created_at=now,
                                                     latitude=24.9, longitude=46.9))
    p.routing.license(loc.location_id, "GENERAL")
    o = p.orders.create(Order(order_id=str(uuid4()), tenant_id=T, owner_id="u-own", payment_method="COD",
                              lines=(OrderLine("food", 1, 1000),), created_at=now))
    cand = ({"location_id": "ph-1", "name": "North", "licensed": True, "has_basket": True, "eta_seconds": 300,
             "distance_metres": 2000},)
    p.routing.record(RoutingDecision(decision_id="d-1", order_id=o.order_id, tenant_id=T, owner_latitude=24.7,
                                     owner_longitude=46.6, candidates=cand, chosen_location_id="ph-1",
                                     rule_version=RULE_VERSION, decided_by="u-own", decided_at=now))
    q = build_persistence(_ENV, connection_url=url)
    d = q.routing.latest_for(o.order_id, tenant_id=T)
    assert (d.chosen_location_id, list(d.candidates), d.owner_latitude) == ("ph-1", list(cand), 24.7)
    assert q.routing.licensed("ph-1", "GENERAL") and not q.routing.licensed("ph-1", "POM")
    assert (q.inventory.get_location("ph-1", tenant_id=T).latitude, q.inventory.get_location("ph-1", tenant_id=T).longitude) == (24.9, 46.9)
    assert q.routing.latest_for(o.order_id, tenant_id="t-other") is None
    with psycopg.connect(url, autocommit=True) as conn:
        with pytest.raises(psycopg.errors.CheckViolation):
            conn.execute("INSERT INTO routing_decision (decision_id, order_id, tenant_id, owner_latitude, owner_longitude, "
                         "candidates, chosen_location_id, rule_version, decided_by, decided_at) "
                         "VALUES ('d-2', %s, %s, 1, 1, '[]'::jsonb, NULL, 'r', 'u', now())", (o.order_id, T))
    q.pool.close()

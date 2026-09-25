"""FR-19 AC-FR-19-01/02 (U13) — batch-bearing dispenses and recall notices are durable in PostgreSQL; the
database refuses a movement without a batch or with a zero quantity, and a second notice for one dispense."""
import os
import sys
from datetime import date, datetime, timezone
from uuid import uuid4

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

psycopg = pytest.importorskip("psycopg")

import routers.auth as auth  # noqa: E402,F401
from inventory import InventoryLocation, StockMovement  # noqa: E402
from persistence import MODE_POSTGRES, PERSISTENCE_MODE_ENV_VAR, build_persistence  # noqa: E402
from recalls import Recall, RecallNotification  # noqa: E402
from repositories import RepositoryDenied, UserIdentity  # noqa: E402
from secret_provider import SECRET_MODE_ENV_VAR  # noqa: E402
from tenants import Tenant  # noqa: E402

T = "t-fr19-pg"
_ENV = {SECRET_MODE_ENV_VAR: "environment", PERSISTENCE_MODE_ENV_VAR: MODE_POSTGRES}


@pytest.fixture()
def pg(clean_postgres):
    p = build_persistence(_ENV, connection_url=clean_postgres)
    p.tenants.create(Tenant(tenant_id=T, display_name=T))
    p.identities.create(UserIdentity(user_id="u-own", email="o@t", password_hash="x", role="owner", full_name="o", tenant_id=T))
    loc = p.inventory.add_location(InventoryLocation(location_id="loc-19", tenant_id=T, name="L",
                                                     created_at=datetime.now(timezone.utc))).location_id
    yield clean_postgres, p, loc
    p.pool.close()


def _mv(loc, delta, reason, batch="B-1", rx=None, expiry=None):
    return StockMovement(movement_id=str(uuid4()), tenant_id=T, location_id=loc, product_id="vax", batch=batch,
                         quantity_delta=delta, reason=reason, supply_class="POM", actor_id="u", actor_role="veterinarian",
                         created_at=datetime.now(timezone.utc), prescription_id=rx, batch_expiry=expiry)


def test_a_batch_bearing_dispense_and_its_recall_notice_survive_a_second_instance(pg):
    url, p, loc = pg
    p.inventory.record([_mv(loc, 10, "RECEIPT", expiry=date(2030, 1, 31))])
    supply = _mv(loc, -2, "SUPPLY", rx="rx-19")
    p.inventory.record([supply])
    now = datetime.now(timezone.utc)
    rc = Recall(recall_id=str(uuid4()), tenant_id=T, product_id="vax", batch="B-1", reason="r", source="STAFF",
                initiated_by_actor_id="u-staff", created_at=now)
    note = RecallNotification(notification_id=str(uuid4()), recall_id=rc.recall_id, tenant_id=T, owner_id="u-own",
                              movement_id=supply.movement_id, rendered_body="Recall: vax B-1", created_at=now)
    p.recalls.create(rc, [note])
    r = build_persistence(_ENV, connection_url=url)
    got = r.inventory.supplies_of_batch(tenant_id=T, product_id="vax", batch="B-1")
    assert [(m.batch, m.prescription_id, m.quantity_delta) for m in got] == [("B-1", "rx-19", -2)]
    assert [b["batch_expiry"] for b in r.inventory.balances(tenant_id=T, location_id=loc)] == ["2030-01-31"]
    assert r.recalls.get(rc.recall_id, tenant_id=T).reason == "r"
    assert [n.movement_id for n in r.recalls.notices_for_owner("u-own", tenant_id=T)] == [supply.movement_id]
    assert r.recalls.get(rc.recall_id, tenant_id="t-other") is None
    with pytest.raises(RepositoryDenied):  # one notice per affected dispense
        r.recalls.create(Recall(recall_id=rc.recall_id + "-2", tenant_id=T, product_id="vax", batch="B-1", reason="r",
                                source="STAFF", initiated_by_actor_id="u", created_at=now), [note, note])
    r.pool.close()


def test_the_database_refuses_a_movement_without_a_batch_or_quantity(pg):
    url, _p, loc = pg
    with psycopg.connect(url, autocommit=True) as conn:
        for batch, qty in (("  ", 1), ("B", 0)):
            with pytest.raises(psycopg.errors.CheckViolation):
                conn.execute("INSERT INTO stock_movement (movement_id, tenant_id, location_id, product_id, batch, "
                             "quantity_delta, reason, supply_class, actor_id, actor_role, created_at) "
                             "VALUES (%s,%s,%s,'vax',%s,%s,'RECEIPT','POM','u','veterinarian',now())",
                             (str(uuid4()), T, loc, batch, qty))

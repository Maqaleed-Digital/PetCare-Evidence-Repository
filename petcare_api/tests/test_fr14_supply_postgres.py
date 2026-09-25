"""FR-14 AC-FR-14-03 (U9) — the prescription gate held by PostgreSQL itself (migration 0042).

A veterinarian-only (POM/RESTRICTED/CONTROLLED) SUPPLY that cites no prescription is refused by
the database, whatever code path writes it; a GENERAL/OTC supply needs none; a SUPPLY adds no stock.
"""
import os
import sys
from datetime import datetime, timezone
from uuid import uuid4

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

psycopg = pytest.importorskip("psycopg")

import routers.auth as auth  # noqa: E402,F401
from inventory import InventoryLocation, StockMovement  # noqa: E402
from persistence import MODE_POSTGRES, PERSISTENCE_MODE_ENV_VAR, build_persistence  # noqa: E402
from repositories import RepositoryDenied  # noqa: E402
from secret_provider import SECRET_MODE_ENV_VAR  # noqa: E402
from tenants import Tenant  # noqa: E402

T = "t-supply-pg"
_ENV = {SECRET_MODE_ENV_VAR: "environment", PERSISTENCE_MODE_ENV_VAR: MODE_POSTGRES}


@pytest.fixture()
def pg(clean_postgres):
    p = build_persistence(_ENV, connection_url=clean_postgres)
    p.tenants.create(Tenant(tenant_id=T, display_name=T))
    loc = p.inventory.add_location(InventoryLocation(location_id=str(uuid4()), tenant_id=T, name="S",
                                                     created_at=datetime.now(timezone.utc))).location_id
    for klass, product in (("GENERAL", "gen"), ("POM", "pom")):
        p.inventory.record([_mv(loc, product, 10, "RECEIPT", klass)])
    yield clean_postgres, loc, p
    p.pool.close()


def _mv(loc, product, delta, reason, klass, rx=None):
    return StockMovement(movement_id=str(uuid4()), tenant_id=T, location_id=loc, product_id=product, batch="B",
                         quantity_delta=delta, reason=reason, supply_class=klass, actor_id="u", actor_role="veterinarian",
                         created_at=datetime.now(timezone.utc), prescription_id=rx)


def _raw_insert(url, loc, product, delta, klass, rx):
    with psycopg.connect(url, autocommit=True) as conn:
        conn.execute("INSERT INTO stock_movement (movement_id, tenant_id, location_id, product_id, batch, quantity_delta, "
                     "reason, supply_class, actor_id, actor_role, created_at, prescription_id) "
                     "VALUES (%s,%s,%s,%s,'B',%s,'SUPPLY',%s,'u','veterinarian',now(),%s)",
                     (str(uuid4()), T, loc, product, delta, klass, rx))


def test_the_database_refuses_a_veterinarian_only_supply_without_a_prescription(pg):
    url, loc, p = pg
    for klass in ("POM", "RESTRICTED", "CONTROLLED"):
        with pytest.raises(psycopg.errors.CheckViolation):
            _raw_insert(url, loc, "pom", -1, klass, None)
    with pytest.raises(psycopg.errors.CheckViolation):  # a supply never adds stock
        _raw_insert(url, loc, "gen", 1, "GENERAL", None)
    _raw_insert(url, loc, "gen", -1, "GENERAL", None)   # GENERAL: no prescription needed
    _raw_insert(url, loc, "pom", -1, "POM", "rx-1")      # POM: cites a prescription
    with pytest.raises(RepositoryDenied):                 # the repository refuses it before the database
        p.inventory.record([_mv(loc, "pom", -1, "SUPPLY", "POM")])


def test_a_supply_survives_a_second_instance_with_its_prescription(pg):
    url, loc, p = pg
    p.inventory.record([_mv(loc, "pom", -2, "SUPPLY", "POM", rx="rx-42")])
    r = build_persistence(_ENV, connection_url=url)
    supplies = [m for m in r.inventory.movements(tenant_id=T, location_id=loc) if m.reason == "SUPPLY"]
    assert [(m.product_id, m.quantity_delta, m.prescription_id) for m in supplies] == [("pom", -2, "rx-42")]
    assert {b["product_id"]: b["quantity"] for b in r.inventory.balances(tenant_id=T, location_id=loc)}["pom"] == 8
    r.pool.close()

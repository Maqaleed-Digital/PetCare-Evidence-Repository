"""FR-13 (U8) — the stock ledger against REAL PostgreSQL, through the repository the serving path uses.

AC-FR-13-02: movements survive a second instance; a balance is the SUM of its movements; the
database itself refuses UPDATE and DELETE of a movement; no table stores a stock quantity.
AC-FR-13-03 (NFR-04): an inventory check on production-sized data answers in under one second.

PRODUCTION-SIZED is fixed here, since the BRD gives no figure: one tenant, 30 pharmacy locations,
1,000 products x 2 batches per location, 5 movements per (location, product, batch) =
300,000 movements — well above a launch pharmacy network's first-year ledger. The bound is
asserted on the worst of 20 repetitions, not the mean.
"""
import os
import sys
import time
from datetime import datetime, timezone
from uuid import uuid4

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

psycopg = pytest.importorskip("psycopg")

import routers.auth as auth  # noqa: E402,F401
from inventory import (REGISTRATION_SOURCE, InventoryLocation, ProductRegistration,  # noqa: E402
                       StockMovement)
from persistence import MODE_POSTGRES, PERSISTENCE_MODE_ENV_VAR, build_persistence  # noqa: E402
from repositories import RepositoryDenied  # noqa: E402
from secret_provider import SECRET_MODE_ENV_VAR  # noqa: E402
from tenants import Tenant  # noqa: E402

T_A, T_B = "t-inv-pg", "t-inv-pg-b"
_ENV = {SECRET_MODE_ENV_VAR: "environment", PERSISTENCE_MODE_ENV_VAR: MODE_POSTGRES}
LOCATIONS, PRODUCTS, BATCHES, PER_KEY = 30, 1000, 2, 5
BOUND_S, REPEATS = 1.0, 20


def _p(url):
    return build_persistence(_ENV, connection_url=url)


@pytest.fixture()
def pg(clean_postgres):
    p = _p(clean_postgres)
    for t in (T_A, T_B):
        p.tenants.create(Tenant(tenant_id=t, display_name=t))
    yield clean_postgres
    p.pool.close()


def _mv(loc, product, delta, reason="RECEIPT", tenant=T_A, batch="B1", klass="GENERAL"):
    return StockMovement(movement_id=str(uuid4()), tenant_id=tenant, location_id=loc, product_id=product,
                         batch=batch, quantity_delta=delta, reason=reason, supply_class=klass, actor_id="u-a",
                         actor_role="partner_clinic_admin", created_at=datetime.now(timezone.utc))


def _loc(p, name, tenant=T_A):
    return p.inventory.add_location(InventoryLocation(location_id=str(uuid4()), tenant_id=tenant, name=name,
                                                      created_at=datetime.now(timezone.utc))).location_id


def test_ledger_survives_a_second_instance_and_the_balance_is_the_sum(pg):
    w = _p(pg)
    w.inventory.register_product(ProductRegistration(product_id="amoxi", name="Amoxicillin", supply_class="POM",
                                                      source=REGISTRATION_SOURCE,
                                                      registered_at=datetime.now(timezone.utc)))
    north, south = _loc(w, "North"), _loc(w, "South")
    w.inventory.record([_mv(north, "amoxi", 30, klass="POM")])
    w.inventory.record([_mv(north, "amoxi", -12, "TRANSFER_OUT", klass="POM"),
                        _mv(south, "amoxi", 12, "TRANSFER_IN", klass="POM")])
    w.inventory.record([_mv(north, "amoxi", -3, "ADJUSTMENT", klass="POM")])
    r = _p(pg)
    got = {(b["location_id"], b["quantity"], b["supply_class"]) for b in r.inventory.balances(tenant_id=T_A)}
    assert got == {(north, 15, "POM"), (south, 12, "POM")}
    for loc in (north, south):
        led = sum(m.quantity_delta for m in r.inventory.movements(tenant_id=T_A, location_id=loc))
        assert [b["quantity"] for b in r.inventory.balances(tenant_id=T_A, location_id=loc)] == [led]
    assert r.inventory.balances(tenant_id=T_B) == [] and r.inventory.locations(tenant_id=T_B) == []
    assert r.inventory.supply_class_of("never-registered") == "POM"
    with pytest.raises(RepositoryDenied):
        r.inventory.record([_mv(south, "amoxi", -13, "ADJUSTMENT", klass="POM")])
    with pytest.raises(RepositoryDenied):  # another tenant's location
        r.inventory.record([_mv(north, "amoxi", 1, tenant=T_B, klass="POM")])
    for p in (w, r):
        p.pool.close()


def test_the_database_refuses_update_and_delete_of_a_movement(pg):
    w = _p(pg)
    loc = _loc(w, "Immutable")
    m = w.inventory.record([_mv(loc, "gauze", 5)])[0]
    with psycopg.connect(pg, autocommit=True) as conn:
        for sql in ("UPDATE stock_movement SET quantity_delta = 500 WHERE movement_id = %s",
                    "DELETE FROM stock_movement WHERE movement_id = %s"):
            with pytest.raises(psycopg.errors.RestrictViolation):
                conn.execute(sql, (m.movement_id,))
        assert conn.execute("SELECT quantity_delta FROM stock_movement WHERE movement_id = %s",
                            (m.movement_id,)).fetchone()[0] == 5
    w.pool.close()


def test_no_table_stores_a_stock_quantity(pg):
    """The FR-13 tables hold no quantity but the movement delta, and no table anywhere holds a
    stock balance / on-hand / stock level (pre-existing pricing-rule quantities are not stock)."""
    with psycopg.connect(pg) as conn:
        inv = conn.execute("SELECT table_name, column_name FROM information_schema.columns "
                           "WHERE table_schema = 'public' AND table_name IN "
                           "('inventory_location', 'product_registration', 'stock_movement') "
                           "AND (column_name ILIKE '%%quantity%%' OR column_name ILIKE '%%qty%%' "
                           "OR column_name ILIKE '%%balance%%')").fetchall()
        anywhere = conn.execute("SELECT table_name, column_name FROM information_schema.columns "
                                "WHERE table_schema = 'public' AND (column_name ILIKE '%%balance%%' "
                                "OR column_name ILIKE '%%on_hand%%' OR column_name ILIKE '%%stock_level%%' "
                                "OR column_name ILIKE '%%stock_qu%%' OR column_name ILIKE '%%in_stock%%')").fetchall()
    assert inv == [("stock_movement", "quantity_delta")]
    assert anywhere == []


def _seed_production_size(url) -> tuple:
    """Direct SQL bulk insert (append-only INSERTs; the trigger guards only UPDATE/DELETE)."""
    with psycopg.connect(url, autocommit=True) as conn:
        conn.execute("INSERT INTO inventory_location (location_id, tenant_id, name, created_at) "
                     "SELECT 'perf-loc-' || l, %s, 'Perf ' || l, now() FROM generate_series(1, %s) l",
                     (T_A, LOCATIONS))
        conn.execute(
            "INSERT INTO stock_movement (movement_id, tenant_id, location_id, product_id, batch, quantity_delta, "
            "reason, supply_class, actor_id, actor_role, created_at) "
            "SELECT md5(l || '/' || p || '/' || b || '/' || k), %s, 'perf-loc-' || l, 'perf-prod-' || p, "
            "'B' || b, CASE WHEN k = 1 THEN 100 ELSE -1 END, CASE WHEN k = 1 THEN 'RECEIPT' ELSE 'ADJUSTMENT' END, "
            "'GENERAL', 'u-seed', 'partner_clinic_admin', now() "
            "FROM generate_series(1, %s) l, generate_series(1, %s) p, generate_series(1, %s) b, "
            "generate_series(1, %s) k", (T_A, LOCATIONS, PRODUCTS, BATCHES, PER_KEY))
        conn.execute("ANALYZE stock_movement")
        n = conn.execute("SELECT count(*) FROM stock_movement WHERE tenant_id = %s", (T_A,)).fetchone()[0]
    return n, "perf-loc-17", "perf-prod-503"


def _worst(fn) -> float:
    worst = 0.0
    for _ in range(REPEATS):
        t = time.perf_counter()
        fn()
        worst = max(worst, time.perf_counter() - t)
    return worst


def test_inventory_check_is_sub_second_on_production_sized_data(pg):
    n, loc, product = _seed_production_size(pg)
    assert n == LOCATIONS * PRODUCTS * BATCHES * PER_KEY == 300_000
    r = _p(pg)
    per_location = r.inventory.balances(tenant_id=T_A, location_id=loc)
    per_product = r.inventory.balances(tenant_id=T_A, product_id=product)
    assert len(per_location) == PRODUCTS * BATCHES and {b["quantity"] for b in per_location} == {96}
    assert len(per_product) == LOCATIONS * BATCHES
    worst_location = _worst(lambda: r.inventory.balances(tenant_id=T_A, location_id=loc))
    worst_product = _worst(lambda: r.inventory.balances(tenant_id=T_A, product_id=product))
    print(f"AC-FR-13-03 worst of {REPEATS}: per-location {worst_location * 1000:.1f} ms, "
          f"per-product {worst_product * 1000:.1f} ms over {n} movements")
    assert worst_location < BOUND_S, worst_location
    assert worst_product < BOUND_S, worst_product
    r.pool.close()

"""FR-20 AC-FR-20-01/02 (U14) — COD orders, their collection and receipt are durable in PostgreSQL; a
receipt cannot exist without a collection, and a collection of the wrong amount is refused."""
import os
import sys
from datetime import datetime, timezone
from uuid import uuid4

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

psycopg = pytest.importorskip("psycopg")

import routers.auth as auth  # noqa: E402,F401
from orders import Collection, Order, OrderLine, PriceEntry, Receipt  # noqa: E402
from persistence import MODE_POSTGRES, PERSISTENCE_MODE_ENV_VAR, build_persistence  # noqa: E402
from repositories import RepositoryDenied, UserIdentity  # noqa: E402
from secret_provider import SECRET_MODE_ENV_VAR  # noqa: E402
from tenants import Tenant  # noqa: E402

T = "t-fr20-pg"
_ENV = {SECRET_MODE_ENV_VAR: "environment", PERSISTENCE_MODE_ENV_VAR: MODE_POSTGRES}


@pytest.fixture()
def pg(clean_postgres):
    p = build_persistence(_ENV, connection_url=clean_postgres)
    p.tenants.create(Tenant(tenant_id=T, display_name=T))
    p.identities.create(UserIdentity(user_id="u-own", email="o@t", password_hash="x", role="owner", full_name="o", tenant_id=T))
    yield clean_postgres, p
    p.pool.close()


def _order(p):
    now = datetime.now(timezone.utc)
    p.orders.set_price(PriceEntry(tenant_id=T, product_id="sh", unit_price_halalas=1000, set_by_actor_id="a", set_at=now))
    p.orders.set_price(PriceEntry(tenant_id=T, product_id="sh", unit_price_halalas=1250, set_by_actor_id="a", set_at=now))
    return p.orders.create(Order(order_id=str(uuid4()), tenant_id=T, owner_id="u-own", payment_method="COD",
                                 lines=(OrderLine("sh", 2, p.orders.price_of("sh", tenant_id=T)),), created_at=now)), now


def test_a_cod_order_its_collection_and_receipt_survive_a_second_instance(pg):
    url, p = pg
    o, now = _order(p)
    assert o.total_halalas == 2500
    c = Collection(order_id=o.order_id, tenant_id=T, amount_halalas=2500, reference="CASH-1", source="STAFF",
                   confirmed_by="u-staff", confirmed_at=now)
    p.orders.deliver(c, Receipt(receipt_id=str(uuid4()), order_id=o.order_id, tenant_id=T, owner_id="u-own", language="ar",
                                rendered="إيصال رقمي", total_halalas=2500, issued_at=now))
    r = build_persistence(_ENV, connection_url=url)
    got = r.orders.get(o.order_id, tenant_id=T)
    assert (got.payment_method, [(l.product_id, l.quantity, l.unit_price_halalas) for l in got.lines]) == ("COD", [("sh", 2, 1250)])
    assert r.orders.collection_of(o.order_id, tenant_id=T).reference == "CASH-1"
    assert r.orders.receipt_of(o.order_id, tenant_id=T).rendered == "إيصال رقمي"
    assert r.orders.get(o.order_id, tenant_id="t-other") is None and r.orders.prices(tenant_id=T) == {"sh": 1250}
    r.pool.close()


def test_the_database_refuses_a_receipt_without_a_collection_and_a_wrong_amount(pg):
    url, p = pg
    o, now = _order(p)
    with pytest.raises(RepositoryDenied):
        p.orders.deliver(Collection(order_id=o.order_id, tenant_id=T, amount_halalas=100, reference="X", source="STAFF",
                                    confirmed_by="u", confirmed_at=now),
                         Receipt(receipt_id=str(uuid4()), order_id=o.order_id, tenant_id=T, owner_id="u-own", language="ar",
                                 rendered="x", total_halalas=100, issued_at=now))
    with psycopg.connect(url, autocommit=True) as conn:
        with pytest.raises(psycopg.errors.ForeignKeyViolation):
            conn.execute("INSERT INTO order_receipt (receipt_id, order_id, tenant_id, owner_id, language, rendered, "
                         "total_halalas, issued_at) VALUES (%s,%s,%s,'u-own','ar','x',2500,now())",
                         (str(uuid4()), o.order_id, T))
    assert p.orders.collection_of(o.order_id, tenant_id=T) is None

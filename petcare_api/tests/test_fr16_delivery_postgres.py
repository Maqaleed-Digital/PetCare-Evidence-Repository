"""FR-16 AC-FR-16-01 (U12) — deliveries, temperature logs, alerts and completions are durable in
PostgreSQL; a reading after completion is refused; each alert belongs to exactly one reading."""
import os
import sys
from datetime import datetime, timezone
from uuid import uuid4

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

psycopg = pytest.importorskip("psycopg")

import routers.auth as auth  # noqa: E402,F401
from deliveries import Delivery, DeliveryAlert, DeliveryCompletion, TemperatureReading  # noqa: E402
from inventory import REGISTRATION_SOURCE, ProductRegistration  # noqa: E402
from persistence import MODE_POSTGRES, PERSISTENCE_MODE_ENV_VAR, build_persistence  # noqa: E402
from repositories import RepositoryDenied, UserIdentity  # noqa: E402
from secret_provider import SECRET_MODE_ENV_VAR  # noqa: E402
from tenants import Tenant  # noqa: E402

T = "t-fr16-pg"
_ENV = {SECRET_MODE_ENV_VAR: "environment", PERSISTENCE_MODE_ENV_VAR: MODE_POSTGRES}


@pytest.fixture()
def pg(clean_postgres):
    p = build_persistence(_ENV, connection_url=clean_postgres)
    p.tenants.create(Tenant(tenant_id=T, display_name=T))
    p.identities.create(UserIdentity(user_id="u-own", email="o@t", password_hash="x", role="owner", full_name="o",
                                     tenant_id=T))
    yield clean_postgres, p
    p.pool.close()


def _reading(did, c, oor):
    return TemperatureReading(reading_id=str(uuid4()), delivery_id=did, tenant_id=T, recorded_at=datetime.now(timezone.utc),
                              celsius=c, source="STAFF", recorded_by="u-staff", out_of_range=oor)


def test_a_cold_chain_delivery_and_its_log_survive_a_second_instance(pg):
    url, p = pg
    p.inventory.register_product(ProductRegistration(product_id="vax", name="vax", supply_class="GENERAL",
                                                     source=REGISTRATION_SOURCE, registered_at=datetime.now(timezone.utc),
                                                     storage_min_c=2.0, storage_max_c=8.0))
    assert p.inventory.storage_range_of("vax") == (2.0, 8.0)
    d = p.deliveries.create(Delivery(delivery_id=str(uuid4()), tenant_id=T, owner_id="u-own", product_id="vax",
                                     created_by_actor_id="u-staff", created_at=datetime.now(timezone.utc),
                                     temp_min_c=2.0, temp_max_c=8.0))
    p.deliveries.add_reading(_reading(d.delivery_id, 4.0, False), None)
    hot = _reading(d.delivery_id, 12.5, True)
    p.deliveries.add_reading(hot, DeliveryAlert(alert_id=str(uuid4()), delivery_id=d.delivery_id, tenant_id=T,
                                                reading_id=hot.reading_id, kind="TEMPERATURE_OUT_OF_RANGE",
                                                raised_at=datetime.now(timezone.utc)))
    p.deliveries.complete(DeliveryCompletion(delivery_id=d.delivery_id, tenant_id=T, completed_by_actor_id="u-staff",
                                             completed_at=datetime.now(timezone.utc)))
    r = build_persistence(_ENV, connection_url=url)
    got = r.deliveries.get(d.delivery_id, tenant_id=T)
    assert got.cold_chain and (got.temp_min_c, got.temp_max_c) == (2.0, 8.0)
    assert [(x.celsius, x.out_of_range) for x in r.deliveries.readings(d.delivery_id, tenant_id=T)] == [(4.0, False),
                                                                                                        (12.5, True)]
    assert [a.reading_id for a in r.deliveries.alerts(tenant_id=T)] == [hot.reading_id]
    assert r.deliveries.completion_of(d.delivery_id, tenant_id=T) is not None
    with pytest.raises(RepositoryDenied):
        r.deliveries.add_reading(_reading(d.delivery_id, 5.0, False), None)
    assert r.deliveries.get(d.delivery_id, tenant_id="t-other") is None
    r.pool.close()

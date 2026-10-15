"""MVC-EPC-D-001 D2h — PostgreSQL (0060): establishment licences persist, are tenant- and location-scoped, survive a second
instance, and the DATABASE refuses a blank licence number/authority/basis or a location that does not exist."""
import os
import sys
from datetime import date, datetime, timezone

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

psycopg = pytest.importorskip("psycopg")

import routers.auth as auth  # noqa: E402,F401
import establishment_licences as est  # noqa: E402
from inventory import InventoryLocation  # noqa: E402
from persistence import MODE_POSTGRES, PERSISTENCE_MODE_ENV_VAR, build_persistence  # noqa: E402
from secret_provider import SECRET_MODE_ENV_VAR  # noqa: E402
from tenants import Tenant  # noqa: E402

NOW = datetime(2031, 3, 1, 6, 0, tzinfo=timezone.utc)
T = "t-d2h-pg"
ENV = {SECRET_MODE_ENV_VAR: "environment", PERSISTENCE_MODE_ENV_VAR: MODE_POSTGRES}


def _lic(i, loc, expires, tenant=T):
    return est.EstablishmentLicence(f"el-{i}", tenant, loc, f"SFDA-{i}", "SFDA", expires, "certificate sighted", "u-pa", NOW)


def test_establishment_licences_persist_scoped_and_the_database_refuses_invalid_rows(clean_postgres):
    p = build_persistence(ENV, connection_url=clean_postgres)
    p.tenants.create(Tenant(tenant_id=T, display_name="t"))
    p.inventory.add_location(InventoryLocation(location_id="loc-1", tenant_id=T, name="Shop", created_at=NOW))
    p.establishment_licences.record(_lic(1, "loc-1", date(2031, 3, 10)))
    p.establishment_licences.record(_lic(2, "loc-1", date(2032, 1, 1)))
    again = build_persistence(ENV, connection_url=clean_postgres).establishment_licences
    rows = again.for_location("loc-1", tenant_id=T)
    assert [l.licence_id for l in rows] == ["el-1", "el-2"] and rows[0].expires_on == date(2031, 3, 10)
    assert again.for_location("loc-1", tenant_id="t-other") == []
    assert est.valid_on(rows, date(2031, 6, 1)).licence_id == "el-2"
    assert est.valid_on(rows, date(2032, 1, 2)) is None
    with psycopg.connect(clean_postgres) as conn:
        with pytest.raises(psycopg.errors.CheckViolation):
            conn.execute("INSERT INTO establishment_licence VALUES ('el-x','t-d2h-pg','loc-1','  ','SFDA','2031-01-01','b','u',now())")
    with psycopg.connect(clean_postgres) as conn:
        with pytest.raises(psycopg.errors.ForeignKeyViolation):
            conn.execute("INSERT INTO establishment_licence VALUES ('el-y','t-d2h-pg','no-loc','N','SFDA','2031-01-01','b','u',now())")
    p.pool.close()

"""MVC-EPC-D-001 D2k — PostgreSQL (0061, Sponsor ruling R19.2): the licence type, scope and evidence-document reference persist and
survive a second instance; several licences per location are kept; the DATABASE refuses a blank value; a pre-0061 row (NULLs)
stays readable and is incomplete, so it never validates a delivery."""
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
T = "t-d2k-pg"
ENV = {SECRET_MODE_ENV_VAR: "environment", PERSISTENCE_MODE_ENV_VAR: MODE_POSTGRES}
COLS = "licence_id, tenant_id, location_id, licence_number, issuing_authority, expires_on, basis, recorded_by_actor_id, recorded_at"


def test_r19_2_fields_persist_several_per_location_and_the_database_refuses_blanks(clean_postgres):
    p = build_persistence(ENV, connection_url=clean_postgres)
    p.tenants.create(Tenant(tenant_id=T, display_name="t"))
    p.inventory.add_location(InventoryLocation(location_id="loc-1", tenant_id=T, name="Shop", created_at=NOW))
    for i, (kind, exp) in enumerate([("PHARMACY_ESTABLISHMENT", date(2031, 3, 10)), ("MEDICINES_STORE", date(2032, 1, 1))]):
        p.establishment_licences.record(est.EstablishmentLicence(f"el-{i}", T, "loc-1", f"SFDA-{i}", "SFDA", exp, "sighted", "u-pa",
                                                                 NOW, kind, f"scope {i}", f"DOC-{i}"))
    rows = build_persistence(ENV, connection_url=clean_postgres).establishment_licences.for_location("loc-1", tenant_id=T)
    assert [(l.licence_type, l.scope, l.evidence_document_ref) for l in rows] == [
        ("PHARMACY_ESTABLISHMENT", "scope 0", "DOC-0"), ("MEDICINES_STORE", "scope 1", "DOC-1")]
    assert all(l.is_complete() for l in rows) and est.valid_on(rows, date(2031, 6, 1)).licence_id == "el-1"
    for col in ("licence_type", "scope", "evidence_document_ref"):
        with psycopg.connect(clean_postgres) as conn:
            with pytest.raises(psycopg.errors.CheckViolation):
                conn.execute(f"INSERT INTO establishment_licence ({COLS}, {col}) "
                             f"VALUES ('el-b-{col}','{T}','loc-1','N','SFDA','2031-01-01','b','u',now(),'   ')")
    with psycopg.connect(clean_postgres) as conn:              # a pre-0061-shaped row: the three columns NULL
        conn.execute(f"INSERT INTO establishment_licence ({COLS}) VALUES ('el-legacy','{T}','loc-1','N','SFDA','2099-12-31','b',"
                     "'u',now())")
    legacy = [l for l in p.establishment_licences.for_location("loc-1", tenant_id=T) if l.licence_id == "el-legacy"]
    assert legacy and not legacy[0].is_complete() and est.valid_on(legacy, date(2031, 6, 1)) is None
    p.pool.close()

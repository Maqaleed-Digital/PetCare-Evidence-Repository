"""MVC-EPC-D-001 D2g — PostgreSQL (0059): owner-uploaded prescriptions persist, are tenant- and owner-scoped, survive a
second instance, and the DATABASE itself refuses an unknown status or an empty file."""
import os
import sys
from datetime import datetime, timezone

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

psycopg = pytest.importorskip("psycopg")

import routers.auth as auth  # noqa: E402,F401
import owner_prescriptions as orx  # noqa: E402
from persistence import MODE_POSTGRES, PERSISTENCE_MODE_ENV_VAR, build_persistence  # noqa: E402
from pets import PetProfile as Pet  # noqa: E402
from repositories import UserIdentity  # noqa: E402
from secret_provider import SECRET_MODE_ENV_VAR  # noqa: E402
from tenants import Tenant  # noqa: E402

NOW = datetime(2031, 3, 1, 6, 0, tzinfo=timezone.utc)
T = "t-d2g-pg"
ENV = {SECRET_MODE_ENV_VAR: "environment", PERSISTENCE_MODE_ENV_VAR: MODE_POSTGRES}


def _u(i, owner, pet):
    return orx.OwnerPrescriptionUpload(f"up-{i}", T, owner, pet, "rx.png", "image/png", 72, "ab" * 32, f"{T}/k-{i}", "",
                                       orx.AWAITING_VERIFICATION, NOW)


def test_owner_uploads_persist_scoped_and_the_database_refuses_invalid_rows(clean_postgres):
    p = build_persistence(ENV, connection_url=clean_postgres)
    p.tenants.create(Tenant(tenant_id=T, display_name="t"))
    for uid in ("u-o", "u-o2"):
        p.identities.create(UserIdentity(user_id=uid, email=f"{uid}@t", password_hash="x", role="owner", full_name=uid,
                                         tenant_id=T))
    for pid, owner in (("pet-1", "u-o"), ("pet-2", "u-o2")):
        p.pets.create(Pet(pet_id=pid, tenant_id=T, owner_id=owner, name=pid, species="cat", breed=None, birth_date=None,
                          weight_kg=None, medical_conditions=None, allergies=None, preferences=None,
                          created_by_actor_id=owner, created_at=NOW, updated_at=NOW))
    p.owner_prescription_uploads.create(_u(1, "u-o", "pet-1"))
    p.owner_prescription_uploads.create(_u(2, "u-o2", "pet-2"))
    again = build_persistence(ENV, connection_url=clean_postgres).owner_prescription_uploads
    assert [u.upload_id for u in again.list_for_owner("u-o", tenant_id=T)] == ["up-1"]
    assert again.get("up-1", tenant_id=T).uploaded_at == NOW
    assert again.get("up-1", tenant_id="t-other") is None
    assert [u.upload_id for u in again.list_awaiting(tenant_id=T)] == ["up-1", "up-2"]
    with psycopg.connect(clean_postgres) as conn:
        with pytest.raises(psycopg.errors.CheckViolation):
            conn.execute("INSERT INTO owner_prescription_upload VALUES ('up-x','t-d2g-pg','u-o','pet-1','f','image/png',"
                         "1,'h','k-x','','VERIFIED',now())")
    with psycopg.connect(clean_postgres) as conn:
        with pytest.raises(psycopg.errors.CheckViolation):
            conn.execute("INSERT INTO owner_prescription_upload VALUES ('up-y','t-d2g-pg','u-o','pet-1','f','image/png',"
                         "0,'h','k-y','','AWAITING_VERIFICATION',now())")
    p.pool.close()

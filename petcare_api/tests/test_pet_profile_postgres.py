"""FR-02 — a pet profile outlives the process that wrote it (MVC-BUILD-RUNNER-001 U2).

Against REAL PostgreSQL through the repository the serving path uses. Every
read-back goes through a SECOND `build_persistence()` instance — a fresh object
over the same database, which is what a second container is. Reading back
through the same instance would pass against the node-local store this replaced.
"""
import os
import sys
from datetime import date, datetime, timezone
from uuid import uuid4

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

psycopg = pytest.importorskip("psycopg")

from persistence import MODE_POSTGRES, PERSISTENCE_MODE_ENV_VAR, build_persistence  # noqa: E402
from pets import PetIdentification, PetMedicalRecord, PetProfile  # noqa: E402
from repositories import RepositoryDenied  # noqa: E402
from secret_provider import SECRET_MODE_ENV_VAR  # noqa: E402
from tenants import Tenant  # noqa: E402

T_A, T_B = "t-pet-pg-alpha", "t-pet-pg-beta"
_ENV = {SECRET_MODE_ENV_VAR: "environment", PERSISTENCE_MODE_ENV_VAR: MODE_POSTGRES}


def _persistence(url):
    return build_persistence(_ENV, connection_url=url)


@pytest.fixture()
def pg(clean_postgres):
    p = _persistence(clean_postgres)
    for tid in (T_A, T_B):
        if p.tenants.get(tid) is None:
            p.tenants.create(Tenant(tenant_id=tid, display_name=tid))
    yield clean_postgres
    if p.pool is not None:
        p.pool.close()


def _pet(tenant=T_A):
    now = datetime.now(timezone.utc)
    return PetProfile(pet_id=str(uuid4()), tenant_id=tenant, owner_id="u-owner", name="Luna",
                      species="cat", breed="Siamese", birth_date=date(2021, 4, 2), weight_kg=4.2,
                      medical_conditions="asthma", allergies="penicillin", preferences="SMS",
                      created_by_actor_id="u-owner", created_at=now, updated_at=now)


def test_profile_with_every_brd_field_survives_a_second_instance(pg):
    w = _persistence(pg)
    pet = w.pets.create(_pet())
    r = _persistence(pg)
    got = r.pets.get(pet.pet_id, tenant_id=T_A)
    assert got is not None
    for f in ("name", "species", "breed", "birth_date", "weight_kg", "medical_conditions",
              "allergies", "preferences", "owner_id"):
        assert getattr(got, f) == getattr(pet, f), f
    assert r.pets.get(pet.pet_id, tenant_id=T_B) is None
    for p in (w, r):
        p.pool.close()


def test_identification_and_history_survive_a_second_instance(pg):
    w = _persistence(pg)
    pet = w.pets.create(_pet())
    now = datetime.now(timezone.utc)
    w.pets.add_identification(PetIdentification(
        identification_id=str(uuid4()), pet_id=pet.pet_id, tenant_id=T_A, id_type="MICROCHIP",
        id_value="982000123456789", captured_at=date(2024, 2, 1), capture_method="scanner",
        recorded_by_actor_id="u-vet", recorded_at=now))
    w.pets.add_medical_record(PetMedicalRecord(
        record_id=str(uuid4()), pet_id=pet.pet_id, tenant_id=T_A, record_type="LAB_RESULT",
        title="CBC", recorded_by_actor_id="u-vet", recorded_at=now))
    r = _persistence(pg)
    ids = r.pets.identifications_for(pet.pet_id, tenant_id=T_A)
    assert [(i.id_type, i.id_value, i.captured_at) for i in ids] == [
        ("MICROCHIP", "982000123456789", date(2024, 2, 1))]
    assert [m.title for m in r.pets.medical_records_for(pet.pet_id, tenant_id=T_A)] == ["CBC"]
    assert r.pets.identifications_for(pet.pet_id, tenant_id=T_B) == []
    for p in (w, r):
        p.pool.close()


def test_unregistered_tenant_and_free_text_identification_are_refused(pg):
    w = _persistence(pg)
    with pytest.raises(RepositoryDenied):
        w.pets.create(_pet(tenant="t-not-registered"))
    pet = w.pets.create(_pet())
    with pytest.raises(RepositoryDenied):
        w.pets.add_identification(PetIdentification(
            identification_id=str(uuid4()), pet_id=pet.pet_id, tenant_id=T_A, id_type="NOTE",
            id_value="chip somewhere", captured_at=date(2024, 2, 1), capture_method="x",
            recorded_by_actor_id="u", recorded_at=datetime.now(timezone.utc)))
    w.pool.close()


def test_update_persists_and_cannot_touch_identity_fields(pg):
    w = _persistence(pg)
    pet = w.pets.create(_pet())
    w.pets.update(pet.pet_id, tenant_id=T_A, changes={"preferences": "email", "weight_kg": 4.6},
                  updated_at=datetime.now(timezone.utc))
    with pytest.raises(RepositoryDenied):
        w.pets.update(pet.pet_id, tenant_id=T_A, changes={"tenant_id": T_B},
                      updated_at=datetime.now(timezone.utc))
    got = _persistence(pg).pets.get(pet.pet_id, tenant_id=T_A)
    assert (got.preferences, got.weight_kg) == ("email", 4.6)
    w.pool.close()

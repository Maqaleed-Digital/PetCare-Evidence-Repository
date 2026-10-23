"""MVC-EPC-D-001 D3c — PostgreSQL: consultation SOAP drafts are durable and versioned (the latest version is read back by a second
instance, with every section and the template), tenant-scoped, and the database itself refuses an empty draft and a draft for a
consultation that does not exist."""
import os
import sys
from datetime import datetime, timedelta, timezone

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

psycopg = pytest.importorskip("psycopg")

import routers.auth as auth  # noqa: E402,F401
import consultations as consult  # noqa: E402
import soap_notes as soap  # noqa: E402
from persistence import MODE_POSTGRES, PERSISTENCE_MODE_ENV_VAR, build_persistence  # noqa: E402
from pets import PetProfile  # noqa: E402
from repositories import RepositoryDenied, UserIdentity  # noqa: E402
from secret_provider import SECRET_MODE_ENV_VAR  # noqa: E402
from tenants import Tenant  # noqa: E402

T = "t-d3c-pg"
ENV = {SECRET_MODE_ENV_VAR: "environment", PERSISTENCE_MODE_ENV_VAR: MODE_POSTGRES}
T0 = datetime(2031, 3, 1, 6, 0, tzinfo=timezone.utc)


def _d(did, sid, at, **kw):
    sections = {s: kw.get(s, "") for s in soap.SECTIONS}
    return soap.SoapDraft(draft_id=did, session_id=sid, tenant_id=kw.get("tenant", T), veterinarian_id="u-vet",
                          template_id=kw.get("template_id"), saved_at=at, **sections)


def test_soap_drafts_are_durable_versioned_and_tenant_scoped(clean_postgres):
    p = build_persistence(ENV, connection_url=clean_postgres)
    p.tenants.create(Tenant(tenant_id=T, display_name=T))
    for uid, role in (("u-own", "owner"), ("u-vet", "veterinarian")):
        p.identities.create(UserIdentity(user_id=uid, email=f"{uid}@t", password_hash="x", role=role, full_name=uid, tenant_id=T))
    p.pets.create(PetProfile(pet_id="pet-1", tenant_id=T, owner_id="u-own", name="Luna", species="cat",
                             created_by_actor_id="u-own", created_at=T0, updated_at=T0))
    p.consultations.create(consult.Consultation(session_id="s-1", tenant_id=T, pet_id="pet-1", owner_id="u-own",
                                                veterinarian_id="u-vet", requested_by_actor_id="u-vet",
                                                mode=consult.MODE_IN_PERSON, created_at=T0))
    p.soap_drafts.save(_d("d-1", "s-1", T0, subjective="Limping", template_id="SOAP_GENERAL"))
    p.soap_drafts.save(_d("d-2", "s-1", T0 + timedelta(minutes=5), subjective="Limping", objective="Weight (kg): 4.2",
                          assessment="Strain", plan="Rest", template_id="SOAP_GENERAL"))
    q = build_persistence(ENV, connection_url=clean_postgres)
    got = q.soap_drafts.latest("s-1", tenant_id=T)
    assert got == _d("d-2", "s-1", T0 + timedelta(minutes=5), subjective="Limping", objective="Weight (kg): 4.2",
                     assessment="Strain", plan="Rest", template_id="SOAP_GENERAL")
    assert q.soap_drafts.versions("s-1", tenant_id=T) == 2
    assert q.soap_drafts.latest("s-1", tenant_id="t-other") is None
    assert q.soap_drafts.versions("s-1", tenant_id="t-other") == 0
    with pytest.raises(RepositoryDenied):                                       # no such consultation (foreign key)
        q.soap_drafts.save(_d("d-3", "s-missing", T0, subjective="Itching"))
    with p.pool.connection() as conn, pytest.raises(psycopg.errors.CheckViolation):   # the database refuses an empty draft
        conn.execute("INSERT INTO consultation_soap_draft (draft_id, session_id, tenant_id, veterinarian_id, subjective, "
                     "objective, assessment, plan, saved_at) VALUES ('d-4','s-1',%s,'u-vet',' ','','','',now())", (T,))
    assert q.soap_drafts.versions("s-1", tenant_id=T) == 2
    p.pool.close(); q.pool.close()

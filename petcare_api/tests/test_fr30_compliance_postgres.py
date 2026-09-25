"""FR-30 AC-FR-30-01/02 (U16) — report headers, prescription product links, antimicrobial registration facts
and notifiable cases are durable in PostgreSQL; the database refuses a case without its reporting clock."""
import os
import sys
from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

psycopg = pytest.importorskip("psycopg")

import routers.auth as auth  # noqa: E402,F401
from compliance import NotifiableCase, NotifiableDisease, ReportHeader  # noqa: E402
from inventory import REGISTRATION_SOURCE, ProductRegistration  # noqa: E402
from persistence import MODE_POSTGRES, PERSISTENCE_MODE_ENV_VAR, build_persistence  # noqa: E402
from pets import PetProfile  # noqa: E402
from prescriptions import Prescription  # noqa: E402
from repositories import RepositoryDenied, UserIdentity  # noqa: E402
from secret_provider import SECRET_MODE_ENV_VAR  # noqa: E402
from tenants import Tenant  # noqa: E402

T = "t-fr30-pg"
_ENV = {SECRET_MODE_ENV_VAR: "environment", PERSISTENCE_MODE_ENV_VAR: MODE_POSTGRES}


@pytest.fixture()
def pg(clean_postgres):
    p = build_persistence(_ENV, connection_url=clean_postgres)
    p.tenants.create(Tenant(tenant_id=T, display_name=T))
    p.identities.create(UserIdentity(user_id="u-own", email="o@t", password_hash="x", role="owner", full_name="o", tenant_id=T))
    now = datetime.now(timezone.utc)
    pet = p.pets.create(PetProfile(pet_id=str(uuid4()), tenant_id=T, owner_id="u-own", name="Luna", species="cat",
                                   created_by_actor_id="u-own", created_at=now, updated_at=now))
    yield clean_postgres, p, pet.pet_id, now
    p.pool.close()


def test_report_headers_product_links_and_cases_survive_a_second_instance(pg):
    url, p, pet_id, now = pg
    p.inventory.register_product(ProductRegistration(product_id="amoxi", name="a", supply_class="POM",
                                                     source=REGISTRATION_SOURCE, registered_at=now,
                                                     antimicrobial_agent="amoxicillin", antimicrobial_class="penicillin"))
    rx = p.prescriptions.create(Prescription(prescription_id=str(uuid4()), tenant_id=T, pet_id=pet_id, session_id="s",
                                             issuing_vet_id="u-vet", medication_name="m", dosage="d", instructions="i",
                                             status="ISSUED", issued_at=now), actor_id="u-vet", actor_role="veterinarian")
    p.compliance.link_product(rx.prescription_id, T, "amoxi", now)
    p.compliance.save_report(ReportHeader(report_id="rep-1", tenant_id=T, kind="CONTROLLED_SUBSTANCE_AUDIT",
                                          period_from=now - timedelta(days=1), period_to=now, generated_by="u-admin",
                                          generated_at=now, row_count=3, content_sha256="a" * 64))
    p.compliance.register_disease(NotifiableDisease("RABIES", "Rabies", 24, "register"))
    p.compliance.add_case(NotifiableCase(case_id="c-1", tenant_id=T, pet_id=pet_id, disease_code="RABIES",
                                         detected_at=now, report_due_at=now + timedelta(hours=24), recorded_by="u-vet",
                                         created_at=now))
    q = build_persistence(_ENV, connection_url=url)
    assert q.compliance.product_of(rx.prescription_id, tenant_id=T) == "amoxi"
    assert q.inventory.antimicrobial_of("amoxi") == ("amoxicillin", "penicillin")
    h = q.compliance.get_report("rep-1", tenant_id=T)
    assert (h.row_count, h.content_sha256) == (3, "a" * 64) and q.compliance.get_report("rep-1", tenant_id="x") is None
    (case,) = q.compliance.cases(tenant_id=T)
    assert case.report_due_at - case.detected_at == timedelta(hours=24)
    q.pool.close()


def test_the_database_refuses_a_case_without_its_reporting_clock(pg):
    url, p, pet_id, now = pg
    p.compliance.register_disease(NotifiableDisease("RABIES", "Rabies", 24, "register"))
    with psycopg.connect(url, autocommit=True) as conn:
        for due in (None, now - timedelta(hours=1)):
            with pytest.raises((psycopg.errors.NotNullViolation, psycopg.errors.CheckViolation)):
                conn.execute("INSERT INTO notifiable_case (case_id, tenant_id, pet_id, disease_code, detected_at, "
                             "report_due_at, recorded_by, created_at) VALUES (%s,%s,%s,'RABIES',%s,%s,'u',now())",
                             (str(uuid4()), T, pet_id, now.replace(tzinfo=None), due.replace(tzinfo=None) if due else None))
    with pytest.raises(RepositoryDenied):
        p.compliance.register_disease(NotifiableDisease("BAD", "Bad", 0, "register"))

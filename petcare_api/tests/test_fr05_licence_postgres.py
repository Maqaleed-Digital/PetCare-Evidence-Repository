"""FR-05 AC-FR-05-02 (U10) — licences and their verifications are durable, and PostgreSQL refuses a
verification that does not name its verifier and basis, or a second verification of one licence."""
import os
import sys
from datetime import date, datetime, timedelta, timezone
from uuid import uuid4

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

psycopg = pytest.importorskip("psycopg")

import routers.auth as auth  # noqa: E402,F401
from licences import LicenceVerification, VetLicence  # noqa: E402
from persistence import MODE_POSTGRES, PERSISTENCE_MODE_ENV_VAR, build_persistence  # noqa: E402
from practitioners import CLASS_VETERINARIAN, PractitionerAuthorityGrant  # noqa: E402
from repositories import RepositoryDenied, UserIdentity  # noqa: E402
from secret_provider import SECRET_MODE_ENV_VAR  # noqa: E402
from tenants import Tenant  # noqa: E402

T = "t-fr05-pg"
_ENV = {SECRET_MODE_ENV_VAR: "environment", PERSISTENCE_MODE_ENV_VAR: MODE_POSTGRES}


@pytest.fixture()
def pg(clean_postgres):
    p = build_persistence(_ENV, connection_url=clean_postgres)
    p.tenants.create(Tenant(tenant_id=T, display_name=T))
    for uid in ("u-vet-pg", "u-admin-pg"):
        p.identities.create(UserIdentity(user_id=uid, email=f"{uid}@t", password_hash="x", role="veterinarian"
                                         if uid == "u-vet-pg" else "platform_admin", full_name=uid, tenant_id=T))
    yield clean_postgres, p
    p.pool.close()


def _flow(p):
    now = datetime.now(timezone.utc)
    lic = p.licences.submit(VetLicence(licence_id=str(uuid4()), actor_id="u-vet-pg", licence_number="MEWA-9",
                                       issuing_authority="MEWA", expires_on=date.today() + timedelta(days=30),
                                       submitted_at=now))
    g = p.practitioners.grant(PractitionerAuthorityGrant(
        grant_id=str(uuid4()), tenant_id=T, actor_id="u-vet-pg", professional_class=CLASS_VETERINARIAN,
        licence_ref="MEWA:MEWA-9", effective_from=now, expires_at=lic.expires_at(), granted_by_actor_id="u-admin-pg",
        granted_at=now))
    return lic, g, now


def test_a_licence_and_its_verification_survive_a_second_instance(pg):
    url, p = pg
    lic, g, now = _flow(p)
    p.licences.record_verification(LicenceVerification(
        verification_id=str(uuid4()), licence_id=lic.licence_id, tenant_id=T, verified_by_actor_id="u-admin-pg",
        verified_at=now, method="MANUAL_STAFF", basis="MEWA register", grant_id=g.grant_id))
    r = build_persistence(_ENV, connection_url=url)
    assert [x.licence_number for x in r.licences.for_actor("u-vet-pg")] == ["MEWA-9"]
    v = r.licences.verification_of(lic.licence_id)
    assert (v.verified_by_actor_id, v.method, v.basis, v.grant_id) == ("u-admin-pg", "MANUAL_STAFF", "MEWA register",
                                                                      g.grant_id)
    assert abs((v.verified_at - now).total_seconds()) < 1
    r.pool.close()


def test_the_database_refuses_an_unnamed_or_repeated_verification(pg):
    url, p = pg
    lic, g, now = _flow(p)
    with psycopg.connect(url, autocommit=True) as conn:
        for verifier, basis in (("u-admin-pg", "  "), ("  ", "MEWA register")):
            with pytest.raises(psycopg.errors.CheckViolation):
                conn.execute("INSERT INTO vet_licence_verification (verification_id, licence_id, tenant_id, "
                             "verified_by_actor_id, verified_at, method, basis, grant_id) "
                             "VALUES (%s,%s,%s,%s,now(),'MANUAL_STAFF',%s,%s)",
                             (str(uuid4()), lic.licence_id, T, verifier, basis, g.grant_id))
    p.licences.record_verification(LicenceVerification(
        verification_id=str(uuid4()), licence_id=lic.licence_id, tenant_id=T, verified_by_actor_id="u-admin-pg",
        verified_at=now, method="MANUAL_STAFF", basis="MEWA register", grant_id=g.grant_id))
    with pytest.raises(RepositoryDenied):
        p.licences.record_verification(LicenceVerification(
            verification_id=str(uuid4()), licence_id=lic.licence_id, tenant_id=T, verified_by_actor_id="u-admin-pg",
            verified_at=now, method="MANUAL_STAFF", basis="again", grant_id=g.grant_id))

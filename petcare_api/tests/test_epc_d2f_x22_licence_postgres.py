"""MVC-EPC-D-001 D2f — X-22 (R16.3 Option B) on PostgreSQL: the persistent licence repository judges a submission on the
Asia/Riyadh calendar date, so a licence that lapsed yesterday in Riyadh is refused at 01:30 Riyadh although the UTC
date is still its expiry date, and nothing is written."""
import os
import sys
from datetime import date, datetime, timezone
from uuid import uuid4

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

psycopg = pytest.importorskip("psycopg")

import routers.auth as auth  # noqa: E402,F401
from licences import VetLicence  # noqa: E402
from persistence import MODE_POSTGRES, PERSISTENCE_MODE_ENV_VAR, build_persistence  # noqa: E402
from repositories import RepositoryDenied, UserIdentity  # noqa: E402
from secret_provider import SECRET_MODE_ENV_VAR  # noqa: E402
from tenants import Tenant  # noqa: E402

T = "t-d2f-x22-pg"
AT_0130_RIYADH = datetime(2031, 3, 9, 22, 30, tzinfo=timezone.utc)   # 2031-03-10 01:30 Asia/Riyadh


def test_the_postgres_licence_repository_judges_on_the_riyadh_calendar(clean_postgres):
    p = build_persistence({SECRET_MODE_ENV_VAR: "environment", PERSISTENCE_MODE_ENV_VAR: MODE_POSTGRES},
                          connection_url=clean_postgres)
    p.tenants.create(Tenant(tenant_id=T, display_name=T))
    p.identities.create(UserIdentity(user_id="u-vet-x22", email="u-vet-x22@t", password_hash="x", role="veterinarian",
                                     full_name="v", tenant_id=T))

    def lic(expires_on):
        return VetLicence(licence_id=str(uuid4()), actor_id="u-vet-x22", licence_number=f"MEWA-{expires_on.day}",
                          issuing_authority="MEWA", expires_on=expires_on, submitted_at=AT_0130_RIYADH)

    with pytest.raises(RepositoryDenied):
        p.licences.submit(lic(date(2031, 3, 9)))
    assert p.licences.for_actor("u-vet-x22") == []
    p.licences.submit(lic(date(2031, 3, 10)))
    assert [x.expires_on for x in p.licences.for_actor("u-vet-x22")] == [date(2031, 3, 10)]
    p.pool.close()

"""FR-01 (U5) — practitioner authority grants are durable and live. Second-instance read-back
against REAL PostgreSQL through the repository the serving path uses."""
import os
import sys
from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

psycopg = pytest.importorskip("psycopg")

import routers.auth as auth  # noqa: E402,F401
from persistence import MODE_POSTGRES, PERSISTENCE_MODE_ENV_VAR, build_persistence  # noqa: E402
from practitioners import CLASS_VETERINARIAN, PractitionerAuthorityGrant, evaluate  # noqa: E402
from repositories import RepositoryDenied, UserIdentity  # noqa: E402
from secret_provider import SECRET_MODE_ENV_VAR  # noqa: E402
from tenants import Tenant  # noqa: E402

T_A = "t-auth-pg"
_ENV = {SECRET_MODE_ENV_VAR: "environment", PERSISTENCE_MODE_ENV_VAR: MODE_POSTGRES}


def _p(url):
    return build_persistence(_ENV, connection_url=url)


@pytest.fixture()
def pg(clean_postgres):
    p = _p(clean_postgres)
    p.tenants.create(Tenant(tenant_id=T_A, display_name=T_A))
    p.identities.create(UserIdentity(user_id="u-vet-pg-auth", email="vpa@auth.test", password_hash="x",
                                     role="veterinarian", full_name="V", tenant_id=T_A))
    yield clean_postgres
    p.pool.close()


def _grant(**kw):
    now = datetime.now(timezone.utc)
    base = dict(grant_id=str(uuid4()), tenant_id=T_A, actor_id="u-vet-pg-auth",
                professional_class=CLASS_VETERINARIAN, licence_ref="MEWA-1",
                effective_from=now - timedelta(minutes=5), granted_by_actor_id="u-admin", granted_at=now)
    base.update(kw)
    return PractitionerAuthorityGrant(**base)


def test_grant_and_revocation_survive_a_second_instance(pg):
    w = _p(pg)
    g = w.practitioners.grant(_grant())
    r = _p(pg)
    live, _ = evaluate(r.practitioners.grants_for("u-vet-pg-auth", tenant_id=T_A),
                       professional_class=CLASS_VETERINARIAN, when=datetime.now(timezone.utc))
    assert live is not None and live.grant_id == g.grant_id
    r.practitioners.revoke(g.grant_id, tenant_id=T_A, at=datetime.now(timezone.utc), by="u-admin")
    live2, reason = evaluate(_p(pg).practitioners.grants_for("u-vet-pg-auth", tenant_id=T_A),
                             professional_class=CLASS_VETERINARIAN, when=datetime.now(timezone.utc))
    assert live2 is None and reason.startswith("revoked at")
    for p in (w, r):
        p.pool.close()


def test_invalid_grants_are_refused(pg):
    w = _p(pg)
    with pytest.raises(RepositoryDenied):
        w.practitioners.grant(_grant(professional_class="PHARMACIST"))
    with pytest.raises(RepositoryDenied):
        w.practitioners.grant(_grant(actor_id="u-nobody"))
    g = w.practitioners.grant(_grant())
    w.practitioners.revoke(g.grant_id, tenant_id=T_A, at=datetime.now(timezone.utc), by="u-admin")
    with pytest.raises(RepositoryDenied):
        w.practitioners.revoke(g.grant_id, tenant_id=T_A, at=datetime.now(timezone.utc), by="u-admin")
    w.pool.close()

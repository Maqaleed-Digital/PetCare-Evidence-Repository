"""MVC-EPC-D-001 D2 — PostgreSQL (0057): the owner consent ledger is append-only in the DATABASE (UPDATE and DELETE are
refused by trigger), the privacy notice cannot be revoked even by a direct INSERT, and a profile edit writes only the
display name."""
import os
import sys
from datetime import datetime, timedelta, timezone

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

psycopg = pytest.importorskip("psycopg")

import routers.auth as auth  # noqa: E402,F401
import owner_consent as oc  # noqa: E402
from persistence import MODE_POSTGRES, PERSISTENCE_MODE_ENV_VAR, build_persistence  # noqa: E402
from repositories import UserIdentity  # noqa: E402
from secret_provider import SECRET_MODE_ENV_VAR  # noqa: E402
from tenants import Tenant  # noqa: E402

NOW = datetime(2031, 3, 1, 9, 0, tzinfo=timezone.utc)


def _persistence(url):
    p = build_persistence({SECRET_MODE_ENV_VAR: "environment", PERSISTENCE_MODE_ENV_VAR: MODE_POSTGRES},
                          connection_url=url)
    p.tenants.create(Tenant(tenant_id="t-d2c-pg", display_name="t"))
    p.identities.create(UserIdentity(user_id="u-o", email="o@t", password_hash="x", role="owner", full_name="o",
                                     tenant_id="t-d2c-pg"))
    return p


def _event(i, purpose, action, minutes):
    return oc.ConsentEvent(f"ev-{i}", "t-d2c-pg", "u-o", purpose, action, "account_settings", oc.POLICY_VERSION,
                           NOW + timedelta(minutes=minutes))


def test_the_consent_ledger_is_append_only_and_its_state_is_the_latest_event(clean_postgres):
    p = _persistence(clean_postgres)
    repo = p.owner_consent
    repo.append(_event(1, oc.CARE_REMINDERS, oc.GRANT, 0))
    repo.append(_event(2, oc.CARE_REMINDERS, oc.REVOKE, 5))
    assert [e.action for e in repo.events_for("u-o", tenant_id="t-d2c-pg")] == ["GRANT", "REVOKE"]
    assert repo.latest("u-o", oc.CARE_REMINDERS, tenant_id="t-d2c-pg").action == "REVOKE"
    assert repo.events_for("u-o", tenant_id="t-other") == []
    with psycopg.connect(clean_postgres) as conn:
        for stmt in ("UPDATE owner_consent_event SET action = 'GRANT' WHERE event_id = 'ev-2'",
                     "DELETE FROM owner_consent_event WHERE event_id = 'ev-1'"):
            with pytest.raises(psycopg.errors.RaiseException, match="append-only"):
                conn.execute(stmt)
            conn.rollback()
        with pytest.raises(psycopg.errors.CheckViolation):
            conn.execute("INSERT INTO owner_consent_event VALUES ('ev-3','t-d2c-pg','u-o','privacy_notice','REVOKE',"
                         "'account_settings','v', now())")
    assert len(repo.events_for("u-o", tenant_id="t-d2c-pg")) == 2
    p.pool.close()


def test_a_profile_edit_writes_only_the_display_name_and_only_in_the_callers_tenant(clean_postgres):
    p = _persistence(clean_postgres)
    assert p.identities.set_full_name("u-o", "نورة", tenant_id="t-other") is False
    assert p.identities.set_full_name("u-o", "نورة", tenant_id="t-d2c-pg") is True
    ident = p.identities.get_by_user_id("u-o")
    assert (ident.full_name, ident.role, ident.tenant_id, ident.email) == ("نورة", "owner", "t-d2c-pg", "o@t")
    p.pool.close()

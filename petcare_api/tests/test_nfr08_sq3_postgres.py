"""NFR-08 under SQ-3 (v1.3 U28) — PostgreSQL decides the step-up and recovery rules ATOMICALLY (migration 0054).

Concurrency is where a check-then-write rule breaks: eight simultaneous spends of one always-fresh step-up, eight
redemptions of one recovery code and eight approvals of one reset must each succeed exactly once.
"""
import os
import sys
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

psycopg = pytest.importorskip("psycopg")

import routers.auth as auth  # noqa: E402,F401
import mfa  # noqa: E402
from persistence import MODE_POSTGRES, PERSISTENCE_MODE_ENV_VAR, build_persistence  # noqa: E402
from repositories import UserIdentity  # noqa: E402
from secret_provider import SECRET_MODE_ENV_VAR  # noqa: E402
from tenants import Tenant  # noqa: E402

_ENV = {SECRET_MODE_ENV_VAR: "environment", PERSISTENCE_MODE_ENV_VAR: MODE_POSTGRES}
NOW = datetime(2031, 3, 1, 9, 0, tzinfo=timezone.utc)


def _seed(p):
    p.tenants.create(Tenant(tenant_id="t-sq3pg", display_name="t"))
    for uid, role in (("u-a", "partner_clinic_admin"), ("u-b", "platform_admin"), ("u-s", "veterinarian")):
        p.identities.create(UserIdentity(user_id=uid, email=f"{uid}@t", password_hash="x", role=role, full_name=uid,
                                         tenant_id="t-sq3pg"))


def test_step_ups_recovery_codes_and_resets_are_decided_atomically(clean_postgres):
    p = build_persistence(_ENV, connection_url=clean_postgres)
    _seed(p)
    assert [i.user_id for i in p.identities.list_for_tenant(tenant_id="t-sq3pg")] == ["u-a", "u-b", "u-s"]
    repo = p.mfa

    # always-fresh: one fresh, unused step-up is spent exactly once under concurrency
    repo.record_step_up("sid-1", "u-a", NOW)
    with ThreadPoolExecutor(max_workers=8) as ex:
        wins = list(ex.map(lambda _: repo.authorize("sid-1", "u-a", now=NOW, always_fresh=True), range(8)))
    assert sum(wins) == 1 and repo.step_up("sid-1") is None

    # a normal step-up is marked used, keeps serving normal operations, and is then no longer "new"
    repo.record_step_up("sid-2", "u-a", NOW)
    assert repo.authorize("sid-2", "u-a", now=NOW, always_fresh=False)
    assert repo.authorize("sid-2", "u-a", now=NOW + timedelta(seconds=900), always_fresh=False)     # 15:00 fresh
    assert not repo.authorize("sid-2", "u-a", now=NOW + timedelta(seconds=901), always_fresh=False)  # 15:01 stale
    assert not repo.authorize("sid-2", "u-a", now=NOW, always_fresh=True)                            # already used
    assert not repo.authorize("sid-2", "u-b", now=NOW, always_fresh=False)                           # another user

    # a recovery-code step-up authorizes exactly one operation
    repo.record_step_up("sid-3", "u-a", NOW, single_use=True)
    with ThreadPoolExecutor(max_workers=8) as ex:
        wins = list(ex.map(lambda _: repo.authorize("sid-3", "u-a", now=NOW, always_fresh=False), range(8)))
    assert sum(wins) == 1

    # recovery codes: digest only in the database; one code, eight concurrent redemptions, one success
    plain, stored = mfa.issue_recovery_codes("u-a")
    repo.replace_recovery_codes("u-a", stored)
    with psycopg.connect(clean_postgres) as conn:
        rows = conn.execute("SELECT code_id, salt, digest, used_at FROM mfa_recovery_code WHERE user_id = 'u-a'").fetchall()
    raw = b"".join(bytes(r[1]) + bytes(r[2]) + r[0].encode() for r in rows)
    assert len(rows) == 10 and not any(c.encode() in raw or c.replace("-", "").encode() in raw for c in plain)
    hit = mfa.matching_code(repo.recovery_codes("u-a"), plain[3])
    with ThreadPoolExecutor(max_workers=8) as ex:
        wins = list(ex.map(lambda _: repo.use_recovery_code("u-a", hit.code_id, NOW), range(8)))
    assert sum(wins) == 1 and mfa.matching_code(repo.recovery_codes("u-a"), plain[3]) is None

    # assisted reset: approved once; the database itself refuses a self-approval
    repo.create_reset(mfa.ResetRequest("r-1", "t-sq3pg", "u-s", "u-a", NOW))
    with ThreadPoolExecutor(max_workers=8) as ex:
        wins = list(ex.map(lambda _: repo.approve_reset("r-1", tenant_id="t-sq3pg", approver="u-b", at=NOW), range(8)))
    assert sum(wins) == 1 and repo.get_reset("r-1", tenant_id="t-sq3pg").approved_by == "u-b"
    assert repo.get_reset("r-1", tenant_id="t-other") is None
    repo.create_reset(mfa.ResetRequest("r-2", "t-sq3pg", "u-s", "u-a", NOW))
    with pytest.raises(psycopg.errors.CheckViolation):
        repo.approve_reset("r-2", tenant_id="t-sq3pg", approver="u-s", at=NOW)

    # the reset removes the factor, the codes and every step-up of the subject
    nonce, ct = mfa.encrypt("k", os.urandom(20))
    repo.put_factor(mfa.Factor(user_id="u-s", nonce=nonce, ciphertext=ct, created_at=NOW, confirmed_at=NOW))
    repo.replace_recovery_codes("u-s", mfa.issue_recovery_codes("u-s")[1])
    repo.record_step_up("sid-s", "u-s", NOW)
    repo.clear_user("u-s")
    assert repo.factor("u-s") is None and repo.recovery_codes("u-s") == [] and repo.step_up("sid-s") is None
    p.pool.close()

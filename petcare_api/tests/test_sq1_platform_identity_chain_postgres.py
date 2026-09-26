"""SQ-1 (v1.2 U26) — the platform identity chain is durable, serialised (concurrent appends verify), carries no
tenant; the tenant chain's audit_event.tenant_id stays NOT NULL."""
import os
import sys
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from uuid import uuid4

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

psycopg = pytest.importorskip("psycopg")

import routers.auth as auth  # noqa: E402,F401
from persistence import MODE_POSTGRES, PERSISTENCE_MODE_ENV_VAR, build_persistence  # noqa: E402
from platform_identity_audit import PlatformAuditWriteFailed  # noqa: E402
from secret_provider import SECRET_MODE_ENV_VAR  # noqa: E402

_ENV = {SECRET_MODE_ENV_VAR: "environment", PERSISTENCE_MODE_ENV_VAR: MODE_POSTGRES}


def _ev(i):
    return {"event_id": str(uuid4()), "event_name": "auth.sign_in_failed", "subject_kind": "UNKNOWN_IDENTITY",
            "subject_ref": f"email-sha256:{i:064x}", "outcome": "denied", "reason_code": "user_not_found",
            "correlation_id": str(uuid4()), "occurred_at": datetime.now(timezone.utc).isoformat()}


def test_the_platform_chain_is_durable_serialised_and_tenantless_and_the_tenant_invariant_holds(clean_postgres):
    w1, w2 = build_persistence(_ENV, connection_url=clean_postgres), build_persistence(_ENV, connection_url=clean_postgres)
    with ThreadPoolExecutor(max_workers=8) as ex:
        list(ex.map(lambda i: (w1 if i % 2 else w2).platform_audit.append(_ev(i)), range(20)))
    r = build_persistence(_ENV, connection_url=clean_postgres)
    events = r.platform_audit.events()
    assert len(events) >= 20 and [e["chain_seq"] for e in events] == list(range(events[0]["chain_seq"],
                                                                              events[0]["chain_seq"] + len(events)))
    assert r.platform_audit.verify()["ok"] is True
    with pytest.raises(PlatformAuditWriteFailed):
        r.platform_audit.append({**_ev(99), "tenant_id": "t-sentinel"})
    with psycopg.connect(clean_postgres) as conn:
        cols = {c for (c,) in conn.execute("SELECT column_name FROM information_schema.columns "
                                           "WHERE table_name = 'platform_identity_event'").fetchall()}
        assert not {c for c in cols if "tenant" in c}
        nullable = conn.execute("SELECT is_nullable FROM information_schema.columns WHERE table_name = 'audit_event' "
                                "AND column_name = 'tenant_id'").fetchone()[0]
        assert nullable == "NO"
    for p in (w1, w2, r):
        p.pool.close()

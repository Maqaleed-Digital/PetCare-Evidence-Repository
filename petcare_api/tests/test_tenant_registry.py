"""TENANT-01..10 — a tenant is a governed object.

PRE-1 searched for an authoritative tenant and found none: no catalogue table in
any migration, no foreign key, no governance artefact naming one. `tenant_id` was
an unconstrained `TEXT` column, so a typo produced a new, empty, perfectly
functional scope that nothing would ever report.

Sponsor ruling: `TENANT_REGISTRY_STATUS=REQUIRED_FOUNDATION` — build the shape,
create no production tenant.

Every control here runs against both implementations where it can. A memory mode
that accepted a tenant the database would reject would mean the suite proves the
weaker of the two, and the control would first fail in production against the
implementation nobody had run.
"""
import os
import sys
from pathlib import Path

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

psycopg = pytest.importorskip("psycopg")
from psycopg import errors as pgerrors  # noqa: E402

from postgres_repositories import (  # noqa: E402
    PostgresIdentityRepository,
    PostgresSessionStore,
    PostgresTenantRepository,
    open_pool,
)
from repositories import (  # noqa: E402
    PROVENANCE_SEED,
    InMemoryIdentityRepository,
    UserIdentity,
)
from session_store import InMemorySessionStore, SessionDenied  # noqa: E402
from tenants import (  # noqa: E402
    TENANT_ACTIVE,
    TENANT_DISABLED,
    InMemoryTenantRepository,
    Tenant,
    TenantDenied,
    require_assignable,
)

ROOT = Path(__file__).resolve().parents[2]
T_KNOWN = "t-known"
T_OTHER = "t-other"


def _identity(**over) -> UserIdentity:
    base = dict(user_id="u-1", email="a@example.test", password_hash="scrypt$x",
                role="veterinarian", full_name="A", tenant_id=T_KNOWN,
                provenance=PROVENANCE_SEED)
    base.update(over)
    return UserIdentity(**base)


# ---------------------------------------------------------------------------
# In-memory
# ---------------------------------------------------------------------------

@pytest.fixture()
def mem():
    tenants = InMemoryTenantRepository()
    tenants.create(Tenant(tenant_id=T_KNOWN, display_name="Known"))
    return tenants, InMemoryIdentityRepository(tenants), InMemorySessionStore(tenants)


def test_positive_control_a_known_tenant_accepts_an_identity(mem):
    """Without this, a registry that refused everything would satisfy every
    negative control in this file."""
    _, identities, sessions = mem
    assert identities.create(_identity()).tenant_id == T_KNOWN
    assert sessions.create(user_id="u-1", tenant_id=T_KNOWN, role="owner",
                           ttl_seconds=60) is not None


def test_tenant_01_an_unknown_tenant_assignment_is_denied(mem):
    _, identities, _ = mem
    with pytest.raises(TenantDenied, match="not a known, assignable tenant"):
        identities.create(_identity(tenant_id="t-does-not-exist"))


def test_tenant_02_a_tenant_must_exist_before_a_tenant_scoped_session(mem):
    _, _, sessions = mem
    with pytest.raises(SessionDenied):
        sessions.create(user_id="u-1", tenant_id="t-does-not-exist",
                        role="owner", ttl_seconds=60)


def test_tenant_03_a_disabled_tenant_receives_no_new_identity(mem):
    tenants, identities, sessions = mem
    assert tenants.disable(T_KNOWN) is True
    assert tenants.get(T_KNOWN).status == TENANT_DISABLED
    with pytest.raises(TenantDenied):
        identities.create(_identity(user_id="u-2", email="b@example.test"))
    with pytest.raises(SessionDenied):
        sessions.create(user_id="u-1", tenant_id=T_KNOWN, role="owner", ttl_seconds=60)


def test_tenant_03b_disabling_is_recorded_never_a_deletion(mem):
    """A tenant that is removed cannot be shown to have been disabled rather
    than to have never existed."""
    tenants, _, _ = mem
    tenants.disable(T_KNOWN)
    still_there = tenants.get(T_KNOWN)
    assert still_there is not None
    assert still_there.disabled_at is not None


def test_tenant_03c_disabling_twice_reports_the_second_as_a_no_op(mem):
    tenants, _, _ = mem
    assert tenants.disable(T_KNOWN) is True
    assert tenants.disable(T_KNOWN) is False


def test_tenant_04_there_is_no_default_tenant(mem):
    """`platform` was the default a missing header once fell back to. It does
    not come back as a row, and it is not special."""
    tenants, identities, _ = mem
    assert tenants.get("platform") is None
    assert tenants.count() == 1
    with pytest.raises(TenantDenied):
        identities.create(_identity(tenant_id="platform"))


def test_tenant_05_nothing_infers_a_tenant_from_an_identity(mem):
    """Not from an email domain, not from a role, not from a name."""
    _, identities, _ = mem
    created = identities.create(_identity(
        user_id="u-nt", email="someone@t-known.example", tenant_id=None,
    ))
    assert created.tenant_id is None, "a tenant was inferred from the address"


def test_tenant_05b_a_null_tenant_remains_the_governed_absent_state(mem):
    """W0-C's legitimate state. A registry that forced every identity to hold a
    tenant would force callers to invent one — the outcome PRE-1 exists to
    prevent."""
    _, identities, sessions = mem
    identities.create(_identity(user_id="u-n", email="n@example.test", tenant_id=None))
    record = sessions.create(user_id="u-n", tenant_id=None, role="owner",
                             ttl_seconds=60)
    assert record.tenant_id is None


def test_tenant_09_a_missing_registry_fails_closed_rather_than_skipping_the_check():
    """A write path that silently skipped the check when the registry was absent
    would be a registry that stopped applying exactly when something was
    misconfigured."""
    with pytest.raises(TenantDenied, match="no tenant registry"):
        require_assignable(None, T_KNOWN)
    # ...but the governed ABSENT state still passes, because it asserts nothing
    # about a tenant.
    require_assignable(None, None)


# ---------------------------------------------------------------------------
# PostgreSQL
# ---------------------------------------------------------------------------

@pytest.fixture()
def pg(clean_postgres):
    pool = open_pool(clean_postgres, connect_timeout=5.0)
    tenants = PostgresTenantRepository(pool)
    tenants.create(Tenant(tenant_id=T_KNOWN, display_name="Known"))
    yield pool, tenants, PostgresIdentityRepository(pool, tenants), \
        PostgresSessionStore(pool, tenants), clean_postgres
    pool.close()


def test_the_registry_ships_empty(clean_postgres):
    """TENANT_ROWS_CREATED=0. The migration creates the shape and no contents."""
    with psycopg.connect(clean_postgres) as conn:
        assert conn.execute("SELECT count(*) FROM tenant").fetchone()[0] == 0
        # Specifically not the test-fixture identifiers PRE-1 declined to promote.
        for invented in ("tenant_jeddah_001", "tenant_riyadh_001", "platform"):
            assert conn.execute(
                "SELECT 1 FROM tenant WHERE tenant_id = %s", (invented,)
            ).fetchone() is None, f"the migration invented {invented}"


def test_tenant_08_the_foreign_key_refuses_an_unknown_tenant_structurally(pg):
    """The repository check could be removed; the constraint is what makes the
    rule structural. Asserted by writing SQL directly — the path a repair script
    or a future adapter would take."""
    pool, _, _, _, _ = pg
    with pytest.raises(pgerrors.ForeignKeyViolation) as exc:
        with pool.connection() as conn:
            conn.execute(
                "INSERT INTO user_identity (user_id,email,password_hash,role,"
                "full_name,tenant_id,provenance,created_at) "
                "VALUES ('u-fk','fk@example.test','h','owner','FK','t-nope',"
                "'SEED',CURRENT_TIMESTAMP)"
            )
    assert exc.value.sqlstate == "23503"


def test_tenant_08b_the_session_foreign_key_holds_too(pg):
    pool, _, identities, _, _ = pg
    identities.create(_identity())
    with pytest.raises(pgerrors.ForeignKeyViolation):
        with pool.connection() as conn:
            conn.execute(
                "INSERT INTO app_session (session_id,user_id,tenant_id,role,"
                "issued_at,expires_at) VALUES ('s-fk','u-1','t-nope','owner',"
                "CURRENT_TIMESTAMP, CURRENT_TIMESTAMP + INTERVAL '1 hour')"
            )


def test_tenant_01_pg_an_unknown_tenant_is_denied_by_the_repository(pg):
    _, _, identities, _, _ = pg
    with pytest.raises(TenantDenied):
        identities.create(_identity(tenant_id="t-nope"))


def test_tenant_03_pg_a_disabled_tenant_receives_no_new_identity(pg):
    """The rule a foreign key CANNOT express — the row still exists, so the
    constraint is satisfied and only the registry knows better."""
    pool, tenants, identities, sessions, _ = pg
    assert tenants.disable(T_KNOWN) is True
    with pytest.raises(TenantDenied):
        identities.create(_identity(user_id="u-dis", email="dis@example.test"))
    # ...and the row is still there, so the FK would have allowed it.
    with pool.connection() as conn:
        assert conn.execute(
            "SELECT status FROM tenant WHERE tenant_id = %s", (T_KNOWN,)
        ).fetchone()[0] == TENANT_DISABLED


def test_tenant_06_a_cross_tenant_session_cannot_resolve(pg):
    _, tenants, identities, sessions, _ = pg
    tenants.create(Tenant(tenant_id=T_OTHER, display_name="Other"))
    identities.create(_identity())
    record = sessions.create(user_id="u-1", tenant_id=T_KNOWN, role="owner",
                             ttl_seconds=60)
    assert sessions.get_active(record.session_id, tenant_id=T_KNOWN) is not None
    assert sessions.get_active(record.session_id, tenant_id=T_OTHER) is None


def test_tenant_07_a_cross_tenant_audit_read_is_refused(pg):
    """The tenant-scoped audit query cannot reach another tenant's events."""
    from audit_repository import PostgresAuditRepository

    pool, tenants, _, _, _ = pg
    tenants.create(Tenant(tenant_id=T_OTHER, display_name="Other"))
    audit = PostgresAuditRepository(pool)
    base = {"event_name": "e", "actor_id": "a", "actor_role": "owner",
            "clinic_id": None, "resource_type": "rt", "resource_id": "ri",
            "action_result": "ok", "reason_code": None, "correlation_id": "c",
            "occurred_at": "2026-01-01"}
    audit.append_event({**base, "audit_event_id": "e-known", "tenant_id": T_KNOWN})
    audit.append_event({**base, "audit_event_id": "e-other", "tenant_id": T_OTHER})

    got = audit.query_events_for_tenant(T_KNOWN, limit=50)
    assert [e["audit_event_id"] for e in got] == ["e-known"]
    assert audit.get_event("e-other", tenant_id=T_KNOWN) is None


def test_tenant_10_a_migration_cannot_create_the_tenant_it_needs(pg):
    """TENANT-10. The migration tool writes identities and nothing else, so a
    source record naming an unknown tenant fails on the foreign key rather than
    quietly creating a scope. Tenant authority is supplied deliberately, before
    a cutover, or the migration does not proceed."""
    sys.path.insert(0, str(ROOT / "scripts" / "governance"))
    import identity_migration_dryrun as tool

    _, _, _, _, url = pg
    scrypt = "scrypt$16384$8$1$" + "ab" * 16 + "$" + "cd" * 32
    record = tool.SourceRecord(
        source_record_id="s1", user_id="u-mig", email="mig@example.test",
        password_hash=scrypt, role="owner", tenant_id="t-unregistered",
        full_name="Mig",
    )
    migratable, quarantined, _ = tool.plan_migration([record], tenant_map=None)
    assert len(migratable) == 1, "the planner should map it; the DATABASE refuses it"

    with pytest.raises(Exception) as exc:
        tool.apply_to(url, migratable, quarantined)
    assert "ForeignKeyViolation" in type(exc.value).__name__ or \
        isinstance(exc.value, pgerrors.ForeignKeyViolation)

    with psycopg.connect(url) as conn:
        assert conn.execute("SELECT count(*) FROM user_identity").fetchone()[0] == 0

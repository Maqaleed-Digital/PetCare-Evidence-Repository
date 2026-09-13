"""The single-use first-`platform_admin` genesis act, proven on PostgreSQL.

Sponsor ruling of 12 September 2026,
`MYVETICARE FIRST PLATFORM ADMINISTRATOR GENESIS AUTHORITY`:

> GENESIS_AUTHORITY=SINGLE_USE
> GENERAL_PLATFORM_ADMIN_ELEVATION_AUTHORITY=NOT_AUTHORIZED
> GENESIS_REUSE=PROHIBITED
> SECOND_GENESIS_ATTEMPT=MUST_FAIL_CLOSED

Every control runs against real PostgreSQL, because the single-use property the
ruling requires is *"enforced by durable production state, not by operator
memory or documentation alone"* — a property an in-memory double cannot show.
"""
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

psycopg = pytest.importorskip("psycopg")

import main as api  # noqa: E402
import routers.auth as auth  # noqa: E402
from audit_repository import AuditWriteFailed  # noqa: E402
from persistence import MODE_POSTGRES, PERSISTENCE_MODE_ENV_VAR, build_persistence  # noqa: E402
from platform_admin_genesis import (  # noqa: E402
    EVENT_PLATFORM_ADMIN_GENESIS,
    GENESIS_ACTOR_ID,
    GENESIS_ACTOR_ROLE,
    RESOURCE_TYPE_GENESIS,
    GenesisDenied,
    GenesisUnavailable,
    PlatformAdminGenesisService,
)
from roles import ALLOWED_ROLES, ROLE_OWNER, ROLE_PLATFORM_ADMIN  # noqa: E402
from secret_provider import SECRET_MODE_ENV_VAR  # noqa: E402

ADMIN_USER_ID = "u-genesis-001"
ADMIN_EMAIL = "first.admin@test.invalid"
RULING = "MVC-GENESIS-PLATFORM-ADMIN-001"


@pytest.fixture()
def pg(clean_postgres):
    env = {SECRET_MODE_ENV_VAR: "environment",
           PERSISTENCE_MODE_ENV_VAR: MODE_POSTGRES}
    persistence = build_persistence(env, connection_url=clean_postgres)
    try:
        yield persistence
    finally:
        if persistence.pool is not None:
            persistence.pool.close()


def _execute(persistence, **overrides):
    kwargs = dict(
        user_id=ADMIN_USER_ID,
        email=ADMIN_EMAIL,
        password_hash=auth._hash_password("not-a-deployed-credential"),
        full_name="First Platform Administrator",
        ruling_reference=RULING,
        correlation_id="c-genesis",
    )
    kwargs.update(overrides)
    return PlatformAdminGenesisService(persistence).execute(**kwargs)


def _rows(url: str, sql: str, params=()):
    with psycopg.connect(url) as conn:
        return conn.execute(sql, params).fetchall()


def _count(url: str, sql: str, params=()) -> int:
    return _rows(url, sql, params)[0][0]


# ---------------------------------------------------------------------------
# G-01 — the genesis act establishes the first platform_admin
# ---------------------------------------------------------------------------

def test_g01_genesis_creates_the_first_platform_admin(pg):
    """§2: the resulting role is fixed by the governed procedure to
    `platform_admin`, and the identity must actually exist afterwards (§5)."""
    result = _execute(pg)

    assert result.user_id == ADMIN_USER_ID
    assert result.role == ROLE_PLATFORM_ADMIN

    stored = pg.identities.get_by_user_id(ADMIN_USER_ID)
    assert stored is not None, "genesis reported success but created no identity"
    assert stored.role == ROLE_PLATFORM_ADMIN
    assert stored.email == ADMIN_EMAIL


# ---------------------------------------------------------------------------
# G-02 — tenant context: platform scope is the ABSENCE of a tenant
# ---------------------------------------------------------------------------

def test_g02_the_genesis_admin_holds_no_tenant_and_creates_none(pg, clean_postgres):
    """§3: genesis *"must not create any additional tenant or infer any tenant
    value"*, and the governed production identity model represents
    platform scope as the absence of a tenant, never as a tenant that stands
    for everyone (TENANT-04/TENANT-09, `petcare_api/tenants.py`).

    Binding the first administrator to a tenant would also make genesis
    ordering-dependent on a `tenant` row that §9 does not authorize creating,
    because migration 0034 puts an FK from `user_identity.tenant_id` onto it.
    """
    _execute(pg)

    stored = pg.identities.get_by_user_id(ADMIN_USER_ID)
    assert stored.tenant_id is None, (
        "the first platform_admin was bound to a tenant; platform scope is the "
        "absence of one"
    )
    assert _count(clean_postgres, "SELECT count(*) FROM tenant") == 0, (
        "genesis created a tenant row"
    )


# ---------------------------------------------------------------------------
# G-03 — the genesis identity is distinguishable from every other origin
# ---------------------------------------------------------------------------

def test_g03_the_genesis_identity_carries_genesis_provenance(pg):
    """`SEED` is the category PRE-1 discarded as development artefacts and
    `REGISTRATION` is the invite-gated public path. Recording the first
    administrator as either would misdescribe how the highest privilege in the
    system came to exist, and §4 requires the genesis event to be identifiable
    as a genesis event rather than disguised as an ordinary one."""
    from repositories import PROVENANCE_GENESIS

    _execute(pg)

    stored = pg.identities.get_by_user_id(ADMIN_USER_ID)
    assert stored.provenance == PROVENANCE_GENESIS
    assert PROVENANCE_GENESIS not in ("SEED", "REGISTRATION", "IDENTITY_MIGRATION")


# ---------------------------------------------------------------------------
# G-04 — the governed genesis audit record
# ---------------------------------------------------------------------------

def test_g04_genesis_writes_one_governed_audit_event(pg, clean_postgres):
    """§4 requires the record to identify: that this is a first-administrator
    genesis event, the target identity, the resulting role, the tenant context,
    the governing ruling, the timestamp, and the result."""
    result = _execute(pg)

    events = pg.audit.all_events()
    genesis = [e for e in events if e["event_name"] == EVENT_PLATFORM_ADMIN_GENESIS]
    assert len(genesis) == 1, f"expected exactly one genesis event, got {len(genesis)}"
    event = genesis[0]

    assert event["audit_event_id"] == result.audit_event_id
    assert event["resource_type"] == RESOURCE_TYPE_GENESIS
    assert event["resource_id"] == ADMIN_USER_ID, "the target identity is not named"
    assert event["action_result"] == "success", "the result of the act is not recorded"
    assert RULING in (event["reason_code"] or ""), "the governing ruling is not recorded"
    assert event["occurred_at"], "the execution timestamp is not recorded"
    assert ROLE_PLATFORM_ADMIN in event["event_name"], (
        "the resulting role is not identifiable from the governed field set"
    )
    assert _count(clean_postgres, "SELECT count(*) FROM audit_event") == 1


def test_g05_the_genesis_event_actor_is_unattributed_and_never_invented(pg):
    """§4: *"the genesis event has no prior governed human actor… The absence of
    a prior human actor must not be disguised by inventing an actor identity."*

    INVENTED_ACTOR=PROHIBITED. The actor role must also never be a value
    `require_role()` would accept, or the record would read as an act by a
    principal that did not exist.
    """
    _execute(pg)

    event = [e for e in pg.audit.all_events()
             if e["event_name"] == EVENT_PLATFORM_ADMIN_GENESIS][0]

    assert event["actor_id"] == GENESIS_ACTOR_ID
    assert event["actor_role"] == GENESIS_ACTOR_ROLE
    assert event["actor_id"] != ADMIN_USER_ID, (
        "the genesis event names its own target as the actor, which invents a "
        "prior human actor that did not exist"
    )
    assert event["actor_id"] != ADMIN_EMAIL
    assert GENESIS_ACTOR_ROLE not in ALLOWED_ROLES, (
        "the unattributed actor role is a real authority token"
    )


def test_g06_the_genesis_event_carries_the_unattributed_tenant(pg):
    """The first administrator holds no tenant, and `audit_event.tenant_id` is
    `TEXT NOT NULL` with deliberately no FK (0034). `UNATTRIBUTED` is the
    representation the estate already uses for exactly this — a governed event
    with no tenant perimeter — so no tenant is invented to carry the record."""
    _execute(pg)

    event = [e for e in pg.audit.all_events()
             if e["event_name"] == EVENT_PLATFORM_ADMIN_GENESIS][0]

    assert event["tenant_id"] == api.UNATTRIBUTED_TENANT


def test_g07_the_genesis_event_leaves_the_audit_chain_verifiable(pg):
    """An event that broke the chain would be reported as tampering forever
    after — the act that establishes the administrator must not be the act that
    invalidates the log."""
    _execute(pg)

    assert pg.audit.verify_chain()["ok"] is True


# ---------------------------------------------------------------------------
# G-08 … G-12 — the durable single-use property
# ---------------------------------------------------------------------------

def test_g08_the_consumption_record_is_written(pg, clean_postgres):
    """§5: *"the genesis authority is marked consumed"*, in durable state."""
    result = _execute(pg)

    rows = _rows(
        clean_postgres,
        "SELECT target_user_id, granted_role, ruling_reference, audit_event_id "
        "FROM platform_admin_genesis",
    )
    assert len(rows) == 1
    target, role, ruling, event_id = rows[0]
    assert target == ADMIN_USER_ID
    assert role == ROLE_PLATFORM_ADMIN
    assert ruling == RULING
    assert event_id == result.audit_event_id, (
        "the consumption record does not name the governed audit event"
    )


def test_g09_a_second_genesis_attempt_fails_closed(pg, clean_postgres):
    """§5: GENESIS_REUSE=PROHIBITED, SECOND_GENESIS_ATTEMPT=MUST_FAIL_CLOSED.

    The second attempt uses a DIFFERENT identity on purpose: refusing to
    recreate the same user is ordinary idempotence, while refusing to create a
    second, different administrator is the property the ruling asks for.
    """
    _execute(pg)

    with pytest.raises(GenesisDenied):
        _execute(pg, user_id="u-genesis-002", email="second@test.invalid")

    assert pg.identities.get_by_user_id("u-genesis-002") is None
    assert _count(
        clean_postgres,
        "SELECT count(*) FROM user_identity WHERE role = %s", (ROLE_PLATFORM_ADMIN,),
    ) == 1, "a second platform_admin was created"
    assert _count(clean_postgres, "SELECT count(*) FROM platform_admin_genesis") == 1
    assert _count(clean_postgres, "SELECT count(*) FROM audit_event") == 1, (
        "the refused second attempt still wrote an audit event"
    )


def test_g10_genesis_refuses_when_a_platform_admin_already_exists(pg, clean_postgres):
    """§5: the procedure must prove *"that no governed production
    `platform_admin` already exists"* — a separate precondition from the
    consumption record, and the one that holds when an administrator arrived by
    some other route entirely."""
    saved = (auth.PERSISTENCE, auth.IDENTITY_REPO)
    auth.PERSISTENCE, auth.IDENTITY_REPO = pg, pg.identities
    try:
        auth.seed_user("u-other-admin", "other@test.invalid", "pw",
                       ROLE_PLATFORM_ADMIN)
    finally:
        auth.PERSISTENCE, auth.IDENTITY_REPO = saved

    assert _count(clean_postgres, "SELECT count(*) FROM platform_admin_genesis") == 0, (
        "precondition: the genesis authority must still be unconsumed here"
    )

    with pytest.raises(GenesisDenied):
        _execute(pg)

    assert pg.identities.get_by_user_id(ADMIN_USER_ID) is None
    assert _count(clean_postgres, "SELECT count(*) FROM platform_admin_genesis") == 0


def test_g11_the_single_use_property_is_enforced_by_the_database(clean_postgres):
    """§5: *"enforced by durable production state, not by operator memory or
    documentation alone."*

    Asserted against the schema directly, bypassing the service entirely. A
    guarantee that exists only inside the one function everybody is asked to
    use is not a guarantee about the database.
    """
    with psycopg.connect(clean_postgres) as conn:
        conn.execute(
            "INSERT INTO user_identity (user_id, email, password_hash, role, "
            "full_name, provenance) VALUES (%s, %s, %s, %s, %s, 'GENESIS')",
            ("u-direct-1", "d1@test.invalid", "h", ROLE_PLATFORM_ADMIN, "D1"),
        )
        with pytest.raises(psycopg.errors.UniqueViolation):
            conn.execute(
                "INSERT INTO user_identity (user_id, email, password_hash, role, "
                "full_name, provenance) VALUES (%s, %s, %s, %s, %s, 'GENESIS')",
                ("u-direct-2", "d2@test.invalid", "h", ROLE_PLATFORM_ADMIN, "D2"),
            )

    with psycopg.connect(clean_postgres) as conn:
        conn.execute(
            "INSERT INTO user_identity (user_id, email, password_hash, role, "
            "full_name, provenance) VALUES (%s, %s, %s, %s, %s, 'GENESIS')",
            ("u-direct-1", "d1@test.invalid", "h", ROLE_PLATFORM_ADMIN, "D1"),
        )
        conn.execute(
            "INSERT INTO platform_admin_genesis (target_user_id, granted_role, "
            "ruling_reference, audit_event_id) VALUES (%s, %s, %s, %s)",
            ("u-direct-1", ROLE_PLATFORM_ADMIN, RULING, "e-1"),
        )
        with pytest.raises(psycopg.errors.UniqueViolation):
            conn.execute(
                "INSERT INTO platform_admin_genesis (target_user_id, granted_role, "
                "ruling_reference, audit_event_id) VALUES (%s, %s, %s, %s)",
                ("u-direct-1", ROLE_PLATFORM_ADMIN, RULING, "e-2"),
            )


def test_g12_the_consumption_record_cannot_describe_another_role(clean_postgres):
    """§2: the procedure must not be *"capable of creating any other privileged
    role"*. A ledger that could record one would describe an act the ruling
    does not authorize, whatever the service happened to do."""
    with psycopg.connect(clean_postgres) as conn:
        conn.execute(
            "INSERT INTO user_identity (user_id, email, password_hash, role, "
            "full_name, provenance) VALUES (%s, %s, %s, %s, %s, 'SEED')",
            ("u-x", "x@test.invalid", "h", ROLE_OWNER, "X"),
        )
        with pytest.raises(psycopg.errors.CheckViolation):
            conn.execute(
                "INSERT INTO platform_admin_genesis (target_user_id, granted_role, "
                "ruling_reference, audit_event_id) VALUES (%s, %s, %s, %s)",
                ("u-x", ROLE_OWNER, RULING, "e-1"),
            )


# ---------------------------------------------------------------------------
# G-13 … G-15 — §6 transaction and failure semantics
# ---------------------------------------------------------------------------

def test_g13_an_audit_failure_leaves_no_privileged_identity(pg, clean_postgres, monkeypatch):
    """§6: a failure must not leave *"a privileged identity without the
    corresponding governed genesis audit record"*."""
    def refuse(*_a, **_k):
        raise AuditWriteFailed("audit store refused the genesis record")

    monkeypatch.setattr(pg.audit, "append_event_on", refuse)

    with pytest.raises((AuditWriteFailed, GenesisDenied)):
        _execute(pg)

    assert pg.identities.get_by_user_id(ADMIN_USER_ID) is None, (
        "a platform_admin exists with no genesis audit record"
    )
    assert _count(clean_postgres, "SELECT count(*) FROM platform_admin_genesis") == 0
    assert _count(clean_postgres, "SELECT count(*) FROM audit_event") == 0


def test_g14_a_consumption_record_failure_rolls_back_the_whole_act(pg, clean_postgres):
    """§6, the other direction: no audit record may claim *"creation of an
    administrator that was not created"*.

    The collision is provoked with a consumption record that already exists and
    names an identity that is not a `platform_admin`, so the service's own
    "an administrator already exists" precondition is NOT what refuses this —
    the durable single-use state is.
    """
    with psycopg.connect(clean_postgres, autocommit=True) as conn:
        conn.execute(
            "INSERT INTO user_identity (user_id, email, password_hash, role, "
            "full_name, provenance) VALUES (%s, %s, %s, %s, %s, 'SEED')",
            ("u-placeholder", "p@test.invalid", "h", ROLE_OWNER, "P"),
        )
        conn.execute(
            "INSERT INTO platform_admin_genesis (target_user_id, granted_role, "
            "ruling_reference, audit_event_id) VALUES (%s, %s, %s, %s)",
            ("u-placeholder", ROLE_PLATFORM_ADMIN, RULING, "e-prior"),
        )

    with pytest.raises(GenesisDenied):
        _execute(pg)

    assert pg.identities.get_by_user_id(ADMIN_USER_ID) is None
    assert _count(clean_postgres, "SELECT count(*) FROM audit_event") == 0, (
        "an audit record claims an administrator that was not created"
    )
    assert _count(clean_postgres, "SELECT count(*) FROM platform_admin_genesis") == 1


def test_g15_genesis_fails_closed_without_a_durable_store():
    """§6: if persistence cannot be established the operation fails closed. A
    genesis act that died with the process would establish an administrator
    nobody could later prove was authorized."""
    env = {SECRET_MODE_ENV_VAR: "environment", PERSISTENCE_MODE_ENV_VAR: "memory"}
    persistence = build_persistence(env)

    with pytest.raises(GenesisUnavailable):
        _execute(persistence)


# ---------------------------------------------------------------------------
# G-16 … G-18 — the credential, the blast radius, the readback
# ---------------------------------------------------------------------------

def test_g16_genesis_refuses_to_invent_a_credential(pg, clean_postgres):
    """§2: *"This ruling does not authorize inventing, embedding, or storing a
    default credential."* An absent credential must be a refusal, never a
    fallback — a default administrator password is the exact defect PRE-1
    discarded three seed identities over."""
    for blank in ("", "   "):
        with pytest.raises(GenesisDenied):
            _execute(pg, password_hash=blank)

    assert _count(clean_postgres, "SELECT count(*) FROM user_identity") == 0
    assert _count(clean_postgres, "SELECT count(*) FROM platform_admin_genesis") == 0


def test_g17_genesis_creates_exactly_one_identity_and_no_other(pg, clean_postgres):
    """§5: *"no additional privileged identity may have been created by the
    genesis operation."*"""
    _execute(pg)

    assert _count(clean_postgres, "SELECT count(*) FROM user_identity") == 1
    assert _count(
        clean_postgres,
        "SELECT count(*) FROM user_identity WHERE role = %s", (ROLE_PLATFORM_ADMIN,),
    ) == 1
    assert _count(clean_postgres, "SELECT count(*) FROM app_session") == 0, (
        "genesis signed the new administrator in; establishing an identity is "
        "not establishing a session"
    )


def test_g18_the_readback_path_confirms_the_intended_administrator(pg):
    """§5: *"the system must verify that the intended first platform
    administrator exists."*"""
    service = PlatformAdminGenesisService(pg)
    assert service.read_genesis_admin() is None

    _execute(pg)

    found = service.read_genesis_admin()
    assert found is not None
    assert found.user_id == ADMIN_USER_ID
    assert found.role == ROLE_PLATFORM_ADMIN

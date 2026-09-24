"""PostgreSQL implementations of the serving-layer persistence boundary.

`MVC-W0F-DATA-STORE-DECISION-001` names the class of store; migration
`0031_w0f_identity_session_persistence.sql` defines the schema. This module is
the adapter between them and the protocols in `repositories.py` /
`session_store.py`.

## Two rules that shape everything below

**1 · No location appears here.** No region, no endpoint, no account. The
connection URL arrives from `secret_provider.resolve_database_url()`, which reads
it from the governed secret source. That is D.21's portability rule as code: the
mandatory KSA migration repoints configuration and this file is untouched.

**2 · The semantics are the in-memory ones, not new ones.** Every control in
`test_session_revocation.py` was written against `InMemorySessionStore`. If this
class answered differently anywhere — cross-tenant, already-revoked, expiry
boundary — the suite would still be green and production would behave
differently from everything that was ever tested. The two implementations are
run against the same controls for exactly that reason.

## Time

Everything is written as UTC and read back as UTC. The schema uses `TIMESTAMP`
(no zone), matching the thirty migrations that precede it, so the invariant has
to be maintained by this module rather than by the column type: every write
converts to UTC and drops the zone, every read re-attaches it. The connection
also sets its session time zone to UTC, so that `CURRENT_TIMESTAMP` defaults in
the schema agree with values this module writes — otherwise a server running in
a local zone would stamp `created_at` hours away from `issued_at` on the same
row, and the difference would look like a clock problem rather than a
configuration one.
"""
from __future__ import annotations

import secrets
from datetime import datetime, timedelta, timezone
from typing import Any, Iterable, Optional
from uuid import uuid4

from repositories import (
    InviteCode,
    RepositoryDenied,
    UserIdentity,
    validate_identity,
)
from session_store import SessionDenied, SessionRecord


class PersistenceUnavailable(RuntimeError):
    """The configured store could not be reached.

    Its own type, because the one thing that must never happen when persistence
    is unavailable is a silent fall back to memory — and an exception that is
    indistinguishable from an ordinary error invites a broad `except` that does
    exactly that.
    """


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _to_db(value: Optional[datetime]) -> Optional[datetime]:
    """A tz-aware datetime as the naive-UTC value the column stores."""
    if value is None:
        return None
    if value.tzinfo is None:
        return value
    return value.astimezone(timezone.utc).replace(tzinfo=None)


def _from_db(value: Optional[datetime]) -> Optional[datetime]:
    """A stored naive value read back as the tz-aware UTC it always was."""
    if value is None:
        return None
    if value.tzinfo is not None:
        return value.astimezone(timezone.utc)
    return value.replace(tzinfo=timezone.utc)


# ---------------------------------------------------------------------------
# Connection
# ---------------------------------------------------------------------------

def open_pool(
    connection_url: str, *, min_size: int = 1, max_size: int = 8,
    connect_timeout: float = 10.0,
) -> Any:
    """A connection pool, opened eagerly so failure happens at startup.

    Eager is the whole point. A lazily-opened pool turns an unreachable database
    into a per-request failure discovered by the first user, at which point the
    process is already serving and reporting itself healthy. Opening here means
    a process that cannot reach its store does not start — the same fail-closed
    shape W0-A established for the signing key.

    A single direct connection is attempted FIRST, before the pool. Two reasons,
    and the second is the one that matters:

      * the pool retries with backoff until its timeout, so an outright refusal
        would otherwise take as long to report as a slow network — and a
        deployment reads those two situations very differently;
      * the probe's exception is the real one. The pool reports that it could not
        reach min_size connections, which says nothing about whether the host was
        unreachable, the credential rejected, or the database absent.
    """
    try:
        import psycopg
        from psycopg_pool import ConnectionPool
    except ImportError as exc:
        raise PersistenceUnavailable(
            "the PostgreSQL driver is not installed; the configured persistence "
            "mode cannot be served and there is no fallback"
        ) from exc

    try:
        with psycopg.connect(connection_url, connect_timeout=connect_timeout) as probe:
            probe.execute("SELECT 1")
    except Exception as exc:
        # Deliberately does not carry the driver message forward: a libpq error
        # can quote the connection string, and this exception reaches logs.
        raise PersistenceUnavailable(
            f"the configured data store could not be reached "
            f"({type(exc).__name__}); refusing to serve from memory instead"
        ) from None

    def _configure(conn: Any) -> None:
        """UTC for every pooled connection; see the module docstring on time.

        The COMMIT is required, not decorative. A pooled connection is not in
        autocommit, so the SET opens a transaction, and the pool discards any
        connection a configure hook leaves open — which it does silently, then
        retries, then reports a pool timeout. The visible symptom is "the
        database is unreachable" while the database is perfectly reachable.
        """
        conn.execute("SET TIME ZONE 'UTC'")
        conn.commit()

    try:
        pool = ConnectionPool(
            conninfo=connection_url,
            min_size=min_size,
            max_size=max_size,
            open=True,
            timeout=connect_timeout,
            configure=_configure,
        )
        pool.wait(timeout=connect_timeout)
    except Exception as exc:
        raise PersistenceUnavailable(
            f"the configured data store could not be pooled "
            f"({type(exc).__name__}); refusing to serve from memory instead"
        ) from None
    return pool


# ---------------------------------------------------------------------------
# Sessions
# ---------------------------------------------------------------------------

class PostgresSessionStore:
    """`SessionStore`, backed by `app_session`.

    Durability is what W0-F adds. The revocation semantics are unchanged from
    `InMemorySessionStore` and are asserted to be unchanged by running the same
    controls against both.
    """

    def __init__(self, pool: Any, tenants: Any) -> None:
        self._pool = pool
        #: The tenant registry. The foreign key migration 0034 adds already
        #: enforces existence; this adds the rule a foreign key cannot express —
        #: that a DISABLED tenant receives no new session — and reports a reason
        #: rather than a constraint name.
        #: REQUIRED, and deliberately without a default.
        #:
        #: `tests/governance/test_tenant_scope_signatures.py` forbids a
        #: tenant-bearing parameter that may be omitted, and it is right to: a
        #: registry that could be left out is one that gets left out. Passing
        #: `None` explicitly is still allowed and still fails closed — see
        #: `tenants.require_assignable` — but it becomes a decision at the call
        #: site rather than an omission.
        self._tenants = tenants

    # -- writes ----------------------------------------------------------

    def create(
        self, *, user_id: str, tenant_id: Optional[str], role: str, ttl_seconds: int
    ) -> SessionRecord:
        # The same distinction the in-memory store draws, refused at the same
        # point: None is a legitimate absent assignment, "" is a lost value.
        if tenant_id is not None and not tenant_id.strip():
            raise SessionDenied("a session cannot be created with a blank tenant")
        # A session is a tenant-scoped assignment like any other (TENANT-02).
        from tenants import TenantDenied, require_assignable

        try:
            require_assignable(self._tenants, tenant_id)
        except TenantDenied as exc:
            raise SessionDenied(str(exc)) from None
        now = _utc_now()
        record = SessionRecord(
            session_id=secrets.token_urlsafe(32),
            user_id=user_id,
            tenant_id=tenant_id,
            role=role,
            issued_at=now,
            expires_at=now + timedelta(seconds=ttl_seconds),
        )
        try:
            with self._pool.connection() as conn:
                conn.execute(
                    "INSERT INTO app_session "
                    "(session_id, user_id, tenant_id, role, issued_at, expires_at) "
                    "VALUES (%s, %s, %s, %s, %s, %s)",
                    (
                        record.session_id, record.user_id, record.tenant_id,
                        record.role, _to_db(record.issued_at), _to_db(record.expires_at),
                    ),
                )
        except Exception as exc:
            # A session that could not be recorded must not be handed out: the
            # cookie would name a session id that does not exist, and
            # read_session would deny every subsequent request with a reason
            # that points at revocation rather than at this write.
            raise SessionDenied(
                f"the session could not be recorded ({type(exc).__name__}); no "
                "cookie is minted for a session that does not exist"
            ) from None
        return record

    def revoke(self, session_id: str, *, tenant_id: str) -> bool:
        """Revoke one session. False when nothing was revoked.

        A single conditional UPDATE rather than read-then-write: two concurrent
        revocations of the same session would otherwise both read it active and
        both report success, and `revoke` is the operation an incident response
        depends on reporting truthfully.
        """
        with self._pool.connection() as conn:
            cur = conn.execute(
                "UPDATE app_session SET revoked_at = %s "
                "WHERE session_id = %s "
                "  AND tenant_id IS NOT DISTINCT FROM %s "
                "  AND revoked_at IS NULL",
                (_to_db(_utc_now()), session_id, tenant_id),
            )
            return cur.rowcount == 1

    def revoke_all_for_user(self, user_id: str, *, tenant_id: str) -> int:
        """Revoke every ACTIVE session for one user within one tenant."""
        now = _utc_now()
        with self._pool.connection() as conn:
            cur = conn.execute(
                "UPDATE app_session SET revoked_at = %s "
                "WHERE user_id = %s "
                "  AND tenant_id IS NOT DISTINCT FROM %s "
                "  AND revoked_at IS NULL "
                "  AND expires_at > %s",
                (_to_db(now), user_id, tenant_id, _to_db(now)),
            )
            return cur.rowcount

    # -- reads -----------------------------------------------------------

    def get_active(
        self, session_id: str, *, tenant_id: Optional[str]
    ) -> Optional[SessionRecord]:
        """The session, only if it exists, matches the tenant, and is live.

        `IS NOT DISTINCT FROM` rather than `=`: a tenantless identity has a NULL
        tenant, and `NULL = NULL` is NULL, so an equality comparison would deny
        every tenantless session — which W0-C requires to reach the route and be
        refused there with 403 NO_TENANT_AUTHORITY, not denied here with a 401.

        Unknown, revoked, expired and cross-tenant return None alike; the caller
        is not told which, and does not need to be.
        """
        now = _utc_now()
        with self._pool.connection() as conn:
            row = conn.execute(
                "SELECT session_id, user_id, tenant_id, role, issued_at, "
                "       expires_at, revoked_at "
                "FROM app_session "
                "WHERE session_id = %s "
                "  AND tenant_id IS NOT DISTINCT FROM %s "
                "  AND expires_at > %s "
                "  AND (revoked_at IS NULL OR revoked_at > %s)",
                (session_id, tenant_id, _to_db(now), _to_db(now)),
            ).fetchone()
        return _row_to_session(row) if row else None

    # -- introspection, for tests and operations --------------------------

    def all_for_user(self, user_id: str, *, tenant_id: str) -> Iterable[SessionRecord]:
        with self._pool.connection() as conn:
            rows = conn.execute(
                "SELECT session_id, user_id, tenant_id, role, issued_at, "
                "       expires_at, revoked_at "
                "FROM app_session "
                "WHERE user_id = %s AND tenant_id IS NOT DISTINCT FROM %s "
                "ORDER BY issued_at",
                (user_id, tenant_id),
            ).fetchall()
        return [_row_to_session(r) for r in rows]

    def describe(self, session_id: str) -> Optional[SessionRecord]:
        """The record whatever its state — including revoked and expired.

        Needed to tell apart "denied because the signature failed" from "denied
        because the record is gone". AC7-07 turns on exactly that distinction:
        the store record must be observably ACTIVE while the request is denied,
        or the denial proves nothing about signature verification.
        """
        with self._pool.connection() as conn:
            row = conn.execute(
                "SELECT session_id, user_id, tenant_id, role, issued_at, "
                "       expires_at, revoked_at "
                "FROM app_session WHERE session_id = %s",
                (session_id,),
            ).fetchone()
        return _row_to_session(row) if row else None


def _row_to_session(row: Any) -> SessionRecord:
    return SessionRecord(
        session_id=row[0],
        user_id=row[1],
        tenant_id=row[2],
        role=row[3],
        issued_at=_from_db(row[4]),
        expires_at=_from_db(row[5]),
        revoked_at=_from_db(row[6]),
    )


# ---------------------------------------------------------------------------
# Identity
# ---------------------------------------------------------------------------

_IDENTITY_COLUMNS = (
    "user_id, email, password_hash, role, full_name, tenant_id, "
    "provenance, source_record_id, created_at, disabled_at"
)


def _row_to_identity(row: Any) -> UserIdentity:
    return UserIdentity(
        user_id=row[0], email=row[1], password_hash=row[2], role=row[3],
        full_name=row[4], tenant_id=row[5], provenance=row[6],
        source_record_id=row[7], created_at=_from_db(row[8]),
        disabled_at=_from_db(row[9]),
    )


class PostgresIdentityRepository:
    def __init__(self, pool: Any, tenants: Any) -> None:
        self._pool = pool
        #: See PostgresSessionStore.__init__ — same reasoning, same registry.
        #: REQUIRED, and deliberately without a default.
        #:
        #: `tests/governance/test_tenant_scope_signatures.py` forbids a
        #: tenant-bearing parameter that may be omitted, and it is right to: a
        #: registry that could be left out is one that gets left out. Passing
        #: `None` explicitly is still allowed and still fails closed — see
        #: `tenants.require_assignable` — but it becomes a decision at the call
        #: site rather than an omission.
        self._tenants = tenants

    def _require_assignable_tenant(self, tenant_id: Optional[str]) -> None:
        from tenants import require_assignable

        require_assignable(self._tenants, tenant_id)

    def get_by_email(self, email: str) -> Optional[UserIdentity]:
        with self._pool.connection() as conn:
            row = conn.execute(
                f"SELECT {_IDENTITY_COLUMNS} FROM user_identity WHERE email = %s",
                (email,),
            ).fetchone()
        return _row_to_identity(row) if row else None

    def get_by_user_id(self, user_id: str) -> Optional[UserIdentity]:
        with self._pool.connection() as conn:
            row = conn.execute(
                f"SELECT {_IDENTITY_COLUMNS} FROM user_identity WHERE user_id = %s",
                (user_id,),
            ).fetchone()
        return _row_to_identity(row) if row else None

    def upsert(self, identity: UserIdentity) -> UserIdentity:
        """Write, replacing a row with the same user_id. Seeding only.

        `ON CONFLICT (user_id)` and not `(email)`: the identifier is the identity.
        Conflating them would let a re-seed silently rebind an existing user_id to
        a different address.
        """
        validate_identity(identity)
        self._require_assignable_tenant(identity.tenant_id)
        created = identity.created_at or _utc_now()
        with self._pool.connection() as conn:
            conn.execute(
                "INSERT INTO user_identity "
                f"({_IDENTITY_COLUMNS}) "
                "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) "
                "ON CONFLICT (user_id) DO UPDATE SET "
                "  email = EXCLUDED.email, "
                "  password_hash = EXCLUDED.password_hash, "
                "  role = EXCLUDED.role, "
                "  full_name = EXCLUDED.full_name, "
                "  tenant_id = EXCLUDED.tenant_id",
                (
                    identity.user_id, identity.email, identity.password_hash,
                    identity.role, identity.full_name, identity.tenant_id,
                    identity.provenance, identity.source_record_id,
                    _to_db(created), _to_db(identity.disabled_at),
                ),
            )
        return self.get_by_user_id(identity.user_id) or identity

    def create(self, identity: UserIdentity) -> UserIdentity:
        """Write a NEW identity. The database decides, not a prior read.

        A `SELECT ... then INSERT` would let two simultaneous registrations of
        the same address both find nothing and both proceed; the UNIQUE
        constraint is what actually prevents it, so the conflict is caught here
        rather than pre-empted.
        """
        validate_identity(identity)
        self._require_assignable_tenant(identity.tenant_id)
        created = identity.created_at or _utc_now()
        try:
            with self._pool.connection() as conn:
                conn.execute(
                    f"INSERT INTO user_identity ({_IDENTITY_COLUMNS}) "
                    "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                    (
                        identity.user_id, identity.email, identity.password_hash,
                        identity.role, identity.full_name, identity.tenant_id,
                        identity.provenance, identity.source_record_id,
                        _to_db(created), _to_db(identity.disabled_at),
                    ),
                )
        except Exception as exc:
            raise RepositoryDenied(
                f"the identity could not be created ({type(exc).__name__}); it is "
                "not overwritten and no partial row is left behind"
            ) from None
        return self.get_by_user_id(identity.user_id) or identity

    def set_password_hash(self, user_id: str, password_hash: str) -> None:
        with self._pool.connection() as conn:
            cur = conn.execute(
                "UPDATE user_identity SET password_hash = %s WHERE user_id = %s",
                (password_hash, user_id),
            )
            if cur.rowcount != 1:
                raise RepositoryDenied(f"no identity with id {user_id!r}")

    def count(self) -> int:
        with self._pool.connection() as conn:
            return conn.execute("SELECT count(*) FROM user_identity").fetchone()[0]


# ---------------------------------------------------------------------------
# Invite codes
# ---------------------------------------------------------------------------

class PostgresInviteCodeRepository:
    def __init__(self, pool: Any) -> None:
        self._pool = pool

    def get(self, code: str) -> Optional[InviteCode]:
        with self._pool.connection() as conn:
            row = conn.execute(
                "SELECT code, allowed_role, tenant_id, expires_at, consumed_at, "
                "       consumed_by FROM invite_code WHERE code = %s",
                (code,),
            ).fetchone()
        if not row:
            return None
        return InviteCode(
            code=row[0], allowed_role=row[1], tenant_id=row[2],
            expires_at=_from_db(row[3]), consumed_at=_from_db(row[4]),
            consumed_by=row[5],
        )

    def upsert(self, invite: InviteCode) -> InviteCode:
        """Seed or update a code — WITHOUT resetting its consumption.

        The omission is the control. Re-seeding at startup is exactly when a
        consumed pilot code would be handed back if this statement wrote
        `consumed_at = NULL`, and the restart that did it would look like
        ordinary lifecycle. The columns are simply not in the update list.
        """
        try:
            with self._pool.connection() as conn:
                conn.execute(
                    "INSERT INTO invite_code "
                    "(code, allowed_role, tenant_id, expires_at) "
                    "VALUES (%s, %s, %s, %s) "
                    "ON CONFLICT (code) DO UPDATE SET "
                    "  allowed_role = EXCLUDED.allowed_role, "
                    "  tenant_id = EXCLUDED.tenant_id, "
                    "  expires_at = EXCLUDED.expires_at",
                    (invite.code, invite.allowed_role, invite.tenant_id,
                     _to_db(invite.expires_at)),
                )
        except Exception as exc:
            raise RepositoryDenied(
                f"invite code {invite.code!r} was refused ({type(exc).__name__})"
            ) from None
        return self.get(invite.code) or invite

    def consume(self, code: str, *, email: str, at: Optional[datetime] = None) -> bool:
        with self._pool.connection() as conn:
            cur = conn.execute(
                "UPDATE invite_code SET consumed_at = %s, consumed_by = %s "
                "WHERE code = %s AND consumed_at IS NULL",
                (_to_db(at or _utc_now()), email, code),
            )
            return cur.rowcount == 1


# ---------------------------------------------------------------------------
# Quarantine — written by the identity migration, read by reconciliation
# ---------------------------------------------------------------------------

class PostgresQuarantineRepository:
    def __init__(self, pool: Any) -> None:
        self._pool = pool

    def record(
        self, *, source_record_id: str, reason: str,
        source_role: Optional[str] = None, source_tenant: Optional[str] = None,
        source_email: Optional[str] = None,
    ) -> None:
        with self._pool.connection() as conn:
            conn.execute(
                "INSERT INTO identity_migration_quarantine "
                "(source_record_id, reason, source_role, source_tenant, source_email) "
                "VALUES (%s, %s, %s, %s, %s) "
                "ON CONFLICT (source_record_id) DO NOTHING",
                (source_record_id, reason, source_role, source_tenant, source_email),
            )

    def count(self) -> int:
        with self._pool.connection() as conn:
            return conn.execute(
                "SELECT count(*) FROM identity_migration_quarantine"
            ).fetchone()[0]

    def all_reasons(self) -> dict[str, int]:
        with self._pool.connection() as conn:
            rows = conn.execute(
                "SELECT reason, count(*) FROM identity_migration_quarantine "
                "GROUP BY reason ORDER BY reason"
            ).fetchall()
        return {r[0]: r[1] for r in rows}


# ---------------------------------------------------------------------------
# Tenants
# ---------------------------------------------------------------------------

class PostgresTenantRepository:
    """`TenantRepository` backed by the `tenant` table (migration 0034).

    The foreign keys enforce EXISTENCE structurally. This class adds the rule a
    foreign key cannot express — that a DISABLED tenant may not receive a new
    assignment — and gives the caller a reason rather than a constraint name.
    """

    def __init__(self, pool: Any) -> None:
        self._pool = pool

    def get(self, tenant_id: str):
        from tenants import Tenant

        with self._pool.connection() as conn:
            row = conn.execute(
                "SELECT tenant_id, display_name, status, created_at, disabled_at "
                "FROM tenant WHERE tenant_id = %s", (tenant_id,),
            ).fetchone()
        if not row:
            return None
        return Tenant(tenant_id=row[0], display_name=row[1], status=row[2],
                      created_at=_from_db(row[3]), disabled_at=_from_db(row[4]))

    def create(self, tenant):
        from tenants import TenantDenied, validate_tenant

        validate_tenant(tenant)
        try:
            with self._pool.connection() as conn:
                conn.execute(
                    "INSERT INTO tenant (tenant_id, display_name, status, "
                    "created_at, disabled_at) VALUES (%s,%s,%s,%s,%s)",
                    (tenant.tenant_id, tenant.display_name, tenant.status,
                     _to_db(tenant.created_at or _utc_now()),
                     _to_db(tenant.disabled_at)),
                )
        except Exception as exc:
            raise TenantDenied(
                f"tenant {tenant.tenant_id!r} was refused ({type(exc).__name__})"
            ) from None
        return self.get(tenant.tenant_id) or tenant

    def disable(self, tenant_id: str, *, at: Optional[datetime] = None) -> bool:
        """A single conditional UPDATE. Two concurrent disables must not both
        report success — a disable is the operation an incident response relies
        on reporting truthfully."""
        with self._pool.connection() as conn:
            cur = conn.execute(
                "UPDATE tenant SET status = 'DISABLED', disabled_at = %s "
                "WHERE tenant_id = %s AND status = 'ACTIVE'",
                (_to_db(at or _utc_now()), tenant_id),
            )
            return cur.rowcount == 1

    def is_assignable(self, tenant_id: str) -> bool:
        with self._pool.connection() as conn:
            row = conn.execute(
                "SELECT 1 FROM tenant WHERE tenant_id = %s AND status = 'ACTIVE' "
                "AND disabled_at IS NULL", (tenant_id,),
            ).fetchone()
        return row is not None

    def count(self) -> int:
        with self._pool.connection() as conn:
            return conn.execute("SELECT count(*) FROM tenant").fetchone()[0]


# ---------------------------------------------------------------------------
# Prescriptions (FR-14, migration 0036)
# ---------------------------------------------------------------------------


class PostgresPrescriptionRepository:
    """`PrescriptionRepository` backed by `prescription` and its two children.

    The transition method is the whole point of this class, and the reason it is
    written as a single conditional UPDATE rather than read-modify-write:

        UPDATE ... WHERE prescription_id = %s AND tenant_id = %s AND status = %s

    Two processes dispensing the same prescription concurrently both read
    `VET_VERIFIED`, both decide the move is legal, and both write. With a
    conditional update the second one matches zero rows and is refused, because
    the state it believed in is no longer in the table. A read-modify-write
    would dispense twice and the audit log would faithfully record both.

    `rowcount == 0` is therefore not treated as "already done" — it is a
    refusal, and it is distinguished from "no such prescription" by a follow-up
    read inside the same tenant scope.
    """

    def __init__(self, pool: Any) -> None:
        self._pool = pool

    # -- row mapping -----------------------------------------------------
    _COLUMNS = (
        "prescription_id, tenant_id, pet_id, session_id, clinic_id, "
        "issuing_vet_id, medication_name, dosage, instructions, status, "
        "issued_at, verified_at, verified_by_vet_id, dispensed_at, "
        "dispensed_by_actor_id"
    )

    @staticmethod
    def _to_prescription(row):
        from prescriptions import Prescription

        return Prescription(
            prescription_id=row[0], tenant_id=row[1], pet_id=row[2],
            session_id=row[3], clinic_id=row[4], issuing_vet_id=row[5],
            medication_name=row[6], dosage=row[7], instructions=row[8],
            status=row[9], issued_at=_from_db(row[10]),
            verified_at=_from_db(row[11]), verified_by_vet_id=row[12],
            dispensed_at=_from_db(row[13]), dispensed_by_actor_id=row[14],
        )

    # -- writes ----------------------------------------------------------
    def create(self, rx, *, actor_id: str, actor_role: str):
        from prescriptions import STATUS_ISSUED

        if rx.status != STATUS_ISSUED:
            raise RepositoryDenied(
                f"a prescription is created in {STATUS_ISSUED}, not {rx.status!r}"
            )
        try:
            with self._pool.connection() as conn:
                # One transaction. A prescription whose issuing transition was
                # not recorded is a record with no provenance, and a transition
                # with no prescription is a ledger entry about nothing; the two
                # rows are written together or neither is.
                conn.execute(
                    f"INSERT INTO prescription ({self._COLUMNS}) "
                    "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                    (rx.prescription_id, rx.tenant_id, rx.pet_id, rx.session_id,
                     rx.clinic_id, rx.issuing_vet_id, rx.medication_name,
                     rx.dosage, rx.instructions, rx.status, _to_db(rx.issued_at),
                     None, None, None, None),
                )
                conn.execute(
                    "INSERT INTO prescription_status_transition "
                    "(transition_id, prescription_id, from_status, to_status, "
                    " actor_id, actor_role, tenant_id, occurred_at) "
                    "VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",
                    (str(uuid4()), rx.prescription_id, None, STATUS_ISSUED,
                     actor_id, actor_role, rx.tenant_id, _to_db(rx.issued_at)),
                )
        except Exception as exc:
            raise RepositoryDenied(
                f"prescription {rx.prescription_id!r} was refused "
                f"({type(exc).__name__})"
            ) from None
        return self.get(rx.prescription_id, tenant_id=rx.tenant_id) or rx

    def transition(self, prescription_id: str, *, tenant_id: str, to_status: str,
                   actor_id: str, actor_role: str, at=None):
        from prescriptions import (
            PrescriptionNotFound, STATUS_DISPENSED, STATUS_VET_VERIFIED,
            TransitionDenied, assert_transition_allowed,
        )

        current = self.get(prescription_id, tenant_id=tenant_id)
        if current is None:
            raise PrescriptionNotFound(prescription_id)
        # Checked before the statement so the caller gets the governed reason
        # rather than "0 rows matched", which is also what a concurrent writer
        # produces and would be indistinguishable from it.
        assert_transition_allowed(from_status=current.status, to_status=to_status)

        now = _to_db(at or _utc_now())
        if to_status == STATUS_VET_VERIFIED:
            sql = ("UPDATE prescription SET status = %s, verified_at = %s, "
                   "verified_by_vet_id = %s "
                   "WHERE prescription_id = %s AND tenant_id = %s AND status = %s")
        elif to_status == STATUS_DISPENSED:
            sql = ("UPDATE prescription SET status = %s, dispensed_at = %s, "
                   "dispensed_by_actor_id = %s "
                   "WHERE prescription_id = %s AND tenant_id = %s AND status = %s")
        else:  # pragma: no cover - assert_transition_allowed rejects these first
            raise TransitionDenied(f"unsupported target status {to_status!r}")

        with self._pool.connection() as conn:
            cur = conn.execute(
                sql,
                (to_status, now, actor_id, prescription_id, tenant_id,
                 current.status),
            )
            if cur.rowcount != 1:
                raise TransitionDenied(
                    f"prescription {prescription_id!r} was not in "
                    f"{current.status!r} when the move was applied; refusing "
                    "rather than overwriting a state another writer set"
                )
            conn.execute(
                "INSERT INTO prescription_status_transition "
                "(transition_id, prescription_id, from_status, to_status, "
                " actor_id, actor_role, tenant_id, occurred_at) "
                "VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",
                (str(uuid4()), prescription_id, current.status, to_status,
                 actor_id, actor_role, tenant_id, now),
            )
        return self.get(prescription_id, tenant_id=tenant_id)

    def attach_document(self, doc):
        from prescriptions import PrescriptionNotFound

        if self.get(doc.prescription_id, tenant_id=doc.tenant_id) is None:
            raise PrescriptionNotFound(doc.prescription_id)
        try:
            with self._pool.connection() as conn:
                conn.execute(
                    "INSERT INTO prescription_document "
                    "(document_id, prescription_id, tenant_id, "
                    " uploaded_by_actor_id, filename, content_type, byte_size, "
                    " content_sha256, storage_key, uploaded_at) "
                    "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                    (doc.document_id, doc.prescription_id, doc.tenant_id,
                     doc.uploaded_by_actor_id, doc.filename, doc.content_type,
                     doc.byte_size, doc.content_sha256, doc.storage_key,
                     _to_db(doc.uploaded_at)),
                )
        except Exception as exc:
            raise RepositoryDenied(
                f"document {doc.document_id!r} was refused "
                f"({type(exc).__name__})"
            ) from None
        return doc

    # -- reads -----------------------------------------------------------
    def get(self, prescription_id: str, *, tenant_id: str):
        with self._pool.connection() as conn:
            row = conn.execute(
                f"SELECT {self._COLUMNS} FROM prescription "
                "WHERE prescription_id = %s AND tenant_id = %s",
                (prescription_id, tenant_id),
            ).fetchone()
        return self._to_prescription(row) if row else None

    def list_by_status(self, *, tenant_id: str, status: str):
        with self._pool.connection() as conn:
            rows = conn.execute(
                f"SELECT {self._COLUMNS} FROM prescription "
                "WHERE tenant_id = %s AND status = %s ORDER BY issued_at",
                (tenant_id, status),
            ).fetchall()
        return [self._to_prescription(r) for r in rows]

    def transitions_for(self, prescription_id: str, *, tenant_id: str):
        from prescriptions import StatusTransition

        with self._pool.connection() as conn:
            rows = conn.execute(
                "SELECT transition_id, prescription_id, from_status, to_status, "
                "       actor_id, actor_role, tenant_id, occurred_at "
                "FROM prescription_status_transition "
                "WHERE prescription_id = %s AND tenant_id = %s "
                "ORDER BY occurred_at, transition_id",
                (prescription_id, tenant_id),
            ).fetchall()
        return [
            StatusTransition(
                transition_id=r[0], prescription_id=r[1], from_status=r[2],
                to_status=r[3], actor_id=r[4], actor_role=r[5], tenant_id=r[6],
                occurred_at=_from_db(r[7]),
            )
            for r in rows
        ]

    def documents_for(self, prescription_id: str, *, tenant_id: str):
        with self._pool.connection() as conn:
            rows = conn.execute(
                "SELECT document_id, prescription_id, tenant_id, "
                "       uploaded_by_actor_id, filename, content_type, "
                "       byte_size, content_sha256, storage_key, uploaded_at "
                "FROM prescription_document "
                "WHERE prescription_id = %s AND tenant_id = %s "
                "ORDER BY uploaded_at, document_id",
                (prescription_id, tenant_id),
            ).fetchall()
        return [self._to_document(r) for r in rows]

    def get_document(self, document_id: str, *, tenant_id: str):
        with self._pool.connection() as conn:
            row = conn.execute(
                "SELECT document_id, prescription_id, tenant_id, "
                "       uploaded_by_actor_id, filename, content_type, "
                "       byte_size, content_sha256, storage_key, uploaded_at "
                "FROM prescription_document "
                "WHERE document_id = %s AND tenant_id = %s",
                (document_id, tenant_id),
            ).fetchone()
        return self._to_document(row) if row else None

    @staticmethod
    def _to_document(row):
        from prescriptions import PrescriptionDocument

        return PrescriptionDocument(
            document_id=row[0], prescription_id=row[1], tenant_id=row[2],
            uploaded_by_actor_id=row[3], filename=row[4], content_type=row[5],
            byte_size=row[6], content_sha256=row[7], storage_key=row[8],
            uploaded_at=_from_db(row[9]),
        )



class PostgresPetProfileRepository:
    """`PetProfileRepository` over migration 0037 (FR-02, MVC-BUILD-RUNNER-001 U2).

    Every statement carries `tenant_id` in its predicate, so a profile, its
    identifications and its history are unreachable from another tenant through
    this class regardless of what a caller forgets.
    """

    _PET = ("pet_id, tenant_id, owner_id, name, species, breed, birth_date, weight_kg, "
            "medical_conditions, allergies, preferences, created_by_actor_id, created_at, updated_at")
    _IDENT = ("identification_id, pet_id, tenant_id, id_type, id_value, issuing_scheme, "
              "captured_at, capture_method, recorded_by_actor_id, recorded_at")
    _REC = "record_id, pet_id, tenant_id, record_type, title, detail, recorded_by_actor_id, recorded_at"

    def __init__(self, pool: Any) -> None:
        self._pool = pool

    @staticmethod
    def _to_pet(row):
        from pets import PetProfile

        return PetProfile(
            pet_id=row[0], tenant_id=row[1], owner_id=row[2], name=row[3], species=row[4],
            breed=row[5], birth_date=row[6],
            weight_kg=float(row[7]) if row[7] is not None else None,
            medical_conditions=row[8], allergies=row[9], preferences=row[10],
            created_by_actor_id=row[11], created_at=_from_db(row[12]), updated_at=_from_db(row[13]),
        )

    @staticmethod
    def _to_ident(row):
        from pets import PetIdentification

        return PetIdentification(
            identification_id=row[0], pet_id=row[1], tenant_id=row[2], id_type=row[3],
            id_value=row[4], issuing_scheme=row[5], captured_at=row[6], capture_method=row[7],
            recorded_by_actor_id=row[8], recorded_at=_from_db(row[9]),
        )

    @staticmethod
    def _to_rec(row):
        from pets import PetMedicalRecord

        return PetMedicalRecord(
            record_id=row[0], pet_id=row[1], tenant_id=row[2], record_type=row[3], title=row[4],
            detail=row[5], recorded_by_actor_id=row[6], recorded_at=_from_db(row[7]),
        )

    def _write(self, sql: str, params: tuple, what: str) -> None:
        try:
            with self._pool.connection() as conn:
                conn.execute(sql, params)
        except Exception as exc:
            raise RepositoryDenied(f"{what} was refused ({type(exc).__name__})") from None

    def create(self, pet):
        self._write(
            f"INSERT INTO pet_profile ({self._PET}) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
            (pet.pet_id, pet.tenant_id, pet.owner_id, pet.name, pet.species, pet.breed, pet.birth_date,
             pet.weight_kg, pet.medical_conditions, pet.allergies, pet.preferences,
             pet.created_by_actor_id, _to_db(pet.created_at), _to_db(pet.updated_at)),
            f"pet {pet.pet_id!r}")
        return self.get(pet.pet_id, tenant_id=pet.tenant_id) or pet

    def get(self, pet_id: str, *, tenant_id: str):
        with self._pool.connection() as conn:
            row = conn.execute(f"SELECT {self._PET} FROM pet_profile WHERE pet_id = %s AND tenant_id = %s",
                               (pet_id, tenant_id)).fetchone()
        return self._to_pet(row) if row else None

    def list_for_tenant(self, *, tenant_id: str, owner_id=None):
        sql = f"SELECT {self._PET} FROM pet_profile WHERE tenant_id = %s"
        params: tuple = (tenant_id,)
        if owner_id is not None:
            sql += " AND owner_id = %s"
            params = (tenant_id, owner_id)
        with self._pool.connection() as conn:
            rows = conn.execute(sql + " ORDER BY created_at, pet_id", params).fetchall()
        return [self._to_pet(r) for r in rows]

    def update(self, pet_id: str, *, tenant_id: str, changes: dict, updated_at):
        from pets import MUTABLE_FIELDS

        bad = [k for k in changes if k not in MUTABLE_FIELDS]
        if bad:
            raise RepositoryDenied(f"fields {bad} are not mutable")
        if self.get(pet_id, tenant_id=tenant_id) is None:
            raise RepositoryDenied(f"pet {pet_id!r} is not in tenant {tenant_id!r}")
        cols = list(changes)
        assignments = ", ".join(f"{c} = %s" for c in cols + ["updated_at"])
        self._write(f"UPDATE pet_profile SET {assignments} WHERE pet_id = %s AND tenant_id = %s",
                    tuple(changes[c] for c in cols) + (_to_db(updated_at), pet_id, tenant_id),
                    f"update of pet {pet_id!r}")
        return self.get(pet_id, tenant_id=tenant_id)

    def add_identification(self, ident):
        from pets import validate_identification

        validate_identification(ident)
        if self.get(ident.pet_id, tenant_id=ident.tenant_id) is None:
            raise RepositoryDenied(f"pet {ident.pet_id!r} is not in tenant {ident.tenant_id!r}")
        self._write(
            f"INSERT INTO pet_identification ({self._IDENT}) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
            (ident.identification_id, ident.pet_id, ident.tenant_id, ident.id_type, ident.id_value,
             ident.issuing_scheme, ident.captured_at, ident.capture_method, ident.recorded_by_actor_id,
             _to_db(ident.recorded_at)),
            f"identification for pet {ident.pet_id!r}")
        return ident

    def identifications_for(self, pet_id: str, *, tenant_id: str):
        with self._pool.connection() as conn:
            rows = conn.execute(
                f"SELECT {self._IDENT} FROM pet_identification WHERE pet_id = %s AND tenant_id = %s "
                "ORDER BY recorded_at, identification_id", (pet_id, tenant_id)).fetchall()
        return [self._to_ident(r) for r in rows]

    def add_medical_record(self, rec):
        from pets import validate_medical_record

        validate_medical_record(rec)
        if self.get(rec.pet_id, tenant_id=rec.tenant_id) is None:
            raise RepositoryDenied(f"pet {rec.pet_id!r} is not in tenant {rec.tenant_id!r}")
        self._write(
            f"INSERT INTO pet_medical_record ({self._REC}) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",
            (rec.record_id, rec.pet_id, rec.tenant_id, rec.record_type, rec.title, rec.detail,
             rec.recorded_by_actor_id, _to_db(rec.recorded_at)),
            f"medical record for pet {rec.pet_id!r}")
        return rec

    def medical_records_for(self, pet_id: str, *, tenant_id: str):
        with self._pool.connection() as conn:
            rows = conn.execute(
                f"SELECT {self._REC} FROM pet_medical_record WHERE pet_id = %s AND tenant_id = %s "
                "ORDER BY recorded_at, record_id", (pet_id, tenant_id)).fetchall()
        return [self._to_rec(r) for r in rows]

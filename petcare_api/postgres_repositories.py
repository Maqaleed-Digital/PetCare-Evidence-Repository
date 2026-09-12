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

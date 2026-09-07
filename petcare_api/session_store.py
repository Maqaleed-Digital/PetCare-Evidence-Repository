"""W0-F AC-7 — server-side revocable sessions.

The W0-F pack states the problem exactly:

> Because there is one key and no fallback list, **rotating the key invalidates
> every existing session**. If W0-F introduces a server-side session store or a
> previous-key list, that property is lost and an explicit revocation path
> becomes mandatory. Whichever way it goes, it must be a decision, not a side
> effect.

This is the decision. A server-side store is introduced, so key rotation stops
being the revocation mechanism and becomes what it should always have been: an
emergency, system-wide capability. Per-user and per-session revocation happen
here, without touching the signing key.

That distinction is the whole point. Before this module, revoking one compromised
session meant rotating the key and signing every user out — a cost so high that
in practice nobody would pay it, which means in practice sessions were not
revocable at all.

## What a signed cookie can and cannot establish

A validly signed cookie proves the payload was written by this service and has
not been altered. It cannot prove the session is *still* valid — that the user
has not signed out, been disabled, or had the session revoked. Signature
integrity is a statement about the past; session validity is a statement about
now. Only a server-side record can answer the second, which is why
`read_session` must consult this store even when the signature verifies.

## Tenant is required, never defaulted

Every lookup takes `tenant_id` and there is no default. This follows the W0-I
security-review finding: `tenant_id: Optional[str] = None` reads as "match any
tenant", so a caller who omits the argument gets a cross-tenant check that looks
correct at the call site. The estate guard
`tests/governance/test_tenant_scope_signatures.py` enforces the absence of such a
default.

## No persistence here

`InMemorySessionStore` is the non-production implementation. The production
implementation is a table in the store named by
`MVC-W0F-DATA-STORE-DECISION-001`, and applying it is `GATE_LIVE_APPLY`. The
`SessionStore` protocol exists so that swap is a configuration change rather than
a rewrite — the same portability requirement D.21 imposes on hosting location.
"""
from __future__ import annotations

import secrets
from dataclasses import dataclass, replace
from datetime import datetime, timedelta, timezone
from typing import Iterable, Optional, Protocol


class SessionDenied(Exception):
    """A session was presented that must not be honoured."""


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


@dataclass(frozen=True)
class SessionRecord:
    """A server-side session. Immutable; revocation produces a new record.

    Keeping records immutable means the history of a session — when it was
    issued, when it was revoked — survives, rather than being overwritten by the
    act of revoking it.
    """

    session_id: str
    user_id: str
    tenant_id: Optional[str]
    role: str
    issued_at: datetime
    expires_at: datetime
    revoked_at: Optional[datetime] = None

    def is_active_at(self, when: datetime) -> bool:
        """Whether this session may be honoured at `when`.

        Half-open on both ends: a session is dead at its expiry instant and at
        its revocation instant. Where validity is ambiguous the safe reading is
        the one that denies.
        """
        if when >= self.expires_at:
            return False
        if self.revoked_at is not None and when >= self.revoked_at:
            return False
        return True


class SessionStore(Protocol):
    """The contract `read_session` depends on.

    Deliberately narrow: create, look up, revoke one, revoke a user's set. A
    store that could do more would invite authorization logic to migrate into it,
    and authorization belongs in one place.
    """

    def create(
        self, *, user_id: str, tenant_id: str, role: str, ttl_seconds: int
    ) -> SessionRecord: ...

    def get_active(self, session_id: str, *, tenant_id: Optional[str]) -> Optional[SessionRecord]: ...

    def revoke(self, session_id: str, *, tenant_id: str) -> bool: ...

    def revoke_all_for_user(self, user_id: str, *, tenant_id: str) -> int: ...


class InMemorySessionStore:
    """Non-production implementation. Dies with the process, by design.

    It is not a placeholder for the semantics — every control in
    `test_session_revocation.py` runs against this class, so the behaviour is
    fixed here and the production implementation must match it. What it does not
    provide is durability, which is W0-F's persistence step and is gated.
    """

    def __init__(self) -> None:
        self._sessions: dict[str, SessionRecord] = {}

    # -- writes ----------------------------------------------------------

    def create(
        self, *, user_id: str, tenant_id: Optional[str], role: str, ttl_seconds: int
    ) -> SessionRecord:
        # Two different things must not be conflated here.
        #
        #   None  the identity holds NO tenant assignment. That is a legitimate
        #         state — seed_user permits it — and it fails closed downstream:
        #         require_tenant() raises 403 NO_TENANT_AUTHORITY the moment such
        #         an identity attempts anything tenant-scoped. The session is
        #         real; it simply cannot act on a tenant.
        #   ""    a MALFORMED tenant. An empty string is not "no tenant", it is a
        #         tenant whose value was lost, and honouring it would create a
        #         session keyed on a value that could later collide.
        if tenant_id is not None and not tenant_id.strip():
            raise SessionDenied("a session cannot be created with a blank tenant")
        now = _utc_now()
        record = SessionRecord(
            session_id=secrets.token_urlsafe(32),
            user_id=user_id,
            tenant_id=tenant_id,
            role=role,
            issued_at=now,
            expires_at=now + timedelta(seconds=ttl_seconds),
        )
        self._sessions[record.session_id] = record
        return record

    def revoke(self, session_id: str, *, tenant_id: str) -> bool:
        """Revoke one session. Returns whether anything was revoked.

        Scoped by tenant: a caller in tenant B cannot revoke a session in tenant
        A. Revocation is a privileged act on someone else's session, so it needs
        the same scoping as reading one.
        """
        record = self._sessions.get(session_id)
        if record is None or record.tenant_id != tenant_id:
            return False
        if record.revoked_at is not None:
            return False
        self._sessions[session_id] = replace(record, revoked_at=_utc_now())
        return True

    def revoke_all_for_user(self, user_id: str, *, tenant_id: str) -> int:
        """Revoke every active session for one user, within one tenant.

        This is the operation that replaces key rotation for the common case —
        "sign this user out everywhere" — and it must touch nobody else. The
        `user_id` AND `tenant_id` match is what keeps it from becoming a blunt
        instrument.
        """
        now = _utc_now()
        count = 0
        for sid, record in list(self._sessions.items()):
            if record.user_id != user_id or record.tenant_id != tenant_id:
                continue
            if not record.is_active_at(now):
                continue
            self._sessions[sid] = replace(record, revoked_at=now)
            count += 1
        return count

    # -- reads -----------------------------------------------------------

    def get_active(self, session_id: str, *, tenant_id: Optional[str]) -> Optional[SessionRecord]:
        """The session, only if it exists, matches the tenant, and is live.

        Returns None for unknown, revoked, expired and cross-tenant alike. The
        caller cannot distinguish them, and should not: telling an attacker
        whether a session id exists is a small oracle, and no legitimate caller
        needs the difference.
        """
        record = self._sessions.get(session_id)
        if record is None:
            return None
        if record.tenant_id != tenant_id:
            return None
        if not record.is_active_at(_utc_now()):
            return None
        return record

    # -- introspection, for tests and operations --------------------------

    def all_for_user(self, user_id: str, *, tenant_id: str) -> Iterable[SessionRecord]:
        return [
            r
            for r in self._sessions.values()
            if r.user_id == user_id and r.tenant_id == tenant_id
        ]

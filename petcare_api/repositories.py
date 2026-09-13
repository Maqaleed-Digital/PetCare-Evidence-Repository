"""The serving layer's persistence boundary.

W0-F requires the serving path to reach a durable store. The requirement this
module answers is narrower and more important than "add a database": **auth code
must depend on an interface, not on SQL**, so that swapping the backing store is
configuration rather than a rewrite — the same portability property D.21 imposes
on hosting location.

So no SQL appears in `routers/auth.py`, and none ever should. The router calls
these protocols; `postgres_repositories.py` and the in-memory classes below are
the two implementations, and both are exercised by the same controls.

## Why the in-memory implementations live here rather than in the router

They were module-level dicts inside `routers/auth.py` (`_users`, `_invite_codes`).
Read as persistence, a dict is a store with no constraints: it cannot refuse a
role outside the catalogue, cannot refuse a blank tenant, and cannot make a
duplicate email unrepresentable. Every one of those is enforced by the database
in `0031`, and a memory mode that did NOT enforce them would mean the test suite
proves the weaker of the two — and the controls would first fail in production,
against the implementation nobody had run.

The two implementations therefore share their semantics deliberately: the
in-memory one performs the same refusals the schema does.

## What is NOT here

Authorization. The protocols answer "what is stored"; `read_session` and
`require_tenant` answer "what may this caller do". Merging them would put
authorization decisions behind an interface with two implementations, which is
two places for an authorization bug to live.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime, timezone
from typing import Optional, Protocol

from roles import VALID_ROLES
from tenants import TenantRepository, require_assignable


class RepositoryDenied(Exception):
    """A write was refused because it would store something unrepresentable.

    Distinct from "not found": a refusal means the caller asked for a state the
    store must never hold, and the caller should not retry with the same input.
    """


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


#: Where a stored identity came from. Mirrors user_identity.provenance in
#: migration 0031, whose CHECK constraints depend on the value.
PROVENANCE_SEED = "SEED"
PROVENANCE_REGISTRATION = "REGISTRATION"
PROVENANCE_IDENTITY_MIGRATION = "IDENTITY_MIGRATION"
#: The single-use first-`platform_admin` genesis act (migration 0035, Sponsor
#: ruling MVC-GENESIS-PLATFORM-ADMIN-001). A fourth origin rather than a reuse
#: of `SEED`, because the first administrator is not a development artefact and
#: must stay distinguishable from one for as long as the row exists.
PROVENANCE_GENESIS = "GENESIS"
VALID_PROVENANCE = frozenset({
    PROVENANCE_SEED, PROVENANCE_REGISTRATION, PROVENANCE_IDENTITY_MIGRATION,
    PROVENANCE_GENESIS,
})


@dataclass(frozen=True)
class UserIdentity:
    """One stored identity. Frozen for the same reason `SessionRecord` is: a
    mutable identity passed around the serving path can be altered far from
    where it was read, and the alteration would be invisible at the read site."""

    user_id: str
    email: str
    password_hash: str
    role: str
    full_name: str
    tenant_id: Optional[str] = None
    provenance: str = PROVENANCE_SEED
    source_record_id: Optional[str] = None
    created_at: Optional[datetime] = None
    disabled_at: Optional[datetime] = None

    @property
    def is_active(self) -> bool:
        return self.disabled_at is None


@dataclass(frozen=True)
class InviteCode:
    code: str
    allowed_role: str
    tenant_id: Optional[str] = None
    expires_at: Optional[datetime] = None
    consumed_at: Optional[datetime] = None
    consumed_by: Optional[str] = None

    def is_consumed(self) -> bool:
        return self.consumed_at is not None

    def is_expired_at(self, when: datetime) -> bool:
        return self.expires_at is not None and self.expires_at <= when


def validate_identity(identity: UserIdentity) -> None:
    """The refusals the schema makes structurally, applied before any write.

    Duplicated on purpose. The database is the authority, but a check here fails
    at the call site with the offending field named, instead of surfacing as a
    constraint violation several frames away — and in memory mode there is no
    database to do it at all.
    """
    if identity.role not in VALID_ROLES:
        raise RepositoryDenied(
            f"role {identity.role!r} is not in the catalogue; an identity is "
            "never stored with a role the serving layer cannot mint"
        )
    if identity.provenance not in VALID_PROVENANCE:
        raise RepositoryDenied(f"unknown provenance {identity.provenance!r}")
    if identity.tenant_id is not None and not identity.tenant_id.strip():
        raise RepositoryDenied(
            "a blank tenant is not 'no tenant' — it is a tenant whose value was "
            "lost, and is refused"
        )
    if not identity.email or not identity.email.strip():
        raise RepositoryDenied("an identity must carry an email")
    if not identity.password_hash:
        raise RepositoryDenied("an identity must carry a password hash")
    if identity.provenance == PROVENANCE_IDENTITY_MIGRATION:
        # The structural rule from migration 0031, restated where the tool can
        # be told which record failed. An unresolved identity is quarantined,
        # never written to the authoritative table.
        if identity.tenant_id is None:
            raise RepositoryDenied(
                "a migrated identity with no tenant must be quarantined, not "
                "written to the authoritative identity table"
            )
        if not identity.source_record_id:
            raise RepositoryDenied(
                "a migrated identity must carry its source record id, or it "
                "cannot be reconciled against anything"
            )


class IdentityRepository(Protocol):
    """Identity, as the serving path needs it."""

    def get_by_email(self, email: str) -> Optional[UserIdentity]: ...

    def get_by_user_id(self, user_id: str) -> Optional[UserIdentity]: ...

    def upsert(self, identity: UserIdentity) -> UserIdentity:
        """Write an identity, replacing one with the same id. Seeding only."""
        ...

    def create(self, identity: UserIdentity) -> UserIdentity:
        """Write a NEW identity. Raises `RepositoryDenied` if the email exists."""
        ...

    def set_password_hash(self, user_id: str, password_hash: str) -> None: ...

    def count(self) -> int: ...


class InviteCodeRepository(Protocol):
    def get(self, code: str) -> Optional[InviteCode]: ...

    def upsert(self, invite: InviteCode) -> InviteCode: ...

    def consume(self, code: str, *, email: str, at: Optional[datetime] = None) -> bool:
        """Mark a code consumed. Returns False if it was ALREADY consumed.

        One operation rather than read-then-write, because the read-then-write
        shape lets two simultaneous registrations both observe an unconsumed code
        and both proceed. The persistent implementation makes this a single
        conditional update so the database decides the winner.
        """
        ...


# ---------------------------------------------------------------------------
# In-memory implementations — non-production, and dying with the process is the
# point rather than a limitation.
# ---------------------------------------------------------------------------

class InMemoryIdentityRepository:
    """Non-production identity store.

    Takes the tenant registry so that it performs the SAME refusals the schema
    does. A memory mode that accepted a tenant the database would reject would
    mean the suite proves the weaker of the two, and the control would first fail
    in production against the implementation nobody had run.
    """

    def __init__(self, tenants: TenantRepository) -> None:
        self._by_email: dict[str, UserIdentity] = {}
        self._by_id: dict[str, UserIdentity] = {}
        #: REQUIRED, and deliberately without a default.
        #:
        #: `tests/governance/test_tenant_scope_signatures.py` forbids a
        #: tenant-bearing parameter that may be omitted, and it is right to: a
        #: registry that could be left out is one that gets left out. Passing
        #: `None` explicitly is still allowed and still fails closed — see
        #: `tenants.require_assignable` — but it becomes a decision at the call
        #: site rather than an omission.
        self._tenants = tenants

    def _index(self, identity: UserIdentity) -> UserIdentity:
        stored = identity if identity.created_at else replace(identity, created_at=_utc_now())
        self._by_email[stored.email] = stored
        self._by_id[stored.user_id] = stored
        return stored

    def get_by_email(self, email: str) -> Optional[UserIdentity]:
        return self._by_email.get(email)

    def get_by_user_id(self, user_id: str) -> Optional[UserIdentity]:
        return self._by_id.get(user_id)

    def upsert(self, identity: UserIdentity) -> UserIdentity:
        validate_identity(identity)
        require_assignable(self._tenants, identity.tenant_id)
        existing = self._by_id.get(identity.user_id)
        if existing is not None and existing.email != identity.email:
            self._by_email.pop(existing.email, None)
        return self._index(identity)

    def create(self, identity: UserIdentity) -> UserIdentity:
        validate_identity(identity)
        require_assignable(self._tenants, identity.tenant_id)
        if identity.email in self._by_email:
            raise RepositoryDenied(f"an identity already exists for {identity.email!r}")
        if identity.user_id in self._by_id:
            raise RepositoryDenied(f"an identity already exists with id {identity.user_id!r}")
        return self._index(identity)

    def set_password_hash(self, user_id: str, password_hash: str) -> None:
        existing = self._by_id.get(user_id)
        if existing is None:
            raise RepositoryDenied(f"no identity with id {user_id!r}")
        self._index(replace(existing, password_hash=password_hash))

    def count(self) -> int:
        return len(self._by_id)


class InMemoryInviteCodeRepository:
    def __init__(self) -> None:
        self._codes: dict[str, InviteCode] = {}

    def get(self, code: str) -> Optional[InviteCode]:
        return self._codes.get(code)

    def upsert(self, invite: InviteCode) -> InviteCode:
        if invite.allowed_role not in VALID_ROLES:
            raise RepositoryDenied(
                f"invite code {invite.code!r} allows role {invite.allowed_role!r}, "
                "which is not in the catalogue"
            )
        if invite.tenant_id is not None and not invite.tenant_id.strip():
            raise RepositoryDenied("an invite code cannot carry a blank tenant")
        self._codes[invite.code] = invite
        return invite

    def consume(self, code: str, *, email: str, at: Optional[datetime] = None) -> bool:
        invite = self._codes.get(code)
        if invite is None or invite.is_consumed():
            return False
        self._codes[code] = replace(
            invite, consumed_at=at or _utc_now(), consumed_by=email
        )
        return True

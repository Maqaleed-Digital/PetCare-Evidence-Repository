"""The single-use first-`platform_admin` genesis act.

Sponsor ruling of 12 September 2026, `MVC-GENESIS-PLATFORM-ADMIN-001`
(*MYVETICARE FIRST PLATFORM ADMINISTRATOR GENESIS AUTHORITY*):

> This authority exists only because the governed production system requires an
> existing `platform_admin` before tenant membership can be administered, while
> all ordinary role-creation and role-elevation authority remains separately
> governed.

## The deadlock this resolves, and nothing else

`RATIFICATION-002` item 3 makes `platform_admin` the sole role permitted to
administer tenant membership, and withholds every authority that could create
or elevate one. Registration mints `owner` and `veterinarian` through invite
codes and grants no elevated role by design; the three seed identities were
discarded by `PRE1_RULING=1-B`. Production therefore had no authorized way to
obtain its first administrator, so nobody could ever be assigned to a tenant.

This module is the narrowest exit from that. It is **not** a privilege-
management facility:

```
GENESIS_AUTHORITY=SINGLE_USE
GENERAL_PLATFORM_ADMIN_ELEVATION_AUTHORITY=NOT_AUTHORIZED
GENESIS_REUSE=PROHIBITED
SECOND_GENESIS_ATTEMPT=MUST_FAIL_CLOSED
```

## Why the role is an absence, not a parameter

§2: *"The procedure must not accept an arbitrary role parameter… The genesis
procedure must not be capable of creating any other privileged role or of
elevating an existing identity to another role."*

`execute()` has no parameter that names a role, exactly as
`TenantMembershipService.set_membership` has none. The role is the module
constant `ROLE_PLATFORM_ADMIN`, written directly into the `INSERT`. A parameter
that does not exist cannot be misused, and the database refuses the other half
independently: `platform_admin_genesis.granted_role` has a CHECK admitting one
value.

Nor can it elevate: the statement is an `INSERT`, never an `UPDATE` and never an
upsert. An existing identity cannot be reached by this path at all — a duplicate
`user_id` or `email` is a unique violation, which is a refusal.

## Why there is no route

§7 withholds *"a reusable bootstrap endpoint"*. Every other governed act in this
estate is an HTTP route because it recurs; this one happens once in the lifetime
of the deployment, and an endpoint that exists after it has been consumed is a
permanently reachable privilege-creation surface guarded only by a row. The
entry point is `scripts/governance/platform_admin_genesis.py`, run deliberately
by an operator at cutover.

## Tenant context

The first administrator holds **no tenant**. Platform scope is represented in
this estate by the absence of one plus an explicit role, never by a tenant that
stands for everyone — TENANT-04 and TENANT-09, recorded in `tenants.py`. §3
permits *"the tenant context required by the governed production identity
model"* and forbids inferring a tenant value; for a platform-scoped principal
that model requires absence.

That also keeps §9 intact. Migration 0034 puts an FK from
`user_identity.tenant_id` onto `tenant`, so binding the administrator to the
ruled first production tenant would require creating that row first — a
production tenant-row creation the ruling does not authorize.

The identifier itself is deliberately not written here. It belongs in the
governance record (`RATIFICATION-003`, and `RATIFICATION-004` §"Where
implementation had to resolve the ruling's text"), and
`tests/governance/test_production_tenant_not_created.py` keeps it out of every
tree that could create it — including this one. Naming authority is not
creation authority, and a module that names the tenant is one edit from
assigning it.

## Why one transaction

§6: *"The genesis operation must be atomic with its required durable audit
evidence."* Three writes must commit together or not at all — the identity, the
governed audit event, and the consumption record. Any ordering leaves a state
the ruling names as prohibited:

    identity, then audit   → a privileged identity with no genesis record
    audit, then identity   → a record claiming an administrator that was not created
    either, then ledger    → an administrator whose authority is not marked consumed

So there is one transaction, the audit append runs inside it via
`append_event_on`, and every refusal below happens before anything is written.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional
from uuid import uuid4

from audit_repository import AuditWriteFailed
from repositories import PROVENANCE_GENESIS, UserIdentity
from roles import ROLE_PLATFORM_ADMIN

#: The governed event name. The resulting role is part of the name because §4
#: requires the record to identify it and the governed field set may not be
#: widened — an event name is governed representation, not structured state
#: smuggled into a free-text field.
EVENT_PLATFORM_ADMIN_GENESIS = "platform_admin.genesis"

#: The audit `resource_type` for the act. `resource_id` is the target identity.
RESOURCE_TYPE_GENESIS = "platform_admin_genesis"

#: §4: `GENESIS_AUDIT_ACTOR=UNATTRIBUTED_OR_GOVERNED_SYSTEM_GENESIS`,
#: `INVENTED_ACTOR=PROHIBITED`.
#:
#: There is no prior governed human actor, because this is the act that creates
#: the first one. The estate already has a representation for a governed event
#: with no verified principal behind it — `UNATTRIBUTED`, which `main.py` uses
#: for the tenant of an unauthenticated write — and reusing it is what keeps the
#: absence visible. Naming the new administrator as the actor would be the
#: invention the ruling prohibits: it would read as though they had authorized
#: their own creation.
#:
#: Neither value is a member of `ALLOWED_ROLES`, so no authorization decision
#: can ever match them.
GENESIS_ACTOR_ID = "UNATTRIBUTED"
GENESIS_ACTOR_ROLE = "UNATTRIBUTED"

#: The tenant the genesis event is scoped to. `audit_event.tenant_id` is
#: `TEXT NOT NULL` and deliberately carries no FK (0034), precisely so that an
#: event with no tenant perimeter does not require a fake tenant row.
GENESIS_EVENT_TENANT = "UNATTRIBUTED"


class GenesisDenied(Exception):
    """The genesis act was refused. Nothing was written."""


class GenesisUnavailable(Exception):
    """The genesis path cannot operate on this deployment.

    Raised when the configured store is not durable. §5 requires the single-use
    property to rest on durable state; an administrator established in a store
    that dies with the process would be a privilege grant nobody could later
    prove was authorized, and there is no fallback to offer.
    """


@dataclass(frozen=True)
class GenesisResult:
    user_id: str
    role: str
    audit_event_id: str
    ruling_reference: str


class PlatformAdminGenesisService:
    """The only authorized path for establishing the first `platform_admin`."""

    def __init__(self, persistence: Any) -> None:
        self._persistence = persistence

    # -- readback --------------------------------------------------------

    def read_genesis_admin(self) -> Optional[UserIdentity]:
        """§5: *"the system must verify that the intended first platform
        administrator exists."*

        Read through the consumption record rather than by searching for a
        `platform_admin`, so the answer is "the identity this authority was
        consumed to establish" and not "some administrator that exists now".
        """
        persistence = self._persistence
        if not getattr(persistence, "is_durable", False) or persistence.pool is None:
            return None
        with persistence.pool.connection() as conn:
            row = conn.execute(
                "SELECT target_user_id FROM platform_admin_genesis"
            ).fetchone()
        if row is None:
            return None
        return persistence.identities.get_by_user_id(row[0])

    def is_consumed(self) -> bool:
        """Whether the single-use authority has already been spent."""
        persistence = self._persistence
        if not getattr(persistence, "is_durable", False) or persistence.pool is None:
            raise GenesisUnavailable(
                "the genesis authority's state is durable state; it cannot be "
                "read from a store that does not persist"
            )
        with persistence.pool.connection() as conn:
            return conn.execute(
                "SELECT count(*) FROM platform_admin_genesis"
            ).fetchone()[0] > 0

    # -- the governed act ------------------------------------------------

    def execute(
        self,
        *,
        user_id: str,
        email: str,
        password_hash: str,
        full_name: str,
        ruling_reference: str,
        correlation_id: str,
    ) -> GenesisResult:
        """Establish the first production `platform_admin`. Once, ever.

        There is deliberately **no** role parameter: see the module docstring.
        The credential arrives already hashed, so no plaintext production
        credential passes through this module and none is ever defaulted.
        """
        if not str(user_id or "").strip():
            raise GenesisDenied("the genesis act must name the target identity")
        if not str(email or "").strip():
            raise GenesisDenied("the genesis act must name the target address")
        if not str(full_name or "").strip():
            raise GenesisDenied("the genesis act must name the target")
        if not str(password_hash or "").strip():
            # §2: "This ruling does not authorize inventing, embedding, or
            # storing a default credential." An absent credential is a refusal,
            # never a fallback — a default administrator password in a public
            # repository is the exact defect PRE-1 discarded three identities
            # over, and this identity holds the highest role in the system.
            raise GenesisDenied(
                "no credential was supplied for the first platform administrator; "
                "refusing rather than inventing or defaulting one"
            )
        if not str(ruling_reference or "").strip():
            # §4: the audit record must identify the governing Sponsor ruling.
            # An act recorded without its authority is indistinguishable
            # afterwards from an act that had none.
            raise GenesisDenied(
                "the genesis act must cite the governing Sponsor ruling"
            )

        persistence = self._persistence
        if not getattr(persistence, "is_durable", False) or persistence.pool is None:
            raise GenesisUnavailable(
                "the genesis act is a durable governed act and this deployment "
                "is not configured for a durable store; refusing rather than "
                "establishing an administrator that dies with the process"
            )

        try:
            with persistence.pool.connection() as conn:
                with conn.transaction():
                    return self._apply(
                        conn,
                        user_id=user_id,
                        email=email,
                        password_hash=password_hash,
                        full_name=full_name,
                        ruling_reference=ruling_reference,
                        correlation_id=correlation_id,
                    )
        except (GenesisDenied, GenesisUnavailable, AuditWriteFailed):
            raise
        except Exception as exc:
            # Fail closed, and say so without leaking the store's internals.
            raise GenesisDenied(
                f"the genesis act could not be completed ({type(exc).__name__}); "
                f"nothing was written"
            ) from None

    # -- inside the caller's transaction ---------------------------------

    def _apply(
        self, conn: Any, *, user_id: str, email: str, password_hash: str,
        full_name: str, ruling_reference: str, correlation_id: str,
    ) -> GenesisResult:
        # 1 · Serialise against every other genesis attempt.
        #
        #     The singleton primary key already makes two consumption records
        #     impossible, but without this lock two concurrent attempts both
        #     read "not yet consumed", both insert an identity, and one then
        #     fails on the ledger — rolling back, but only after the second
        #     administrator briefly existed inside an open transaction. Taking
        #     the lock first makes the second attempt wait and then observe the
        #     consumed state, which is the refusal §5 asks for.
        conn.execute("LOCK TABLE platform_admin_genesis IN EXCLUSIVE MODE")

        # 2 · §5: prove the genesis authority has not previously been consumed.
        consumed = conn.execute(
            "SELECT target_user_id FROM platform_admin_genesis"
        ).fetchone()
        if consumed is not None:
            raise GenesisDenied(
                f"the genesis authority was already consumed to establish "
                f"{consumed[0]!r}; GENESIS_REUSE=PROHIBITED. Creating or "
                f"elevating another platform_admin requires a separate "
                f"privilege-management authority."
            )

        # 3 · §5: prove no governed production `platform_admin` already exists.
        #
        #     A separate precondition from the one above, and not redundant: an
        #     administrator could exist without the authority having been
        #     consumed — restored from a backup, or created before this control
        #     existed. Either way the deadlock this authority answers is already
        #     broken, so the authority must not be spent.
        existing = conn.execute(
            "SELECT user_id FROM user_identity WHERE role = %s LIMIT 1",
            (ROLE_PLATFORM_ADMIN,),
        ).fetchone()
        if existing is not None:
            raise GenesisDenied(
                f"a platform_admin already exists ({existing[0]!r}); the genesis "
                f"authority exists only to establish the FIRST one and is not a "
                f"privilege-management path"
            )

        # 4 · The identity. INSERT, never UPDATE and never an upsert: §2 forbids
        #     elevating an existing identity, and an upsert would silently do
        #     exactly that to whoever already held this user_id or address.
        #
        #     `role` is the module constant, not an argument. `tenant_id` is
        #     absent — platform scope, per TENANT-04/TENANT-09.
        conn.execute(
            "INSERT INTO user_identity "
            "(user_id, email, password_hash, role, full_name, tenant_id, provenance) "
            "VALUES (%s, %s, %s, %s, %s, NULL, %s)",
            (user_id, email, password_hash, ROLE_PLATFORM_ADMIN, full_name,
             PROVENANCE_GENESIS),
        )

        # 5 · The governed audit record, in the same transaction.
        audit_event_id = self._persistence.audit.append_event_on(conn, {
            "audit_event_id": str(uuid4()),
            "event_name": EVENT_PLATFORM_ADMIN_GENESIS,
            "actor_id": GENESIS_ACTOR_ID,
            "actor_role": GENESIS_ACTOR_ROLE,
            "tenant_id": GENESIS_EVENT_TENANT,
            "clinic_id": None,
            "resource_type": RESOURCE_TYPE_GENESIS,
            "resource_id": user_id,
            "action_result": "success",
            "reason_code": ruling_reference,
            "correlation_id": correlation_id,
            "occurred_at": _utc_now_iso(),
        })["audit_event_id"]

        # 6 · Consume the authority. The FK on `target_user_id` and the NOT NULL
        #     on `audit_event_id` are the structural half of §6: this row cannot
        #     exist naming an identity that was not created, or an audit event
        #     that was not written.
        conn.execute(
            "INSERT INTO platform_admin_genesis "
            "(target_user_id, granted_role, ruling_reference, audit_event_id) "
            "VALUES (%s, %s, %s, %s)",
            (user_id, ROLE_PLATFORM_ADMIN, ruling_reference, audit_event_id),
        )

        # 7 · §5: verify the intended administrator exists and that the act
        #     created no other privileged identity. Asserted rather than
        #     assumed, and still inside the transaction, so a surprise here
        #     rolls the whole act back instead of reporting a success nobody
        #     checked.
        role_after = conn.execute(
            "SELECT role FROM user_identity WHERE user_id = %s", (user_id,),
        ).fetchone()
        if role_after is None or role_after[0] != ROLE_PLATFORM_ADMIN:
            raise GenesisDenied(
                "the genesis identity is not present with the governed role "
                "after its own insert; rolling back"
            )
        admins = conn.execute(
            "SELECT count(*) FROM user_identity WHERE role = %s",
            (ROLE_PLATFORM_ADMIN,),
        ).fetchone()[0]
        if admins != 1:
            raise GenesisDenied(
                f"the genesis act would leave {admins} platform_admin identities; "
                f"exactly one is authorized. Rolling back."
            )

        return GenesisResult(
            user_id=user_id,
            role=ROLE_PLATFORM_ADMIN,
            audit_event_id=audit_event_id,
            ruling_reference=ruling_reference,
        )


def _utc_now_iso() -> str:
    """The estate's one timestamp format, borrowed rather than reinvented so the
    genesis event sorts and verifies alongside every other governed event."""
    from petcare.audit.audit_service import utc_now_iso

    return utc_now_iso()

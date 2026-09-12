"""The governed tenant-assignment control path.

Sponsor ruling of 12 September 2026, item 3:

> I authorize `platform_admin` as the sole actor role permitted to assign,
> change, or revoke tenant membership… Direct repository access is not an
> authorized operating path.

Before this module the only way to move an identity between tenants was an
operator calling `IDENTITY_REPO.upsert()`. That left no audit event, required no
authorization, and had no revocation path — sufficient for a rehearsal, and not a
governed operating model.

## `TENANT_ASSIGNMENT != ROLE_ASSIGNMENT`

The ruling is explicit: the path *"must not accept a role as an input and must
not create, modify, elevate, downgrade, or otherwise change an identity's role"*.

That is implemented as an **absence**, not as a check. `set_membership` has no
parameter that names a role for the target, and the identity is rewritten with
`dataclasses.replace(identity, tenant_id=…)`, which carries every other field
through unchanged by construction. A parameter that does not exist cannot be
misused, and a field that is never named cannot be overwritten.

`actor_id` and `actor_role` describe the **caller**, are read from the validated
session by the route, and are written only into the audit record's actor fields.
Neither is ever applied to the target.

## Why one transaction

`audit_event` and `user_identity` are in the same database, and the change and
its records must commit together. Ordering alone cannot make this safe:

  record first  → a failed update leaves a log entry for a change that did not happen
  update first  → a failed record leaves an unaudited mutation

Both are worse than a rollback, so there is one transaction and the audit appends
run inside it via `append_event_on`.

## The two-event model

Ruled explicitly. A reassignment from A to B writes a **removal scoped to A** and
an **addition scoped to B**, so each tenant's own audit history records the change
to its own perimeter — `query_events_for_tenant` filters on a single `tenant_id`,
so a single event would leave the tenant an identity LEFT with no record that it
left.

A revocation writes the removal only. A first assignment writes the addition only.

The governed field set is **not** widened, and the old→new pair is deliberately
**not** encoded into `reason_code`: the ruling forbids hiding structured state in
an unvalidated field, and `reason_code` carries the human reason.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Any, Optional

from audit_repository import AuditWriteFailed
from repositories import UserIdentity

#: Governed event names. Read by the audit surface; never compared for authority.
EVENT_MEMBERSHIP_ADDED = "tenant_membership.added"
EVENT_MEMBERSHIP_REMOVED = "tenant_membership.removed"

#: The audit `resource_type` for a membership change. The `resource_id` is the
#: TARGET identity, so a tenant's audit history answers "who was added to, or
#: removed from, this tenant" directly.
RESOURCE_TYPE_MEMBERSHIP = "identity_tenant_membership"


class TenantMembershipDenied(Exception):
    """The change was refused. Nothing was written."""


class TenantMembershipUnavailable(Exception):
    """The governed path cannot operate on this deployment.

    Raised when the configured store is not durable. A membership change that
    died with the process would be a governed act with no record, which is the
    condition this path exists to end — and the ruling states that direct
    repository access is not an authorized operating path, so there is no
    fallback to offer.
    """


@dataclass(frozen=True)
class MembershipChange:
    target_user_id: str
    previous_tenant_id: Optional[str]
    resulting_tenant_id: Optional[str]
    removal_event_id: Optional[str] = None
    addition_event_id: Optional[str] = None

    @property
    def is_revocation(self) -> bool:
        return self.resulting_tenant_id is None


class TenantMembershipService:
    """The only authorized path for changing tenant membership."""

    def __init__(self, persistence: Any) -> None:
        self._persistence = persistence

    # -- readback --------------------------------------------------------

    def read(self, target_user_id: str) -> Optional[UserIdentity]:
        """The verification/readback path the ruling requires."""
        return self._persistence.identities.get_by_user_id(target_user_id)

    # -- the governed change --------------------------------------------

    def set_membership(
        self,
        *,
        target_user_id: str,
        tenant_id: Optional[str],
        actor_id: str,
        actor_role: str,
        reason: str,
        correlation_id: str,
    ) -> MembershipChange:
        """Assign, reassign or revoke tenant membership.

        `tenant_id=None` is a revocation. There is deliberately **no** role
        parameter: see the module docstring.

        Every refusal below happens before anything is written, and the write
        itself is one transaction — so a failure at any point leaves the identity
        and the audit log exactly as they were.
        """
        if not str(reason or "").strip():
            raise TenantMembershipDenied(
                "a membership change must carry a reason; the audit record's "
                "reason_code is where it is kept, and an unexplained change to "
                "who can see what is not reviewable afterwards"
            )

        persistence = self._persistence
        if not getattr(persistence, "is_durable", False) or persistence.pool is None:
            raise TenantMembershipUnavailable(
                "tenant membership is a durable governed act and this deployment "
                "is not configured for a durable store; refusing rather than "
                "making a change that dies with the process"
            )

        pool = persistence.pool
        try:
            with pool.connection() as conn:
                with conn.transaction():
                    return self._apply(
                        conn,
                        target_user_id=target_user_id,
                        tenant_id=tenant_id,
                        actor_id=actor_id,
                        actor_role=actor_role,
                        reason=reason,
                        correlation_id=correlation_id,
                    )
        except (TenantMembershipDenied, TenantMembershipUnavailable, AuditWriteFailed):
            raise
        except Exception as exc:
            raise TenantMembershipDenied(
                f"the membership change could not be completed "
                f"({type(exc).__name__}); nothing was written"
            ) from None

    # -- inside the caller's transaction ---------------------------------

    def _apply(
        self, conn: Any, *, target_user_id: str, tenant_id: Optional[str],
        actor_id: str, actor_role: str, reason: str, correlation_id: str,
    ) -> MembershipChange:
        # 1 · lock the target. FOR UPDATE so two concurrent changes to the same
        #     identity serialise rather than both reading the same previous
        #     tenant and each writing a removal event for it.
        row = conn.execute(
            "SELECT tenant_id, role FROM user_identity WHERE user_id = %s FOR UPDATE",
            (target_user_id,),
        ).fetchone()
        if row is None:
            raise TenantMembershipDenied(
                f"no identity with id {target_user_id!r}"
            )
        previous_tenant_id, role_before = row[0], row[1]

        # 2 · validate the destination against the governed registry. Unknown and
        #     disabled are ONE answer: distinguishing them tells a caller which
        #     tenant ids exist.
        if tenant_id is not None:
            if not str(tenant_id).strip():
                raise TenantMembershipDenied(
                    "a blank tenant is not a revocation; pass no tenant to revoke"
                )
            assignable = conn.execute(
                "SELECT 1 FROM tenant WHERE tenant_id = %s AND status = 'ACTIVE' "
                "AND disabled_at IS NULL FOR SHARE",
                (tenant_id,),
            ).fetchone()
            if assignable is None:
                raise TenantMembershipDenied(
                    f"tenant {tenant_id!r} is not a known, assignable tenant"
                )

        # 3 · refuse a change that is not one. Writing a removal and an addition
        #     for the same tenant would put a membership change into both audit
        #     histories that never happened.
        if previous_tenant_id == tenant_id:
            raise TenantMembershipDenied(
                "the identity already holds that membership; refusing to record "
                "a change that did not occur"
            )

        audit = self._persistence.audit
        removal_id = None
        addition_id = None

        # 4 · removal, scoped to the tenant being LEFT.
        if previous_tenant_id is not None:
            removal_id = audit.append_event_on(conn, _event(
                event_name=EVENT_MEMBERSHIP_REMOVED,
                actor_id=actor_id, actor_role=actor_role,
                tenant_id=previous_tenant_id, target_user_id=target_user_id,
                reason=reason, correlation_id=correlation_id,
            ))["audit_event_id"]

        # 5 · addition, scoped to the tenant being JOINED.
        if tenant_id is not None:
            addition_id = audit.append_event_on(conn, _event(
                event_name=EVENT_MEMBERSHIP_ADDED,
                actor_id=actor_id, actor_role=actor_role,
                tenant_id=tenant_id, target_user_id=target_user_id,
                reason=reason, correlation_id=correlation_id,
            ))["audit_event_id"]

        # 6 · the identity update. ONLY tenant_id is named.
        updated = conn.execute(
            "UPDATE user_identity SET tenant_id = %s WHERE user_id = %s",
            (tenant_id, target_user_id),
        )
        if updated.rowcount != 1:
            raise TenantMembershipDenied(
                "the identity update did not apply; the transaction is rolled back"
            )

        # 7 · the role is unchanged, asserted rather than assumed. A membership
        #     path that altered a role would be a privilege-escalation path, and
        #     the ruling separates the two authorities precisely to prevent one.
        role_after = conn.execute(
            "SELECT role FROM user_identity WHERE user_id = %s", (target_user_id,),
        ).fetchone()[0]
        if role_after != role_before:
            raise TenantMembershipDenied(
                "the membership change altered the identity's role; refusing and "
                "rolling back — TENANT_ASSIGNMENT is not ROLE_ASSIGNMENT"
            )

        return MembershipChange(
            target_user_id=target_user_id,
            previous_tenant_id=previous_tenant_id,
            resulting_tenant_id=tenant_id,
            removal_event_id=removal_id,
            addition_event_id=addition_id,
        )


def _event(
    *, event_name: str, actor_id: str, actor_role: str, tenant_id: str,
    target_user_id: str, reason: str, correlation_id: str,
) -> dict:
    """One governed audit record for a membership change.

    The governed field set is NOT widened. `tenant_id` scopes the event to the
    tenant whose perimeter changed, `resource_id` names the target identity, and
    `reason_code` carries the human reason — never an encoded old→new pair, which
    the ruling forbids as hiding structured state in an unvalidated field.
    """
    from petcare.audit.audit_service import utc_now_iso
    from uuid import uuid4

    return {
        "audit_event_id": str(uuid4()),
        "event_name": event_name,
        "actor_id": actor_id,
        "actor_role": actor_role,
        "tenant_id": tenant_id,
        "clinic_id": None,
        "resource_type": RESOURCE_TYPE_MEMBERSHIP,
        "resource_id": target_user_id,
        "action_result": "success",
        "reason_code": reason,
        "correlation_id": correlation_id,
        "occurred_at": utc_now_iso(),
    }

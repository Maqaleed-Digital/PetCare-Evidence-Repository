"""The tenant registry — PRE-1's structural finding, answered.

PRE-1 asked which tenant three seeded identities belonged to. The search for an
authority returned nothing, and that absence was the finding:

```
TENANT_REGISTRY_EXISTS=NO
TENANT_IS_AN_UNCONSTRAINED_TEXT_FIELD=YES
```

No catalogue table in any migration, no foreign key, no governance artefact
naming a tenant. A tenant was a free-text string each caller supplied, so
`tenant_id = "anything"` was as valid as any real scope — and a typo produced a
new, empty, perfectly functional tenant that nothing would ever report.

This module makes a tenant a **governed object**: something that must exist
before an identity can belong to it.

## What this foundation does NOT do

```
TENANT_ROWS_CREATED=0
```

It creates no tenant. Not `tenant_jeddah_001`, not `tenant_riyadh_001` — those
appear only in EP-05/EP-06 test fixtures and no governance record establishes
them. Creating a production tenant is a Sponsor act, and `TENANT_REGISTRY_STATUS`
in the ruling is `REQUIRED_FOUNDATION`: the constitutional and technical shape is
authorised, the contents are not.

## No default tenant, and no inference

`"platform"` was once the default a missing header fell back to — W0-C removed it
because an omitted header silently granted the platform scope. It does not come
back here as a row. Global or platform-scoped authority is represented by the
ABSENCE of a tenant plus an explicit role, never by a tenant that stands for
"everyone" (TENANT-04, TENANT-09).

Nothing here derives a tenant from an email domain, a role, a route or a name
(TENANT-05). A tenant is supplied by an authority or it is absent.

## Why a disabled tenant still exists

Disabling is recorded, never a deletion. A tenant that is removed cannot be shown
to have been disabled rather than to have never existed — and its identities,
sessions and audit events would lose the only thing that explains what scope they
belonged to.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional, Protocol

TENANT_ACTIVE = "ACTIVE"
TENANT_DISABLED = "DISABLED"
VALID_TENANT_STATUS = frozenset({TENANT_ACTIVE, TENANT_DISABLED})


class TenantDenied(Exception):
    """A tenant-scoped write was refused.

    Raised for an unknown tenant and for a disabled one alike. The caller is not
    told which: both mean "this scope may not receive this assignment", and
    distinguishing them tells an unauthenticated caller which tenant ids exist.
    """


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


@dataclass(frozen=True)
class Tenant:
    tenant_id: str
    display_name: str
    status: str = TENANT_ACTIVE
    created_at: Optional[datetime] = None
    disabled_at: Optional[datetime] = None

    @property
    def is_active(self) -> bool:
        return self.status == TENANT_ACTIVE and self.disabled_at is None


def validate_tenant(tenant: Tenant) -> None:
    if not tenant.tenant_id or not tenant.tenant_id.strip():
        raise TenantDenied("a tenant must have an identifier")
    if tenant.status not in VALID_TENANT_STATUS:
        raise TenantDenied(f"unknown tenant status {tenant.status!r}")
    if not tenant.display_name or not tenant.display_name.strip():
        raise TenantDenied("a tenant must have a display name")
    if tenant.status == TENANT_DISABLED and tenant.disabled_at is None:
        raise TenantDenied(
            "a disabled tenant must record when it was disabled; a status with "
            "no instant cannot be reconciled against anything that happened"
        )


class TenantRepository(Protocol):
    def get(self, tenant_id: str) -> Optional[Tenant]: ...

    def create(self, tenant: Tenant) -> Tenant: ...

    def disable(self, tenant_id: str, *, at: Optional[datetime] = None) -> bool: ...

    def is_assignable(self, tenant_id: str) -> bool:
        """Whether a tenant may receive a NEW authoritative assignment.

        The question the write paths actually ask. Separate from `get` because
        "exists" and "may receive an assignment" are different, and a caller that
        only checked existence would happily add identities to a tenant that was
        disabled last week.
        """
        ...

    def count(self) -> int: ...


class InMemoryTenantRepository:
    """Non-production implementation, performing the same refusals as the schema."""

    def __init__(self) -> None:
        self._tenants: dict[str, Tenant] = {}

    def get(self, tenant_id: str) -> Optional[Tenant]:
        return self._tenants.get(tenant_id)

    def create(self, tenant: Tenant) -> Tenant:
        validate_tenant(tenant)
        if tenant.tenant_id in self._tenants:
            raise TenantDenied(f"tenant {tenant.tenant_id!r} already exists")
        stored = tenant if tenant.created_at else Tenant(
            tenant_id=tenant.tenant_id, display_name=tenant.display_name,
            status=tenant.status, created_at=_utc_now(),
            disabled_at=tenant.disabled_at,
        )
        self._tenants[stored.tenant_id] = stored
        return stored

    def disable(self, tenant_id: str, *, at: Optional[datetime] = None) -> bool:
        existing = self._tenants.get(tenant_id)
        if existing is None or not existing.is_active:
            return False
        self._tenants[tenant_id] = Tenant(
            tenant_id=existing.tenant_id, display_name=existing.display_name,
            status=TENANT_DISABLED, created_at=existing.created_at,
            disabled_at=at or _utc_now(),
        )
        return True

    def is_assignable(self, tenant_id: str) -> bool:
        tenant = self._tenants.get(tenant_id)
        return tenant is not None and tenant.is_active

    def count(self) -> int:
        return len(self._tenants)


def require_assignable(tenants: Optional[TenantRepository], tenant_id: Optional[str]) -> None:
    """The check every tenant-scoped write performs.

    `tenant_id is None` passes: an identity with NO tenant assignment is the
    legitimate state W0-C defines, and it fails closed downstream at
    `require_tenant()` with 403 NO_TENANT_AUTHORITY. A registry that forced every
    identity to hold a tenant would force callers to invent one, which is the
    outcome PRE-1 exists to prevent.

    A `tenants` of None means no registry is configured. That raises rather than
    passing: a write path that silently skipped the check when the registry was
    absent would be a registry that stopped applying exactly when something was
    misconfigured.
    """
    if tenant_id is None:
        return
    if tenants is None:
        raise TenantDenied(
            "no tenant registry is configured, so a tenant-scoped assignment "
            "cannot be validated; refusing rather than accepting it unchecked"
        )
    if not tenants.is_assignable(tenant_id):
        raise TenantDenied(
            f"tenant {tenant_id!r} is not a known, assignable tenant. Tenants are "
            "governed objects: one is supplied by an authority or the assignment "
            "is refused. Nothing here infers a tenant."
        )

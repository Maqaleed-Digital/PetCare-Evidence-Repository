"""FR-01 — live practitioner authority attribute (MVC-BUILD-RUNNER-001 U5).

Ratified criterion AC-FR-01-02 (REQ-MVC-8.32): every regulated act — prescribing,
dispensing — is authorised by a live practitioner authority attribute evaluated at
the moment of the act, IN ADDITION to role and tenant membership. Fails if "any
permission check resolves a regulated act from a role, group, permission string or
token claim without reading a live authority attribute."

A grant is time-bounded (effective_from, expires_at, revoked_at) rather than a
boolean, so the question "did this actor hold authority at that instant" has an
answer after the fact. Attribute administration is never self-service: only the
governed admin path grants or revokes (SPEC REQ-MVC-8.37 matrix note).
"""
from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import datetime
from typing import Optional, Protocol

from repositories import RepositoryDenied

CLASS_VETERINARIAN = "VETERINARIAN"
PROFESSIONAL_CLASSES = frozenset({CLASS_VETERINARIAN})


@dataclass(frozen=True)
class PractitionerAuthorityGrant:
    grant_id: str
    tenant_id: str
    actor_id: str
    professional_class: str
    licence_ref: str
    effective_from: datetime
    granted_by_actor_id: str
    granted_at: datetime
    expires_at: Optional[datetime] = None
    revoked_at: Optional[datetime] = None
    revoked_by_actor_id: Optional[str] = None

    def held_at(self, when: datetime) -> bool:
        if when < self.effective_from:
            return False
        if self.expires_at is not None and when >= self.expires_at:
            return False
        if self.revoked_at is not None and when >= self.revoked_at:
            return False
        return True

    def to_read_model(self) -> dict:
        iso = lambda d: d.isoformat() if d else None  # noqa: E731
        return {"grant_id": self.grant_id, "tenant_id": self.tenant_id, "actor_id": self.actor_id,
                "professional_class": self.professional_class, "licence_ref": self.licence_ref,
                "effective_from": iso(self.effective_from), "expires_at": iso(self.expires_at),
                "revoked_at": iso(self.revoked_at), "granted_by_actor_id": self.granted_by_actor_id,
                "granted_at": iso(self.granted_at), "revoked_by_actor_id": self.revoked_by_actor_id}


def validate_grant(g: PractitionerAuthorityGrant) -> None:
    if g.professional_class not in PROFESSIONAL_CLASSES:
        raise RepositoryDenied(f"professional class {g.professional_class!r} is not one of "
                               f"{sorted(PROFESSIONAL_CLASSES)}")
    if not g.licence_ref.strip():
        raise RepositoryDenied("a licence reference is required")
    if g.expires_at is not None and g.expires_at <= g.effective_from:
        raise RepositoryDenied("expires_at must be after effective_from")


def evaluate(grants: list, *, professional_class: str, when: datetime) -> tuple:
    """(grant in force, or None; the reason when none is) — evaluated at `when`."""
    relevant = [g for g in grants if g.professional_class == professional_class]
    live = [g for g in relevant if g.held_at(when)]
    if live:
        return sorted(live, key=lambda g: (g.effective_from, g.grant_id))[-1], None
    if not relevant:
        return None, "no authority granted"
    last = sorted(relevant, key=lambda g: (g.granted_at, g.grant_id))[-1]
    if last.revoked_at is not None and when >= last.revoked_at:
        return None, f"revoked at {last.revoked_at.isoformat()}"
    if last.expires_at is not None and when >= last.expires_at:
        return None, f"expired at {last.expires_at.isoformat()}"
    return None, f"not yet effective (from {last.effective_from.isoformat()})"


class PractitionerAuthorityRepository(Protocol):
    def grant(self, g: PractitionerAuthorityGrant) -> PractitionerAuthorityGrant: ...
    def revoke(self, grant_id: str, *, tenant_id: str, at: datetime, by: str) -> PractitionerAuthorityGrant: ...
    def grants_for(self, actor_id: str, *, tenant_id: str) -> list: ...


@dataclass
class InMemoryPractitionerAuthorityRepository:
    tenants: object
    _grants: dict = field(default_factory=dict)

    def grant(self, g: PractitionerAuthorityGrant) -> PractitionerAuthorityGrant:
        validate_grant(g)
        if self.tenants.get(g.tenant_id) is None:
            raise RepositoryDenied(f"tenant {g.tenant_id!r} is not registered")
        self._grants[g.grant_id] = g
        return g

    def revoke(self, grant_id: str, *, tenant_id: str, at: datetime, by: str) -> PractitionerAuthorityGrant:
        g = self._grants.get(grant_id)
        if g is None or g.tenant_id != tenant_id:
            raise RepositoryDenied(f"grant {grant_id!r} is not in tenant {tenant_id!r}")
        if g.revoked_at is not None:
            raise RepositoryDenied(f"grant {grant_id!r} is already revoked")
        g = replace(g, revoked_at=at, revoked_by_actor_id=by)
        self._grants[grant_id] = g
        return g

    def grants_for(self, actor_id: str, *, tenant_id: str) -> list:
        return sorted((g for g in self._grants.values() if g.actor_id == actor_id and g.tenant_id == tenant_id),
                      key=lambda g: (g.granted_at, g.grant_id))

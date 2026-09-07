"""W0-I — professional authority, separate from device sealing authority.

BRD V3.2 §28:

> Human/professional authority is **separate from device sealing authority** and
> must not be conflated. Sole-practitioner initial authority grant is specified
> (PRD-14): a one-vet practice must be able to bootstrap without a second
> PRINCIPAL, and the bootstrap is a recorded act, never a silent exception.

Two design decisions follow from that paragraph and shape everything here.

**Authority is time-bounded, not a boolean.** `T-PROF-01` denies attesting a
clinical record as an identity that did not hold authority *at that time*. A
`bool` cannot answer that question: it only knows the present, so a revoked vet
would retroactively appear never to have been authorised, and a newly granted one
would appear to have always been. Grants therefore carry `effective_from` and
`revoked_at`, and every check takes the instant it is asking about.

**Device sealing authority is a different type.** `T-PROF-02` denies deriving
professional authority from a device's sealing authority. The reliable way to
prevent a derivation is to make it unrepresentable: `DeviceSealingAuthority` has
no actor, no professional class, and no method that returns a grant. There is no
conversion to write, so there is none to review.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Callable, Iterable, Optional
from uuid import uuid4


class AuthorityDenied(Exception):
    """Raised when an act requires professional authority that is not held."""


class ProfessionalClass:
    """The professional classes recognised by the estate.

    A closed set. A class that is not listed here cannot be granted, so a typo or
    an invented class fails at the grant rather than silently creating a new
    kind of authority nobody defined.
    """

    VETERINARIAN = "VETERINARIAN"
    VETERINARY_NURSE = "VETERINARY_NURSE"

    ALL = frozenset({VETERINARIAN, VETERINARY_NURSE})


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


@dataclass(frozen=True)
class DeviceSealingAuthority:
    """A device's authority to SEAL a record. Not a person, not a clinician.

    §28 forbids conflating this with professional authority. That is enforced by
    the shape of this type rather than by a rule: it carries no `actor_id` and no
    `professional_class`, so there is nothing here from which a professional
    grant could be constructed even by a caller who wanted to.

    Sealing answers "was this record altered after it was written". Professional
    authority answers "was the person who wrote it entitled to". A device can
    guarantee the first and can say nothing about the second.
    """

    device_id: str
    seal_key_id: str
    sealed_at: datetime = field(default_factory=_utc_now)


@dataclass(frozen=True)
class ProfessionalAuthorityGrant:
    """A recorded grant of human professional authority.

    Immutable. Revocation produces a new grant record rather than mutating this
    one, so the history of who could attest what, and when, survives.
    """

    grant_id: str
    actor_id: str
    tenant_id: str
    clinic_id: Optional[str]
    professional_class: str
    effective_from: datetime
    granted_by: Optional[str]
    grant_reason: str
    sole_practitioner_bootstrap: bool = False
    revoked_at: Optional[datetime] = None

    def held_at(self, when: datetime) -> bool:
        """Whether this grant was in force at `when`.

        Half-open interval `[effective_from, revoked_at)`: an act at the instant
        of revocation is denied. Where authority is ambiguous, the safe reading
        is the one that denies.
        """
        if when < self.effective_from:
            return False
        if self.revoked_at is not None and when >= self.revoked_at:
            return False
        return True


class ProfessionalAuthorityRegistry:
    """Holds grants and answers authority questions about a point in time.

    The registry is deliberately the ONLY source of professional class. Nothing
    here reads a request, a header, or a body — `T-PROF-04` requires the class to
    be established server-side, and the way to guarantee that is for the type
    that answers the question to have no access to the request at all.
    """

    def __init__(self, audit_sink: Optional[Callable[[dict], None]] = None) -> None:
        self._grants: list[ProfessionalAuthorityGrant] = []
        self._audit_sink = audit_sink

    # -- queries ---------------------------------------------------------

    def grants_for(self, actor_id: str) -> list[ProfessionalAuthorityGrant]:
        return [g for g in self._grants if g.actor_id == actor_id]

    def _grant_in_force(
        self, actor_id: str, when: datetime, tenant_id: str
    ) -> Optional[ProfessionalAuthorityGrant]:
        """The grant in force for this actor, in THIS tenant, at `when`.

        Single resolution point for both `held_at` and `professional_class_at`.
        They previously answered independently, and the class lookup omitted the
        tenant filter — so an actor could be correctly DENIED authority in a
        tenant while the attestation still recorded a professional class derived
        from a different tenant's grant. Two questions about one grant must be
        answered by one lookup, or they will eventually disagree.
        """
        for g in self._grants:
            if g.actor_id != actor_id:
                continue
            if g.tenant_id != tenant_id:
                continue
            if g.held_at(when):
                return g
        return None

    def held_at(self, actor_id: str, when: datetime, tenant_id: str) -> bool:
        """Did `actor_id` hold professional authority in `tenant_id` at `when`?

        `tenant_id` is REQUIRED. It was previously optional and defaulted to
        None, which meant "match a grant in any tenant" — a caller who simply
        omitted the argument got a cross-tenant authority check that looked
        correct at every call site. A permissive default in an authorization
        path is a bypass waiting for someone to forget an argument, so there is
        no default: W0-C establishes tenant scope server-side, and an authority
        question that cannot name its tenant has no safe answer.
        """
        return self._grant_in_force(actor_id, when, tenant_id) is not None

    def professional_class_at(
        self, actor_id: str, when: datetime, tenant_id: str
    ) -> Optional[str]:
        """The class held in `tenant_id` at `when`, or None. Never defaulted."""
        g = self._grant_in_force(actor_id, when, tenant_id)
        return g.professional_class if g is not None else None

    # -- acts ------------------------------------------------------------

    def grant(
        self,
        *,
        actor_id: str,
        tenant_id: str,
        professional_class: str,
        granted_by: str,
        grant_reason: str,
        clinic_id: Optional[str] = None,
        effective_from: Optional[datetime] = None,
    ) -> ProfessionalAuthorityGrant:
        """Grant authority. Requires a granting principal — see bootstrap below."""
        if professional_class not in ProfessionalClass.ALL:
            raise AuthorityDenied(f"Unknown professional class: {professional_class!r}")
        if not granted_by:
            raise AuthorityDenied(
                "A grant requires a granting principal. A one-vet practice with no "
                "second principal must use bootstrap_sole_practitioner(), which is "
                "recorded as such."
            )
        g = ProfessionalAuthorityGrant(
            grant_id=str(uuid4()),
            actor_id=actor_id,
            tenant_id=tenant_id,
            clinic_id=clinic_id,
            professional_class=professional_class,
            effective_from=effective_from or _utc_now(),
            granted_by=granted_by,
            grant_reason=grant_reason,
        )
        self._grants.append(g)
        self._record("professional_authority.granted", g)
        return g

    def bootstrap_sole_practitioner(
        self,
        *,
        actor_id: str,
        tenant_id: str,
        professional_class: str,
        grant_reason: str,
        clinic_id: Optional[str] = None,
        effective_from: Optional[datetime] = None,
    ) -> ProfessionalAuthorityGrant:
        """PRD-14 — a one-vet practice bootstraps without a second PRINCIPAL.

        `T-PROF-03`: ALLOWED and RECORDED, never silent. The grant is flagged
        `sole_practitioner_bootstrap=True` and emits its own distinct audit event,
        so a later reader can tell a self-granted authority from one a second
        principal conferred. The whole point of the requirement is that this
        remains visible rather than becoming an unmarked exception.

        Refusing to bootstrap would make single-vet practices unusable; allowing
        it silently would make every grant indistinguishable from a self-grant.
        Recording it is the only option that does neither.
        """
        if professional_class not in ProfessionalClass.ALL:
            raise AuthorityDenied(f"Unknown professional class: {professional_class!r}")
        if not grant_reason:
            raise AuthorityDenied("A sole-practitioner bootstrap requires a recorded reason.")

        g = ProfessionalAuthorityGrant(
            grant_id=str(uuid4()),
            actor_id=actor_id,
            tenant_id=tenant_id,
            clinic_id=clinic_id,
            professional_class=professional_class,
            effective_from=effective_from or _utc_now(),
            granted_by=None,               # no second principal — the fact being recorded
            grant_reason=grant_reason,
            sole_practitioner_bootstrap=True,
        )
        self._grants.append(g)
        self._record("professional_authority.sole_practitioner_bootstrap", g)
        return g

    def revoke(self, grant_id: str, *, revoked_at: Optional[datetime] = None) -> ProfessionalAuthorityGrant:
        """Revoke a grant, preserving what it was.

        The grant is replaced with a revoked copy rather than deleted: records
        attested while it was in force must remain verifiable afterwards.
        """
        for i, g in enumerate(self._grants):
            if g.grant_id == grant_id:
                revoked = ProfessionalAuthorityGrant(
                    **{**g.__dict__, "revoked_at": revoked_at or _utc_now()}
                )
                self._grants[i] = revoked
                self._record("professional_authority.revoked", revoked)
                return revoked
        raise AuthorityDenied(f"No such grant: {grant_id}")

    def attest_clinical_record(
        self,
        *,
        actor_id: str,
        record_id: str,
        occurred_at: datetime,
        tenant_id: str,
    ) -> dict:
        """Attest a clinical record, or deny.

        `T-PROF-01`: authority is checked at `occurred_at` — the moment the
        clinical act happened — not at the moment of attestation. Checking "now"
        would let a vet who has since been granted authority attest records from
        before they held it.
        """
        grant = self._grant_in_force(actor_id, occurred_at, tenant_id)
        if grant is None:
            raise AuthorityDenied(
                f"{actor_id} did not hold professional authority in tenant "
                f"{tenant_id} at {occurred_at.isoformat()}"
            )
        attestation = {
            "record_id": record_id,
            "actor_id": actor_id,
            "tenant_id": tenant_id,
            "grant_id": grant.grant_id,
            "professional_class": grant.professional_class,
            "occurred_at": occurred_at.isoformat(),
            "attested_at": _utc_now().isoformat(),
        }
        self._record("clinical_record.attested", None, extra=attestation)
        return attestation

    # -- audit -----------------------------------------------------------

    def _record(
        self,
        event_name: str,
        grant: Optional[ProfessionalAuthorityGrant],
        extra: Optional[dict] = None,
    ) -> None:
        if self._audit_sink is None:
            return
        payload = {"event_name": event_name}
        if grant is not None:
            payload.update(
                {
                    "grant_id": grant.grant_id,
                    "actor_id": grant.actor_id,
                    "tenant_id": grant.tenant_id,
                    "professional_class": grant.professional_class,
                    "sole_practitioner_bootstrap": grant.sole_practitioner_bootstrap,
                    "granted_by": grant.granted_by,
                    "grant_reason": grant.grant_reason,
                }
            )
        if extra:
            payload.update(extra)
        self._audit_sink(payload)

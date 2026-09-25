"""FR-05 — veterinarian licence registration and verification (MVC-BUILD-RUNNER-001 U10).

AC-FR-05-01: a veterinarian registers WITH licence details and performs no clinical act until
the licence is verified. AC-FR-05-02: the verification and its evidence — who verified, when,
by what method and against what — are persisted and audited, and the licence's expiry is
re-checked at the moment of every clinical act (verification mints the time-bounded
practitioner authority grant of FR-01/U5, which expires with the licence and is evaluated at
each act).

A licence record is immutable once submitted; its verification is a separate, immutable record.
Licensing authority: MEWA / the competent KSA veterinary licensing authority. A live lookup is
the EXTERNAL:VET_LICENSING_AUTHORITY dependency (AC-FR-05-03/04): the port below fails closed,
and until it exists verification is a recorded MANUAL verification by a named staff member.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, time, timedelta, timezone
from typing import Optional, Protocol

from repositories import RepositoryDenied

MANUAL_STAFF, AUTHORITY_LOOKUP = "MANUAL_STAFF", "AUTHORITY_LOOKUP"
METHODS = (MANUAL_STAFF, AUTHORITY_LOOKUP)
SUBMITTED, VERIFIED = "SUBMITTED", "VERIFIED"
MAX_FIELD = 200

# The licensing-authority lookup port (AC-FR-05-03 contract): only LICENCE_VALID verifies.
LICENCE_VALID, LICENCE_NOT_FOUND, LICENCE_LAPSED, LOOKUP_UNAVAILABLE = "VALID", "NOT_FOUND", "LAPSED", "UNAVAILABLE"
LOOKUP_STATUSES = (LICENCE_VALID, LICENCE_NOT_FOUND, LICENCE_LAPSED, LOOKUP_UNAVAILABLE)


@dataclass(frozen=True)
class LookupResult:
    status: str
    detail: str = ""

    @property
    def verified(self) -> bool:
        return self.status == LICENCE_VALID


class LicensingAuthorityPort(Protocol):
    def lookup(self, *, licence_number: str, issuing_authority: str) -> LookupResult: ...


class UnconfiguredLicensingAdapter:
    """The only adapter the served app is built with: no live licensing-authority access exists."""

    def lookup(self, *, licence_number, issuing_authority):
        return LookupResult(LOOKUP_UNAVAILABLE, "no licensing-authority adapter is configured "
                                                "(EXTERNAL:VET_LICENSING_AUTHORITY)")


def normalise_lookup(raw: object) -> LookupResult:
    if isinstance(raw, LookupResult) and raw.status in LOOKUP_STATUSES:
        return raw
    return LookupResult(LICENCE_NOT_FOUND, "unrecognised lookup answer")


@dataclass(frozen=True)
class VetLicence:
    licence_id: str
    actor_id: str
    licence_number: str
    issuing_authority: str
    expires_on: date
    submitted_at: datetime

    def expires_at(self) -> datetime:
        """Valid THROUGH expires_on: the authority lapses at the start of the next UTC day."""
        return datetime.combine(self.expires_on + timedelta(days=1), time(0), tzinfo=timezone.utc)


@dataclass(frozen=True)
class LicenceVerification:
    verification_id: str
    licence_id: str
    tenant_id: str
    verified_by_actor_id: str
    verified_at: datetime
    method: str
    basis: str
    grant_id: str


def validate_licence(lic: VetLicence, *, today: date) -> None:
    if not lic.licence_number.strip() or not lic.issuing_authority.strip():
        raise RepositoryDenied("a licence names its number and issuing authority")
    if len(lic.licence_number) > MAX_FIELD or len(lic.issuing_authority) > MAX_FIELD:
        raise RepositoryDenied("licence details are too long")
    if lic.expires_on < today:
        raise RepositoryDenied("the licence has already expired")


def validate_verification(v: LicenceVerification) -> None:
    if v.method not in METHODS:
        raise RepositoryDenied(f"unknown verification method {v.method!r}")
    if not v.verified_by_actor_id.strip() or not v.basis.strip():
        raise RepositoryDenied("a verification names its verifier and what it was checked against")


class LicenceRepository(Protocol):
    def submit(self, lic: VetLicence) -> VetLicence: ...
    def get(self, licence_id: str): ...
    def for_actor(self, actor_id: str) -> list: ...
    def all(self) -> list: ...
    def record_verification(self, v: LicenceVerification) -> LicenceVerification: ...
    def verification_of(self, licence_id: str): ...


@dataclass
class InMemoryLicenceRepository:
    _licences: dict = field(default_factory=dict)
    _verifications: dict = field(default_factory=dict)

    def submit(self, lic):
        validate_licence(lic, today=lic.submitted_at.date())
        self._licences[lic.licence_id] = lic
        return lic

    def get(self, licence_id):
        return self._licences.get(licence_id)

    def for_actor(self, actor_id):
        return sorted((x for x in self._licences.values() if x.actor_id == actor_id),
                      key=lambda x: (x.submitted_at, x.licence_id))

    def all(self):
        return sorted(self._licences.values(), key=lambda x: (x.submitted_at, x.licence_id))

    def record_verification(self, v):
        validate_verification(v)
        if v.licence_id not in self._licences:
            raise RepositoryDenied("verification refers to no licence")
        if v.licence_id in self._verifications:
            raise RepositoryDenied("the licence is already verified")
        self._verifications[v.licence_id] = v
        return v

    def verification_of(self, licence_id):
        return self._verifications.get(licence_id)

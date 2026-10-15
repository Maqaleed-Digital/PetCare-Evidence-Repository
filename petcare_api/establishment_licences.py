"""X-30 / J-O8 — establishment licences of the supplying location (MVC-EPC-D-001 D2h, Sponsor ruling R18.3).

Order fulfilment (POST /api/orders/{id}/deliver) is the regulated dispensing act: stock leaves as SUPPLY movements from the
location the staff name — the pharmacy/stock location (FR-15's "routed pharmacy"). That location is the applicable regulated
establishment. Delivery is accepted only when the location holds a licence, recorded in the SAME tenant, that is valid on the
Asia/Riyadh calendar date of the act (valid THROUGH expires_on, as for veterinary licences, X-22). A licence is entity data the
product validates; it is recorded by a platform administrator with what it was checked against (R18.2 distinguishes such data
from a regulatory determination, which this is not).

R19.2 (D2k): the record also carries the licence type, its scope (X-31) and a reference to the evidence document the
administrator checked (X-32). A row without them (recorded before migration 0061) is INCOMPLETE and never validates a delivery
(fail closed). A location may hold more than one licence; any one complete licence valid on the date suffices. R19.3: recording a
licence is an administrator's attestation, NOT verification against the issuing authority's registry — that is an external
dependency (X-33) this module does not claim.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import date, datetime
from typing import Optional, Protocol

from repositories import RepositoryDenied

MAX_FIELD = 200
#: R19.2 fields a licence must carry to validate a delivery (X-31 type/scope, X-32 evidence-document reference).
R19_2_FIELDS = ("licence_type", "scope", "evidence_document_ref")


@dataclass(frozen=True)
class EstablishmentLicence:
    licence_id: str
    tenant_id: str
    location_id: str
    licence_number: str
    issuing_authority: str
    expires_on: date
    basis: str
    recorded_by_actor_id: str
    recorded_at: datetime
    #: R19.2. None only on a row recorded before migration 0061; such a row is incomplete (see `is_complete`).
    licence_type: Optional[str] = None
    scope: Optional[str] = None
    evidence_document_ref: Optional[str] = None

    def is_complete(self) -> bool:
        return all(getattr(self, name) and getattr(self, name).strip() for name in R19_2_FIELDS)

    def to_read_model(self) -> dict:
        d = asdict(self)
        d["expires_on"] = self.expires_on.isoformat()
        d["recorded_at"] = self.recorded_at.isoformat()
        d["complete"] = self.is_complete()
        d["registry_verified"] = False          # R19.3: attestation only; registry verification is X-33 (external)
        return d


def validate_establishment_licence(lic: EstablishmentLicence) -> None:
    for name in ("licence_number", "issuing_authority", "basis", "location_id", "tenant_id", "recorded_by_actor_id",
                 *R19_2_FIELDS):
        v = getattr(lic, name)
        if not v or not v.strip():
            raise RepositoryDenied(f"an establishment licence names its {name.replace('_', ' ')}")
        if len(v) > MAX_FIELD:
            raise RepositoryDenied(f"{name} is too long")


def valid_on(licences: list, on: date) -> Optional[EstablishmentLicence]:
    """The COMPLETE licence valid THROUGH `on` with the latest expiry, else None (fail closed)."""
    live = [l for l in licences if l.expires_on >= on and l.is_complete()]
    return max(live, key=lambda l: (l.expires_on, l.licence_id)) if live else None


class EstablishmentLicenceRepository(Protocol):
    def record(self, lic: EstablishmentLicence) -> EstablishmentLicence: ...
    def for_location(self, location_id: str, *, tenant_id: str) -> list: ...
    def for_tenant(self, *, tenant_id: str) -> list: ...


@dataclass
class InMemoryEstablishmentLicenceRepository:
    _rows: dict = field(default_factory=dict)

    def record(self, lic):
        validate_establishment_licence(lic)
        self._rows[lic.licence_id] = lic
        return lic

    def for_location(self, location_id, *, tenant_id):
        return sorted((l for l in self._rows.values() if l.location_id == location_id and l.tenant_id == tenant_id),
                      key=lambda l: (l.recorded_at, l.licence_id))

    def for_tenant(self, *, tenant_id):
        return sorted((l for l in self._rows.values() if l.tenant_id == tenant_id), key=lambda l: (l.recorded_at, l.licence_id))

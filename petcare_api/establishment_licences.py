"""X-30 / J-O8 — establishment licences of the supplying location (MVC-EPC-D-001 D2h, Sponsor ruling R18.3).

Order fulfilment (POST /api/orders/{id}/deliver) is the regulated dispensing act: stock leaves as SUPPLY movements from the
location the staff name — the pharmacy/stock location (FR-15's "routed pharmacy"). That location is the applicable regulated
establishment. Delivery is accepted only when the location holds a licence, recorded in the SAME tenant, that is valid on the
Asia/Riyadh calendar date of the act (valid THROUGH expires_on, as for veterinary licences, X-22). A licence is entity data the
product validates; it is recorded by a platform administrator with what it was checked against (R18.2 distinguishes such data
from a regulatory determination, which this is not).
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import date, datetime
from typing import Optional, Protocol

from repositories import RepositoryDenied

MAX_FIELD = 200


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

    def to_read_model(self) -> dict:
        d = asdict(self)
        d["expires_on"] = self.expires_on.isoformat()
        d["recorded_at"] = self.recorded_at.isoformat()
        return d


def validate_establishment_licence(lic: EstablishmentLicence) -> None:
    for name in ("licence_number", "issuing_authority", "basis", "location_id", "tenant_id", "recorded_by_actor_id"):
        v = getattr(lic, name)
        if not v or not v.strip():
            raise RepositoryDenied(f"an establishment licence names its {name.replace('_', ' ')}")
        if len(v) > MAX_FIELD:
            raise RepositoryDenied(f"{name} is too long")


def valid_on(licences: list, on: date) -> Optional[EstablishmentLicence]:
    """The licence valid THROUGH `on` with the latest expiry, else None (fail closed)."""
    live = [l for l in licences if l.expires_on >= on]
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

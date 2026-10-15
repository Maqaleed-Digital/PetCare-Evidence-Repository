"""CO-06 — pre-visit intake with photos (MVC-EPC-D-001 Lane D, D2p; R21.4 remaining owner screens).

Before an upcoming consultation the owner tells the clinic why they are coming — the reason, since when, whether the pet is
eating and drinking normally, what it currently takes — and may attach up to MAX_PHOTOS photographs. One intake per booking,
insert-only: what the veterinarian reads is what the owner submitted, never silently replaced. The intake is owned by the
booking: owner, tenant, booking and pet are written from the session and the booking by petcare_api/main.py, never from the
request. Photos are images only (no documents) and live in the governed document store under server-generated keys, written
before the rows that name them, so a row never names a missing object (the CO-11 / FR-14 order).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Optional, Protocol

from repositories import RepositoryDenied

MAX_PHOTOS = 5
PHOTO_CONTENT_TYPES = frozenset({"image/jpeg", "image/png", "image/heic"})
MAX_REASON = 500
MAX_MEDICATIONS = 500
EATING = ("YES", "NO", "UNSURE")


@dataclass(frozen=True)
class IntakePhoto:
    photo_id: str
    intake_id: str
    tenant_id: str
    position: int
    filename: str
    content_type: str
    byte_size: int
    content_sha256: str
    storage_key: str
    uploaded_at: datetime

    def to_read_model(self) -> dict:
        return {"photo_id": self.photo_id, "position": self.position, "filename": self.filename, "content_type": self.content_type,
                "byte_size": self.byte_size, "content_sha256": self.content_sha256,
                "uploaded_at": self.uploaded_at.isoformat()}


@dataclass(frozen=True)
class PreVisitIntake:
    intake_id: str
    tenant_id: str
    booking_id: str
    owner_id: str
    pet_id: str
    reason: str
    symptoms_since: Optional[date]
    eating_normally: str
    current_medications: str
    submitted_at: datetime
    photos: tuple = ()

    def to_read_model(self) -> dict:
        return {"intake_id": self.intake_id, "booking_id": self.booking_id, "pet_id": self.pet_id, "reason": self.reason,
                "symptoms_since": self.symptoms_since.isoformat() if self.symptoms_since else None,
                "eating_normally": self.eating_normally, "current_medications": self.current_medications,
                "submitted_at": self.submitted_at.isoformat(), "photos": [p.to_read_model() for p in self.photos]}


def validate_intake(i: PreVisitIntake) -> None:
    if not i.reason.strip() or len(i.reason) > MAX_REASON:
        raise RepositoryDenied(f"a reason of 1..{MAX_REASON} characters is required")
    if len(i.current_medications) > MAX_MEDICATIONS:
        raise RepositoryDenied(f"current medications are at most {MAX_MEDICATIONS} characters")
    if i.eating_normally not in EATING:
        raise RepositoryDenied(f"eating_normally must be one of {EATING}")
    if i.symptoms_since is not None and i.symptoms_since > i.submitted_at.date():
        raise RepositoryDenied("symptoms cannot start after the intake is submitted")
    if len(i.photos) > MAX_PHOTOS:
        raise RepositoryDenied(f"at most {MAX_PHOTOS} photos")
    if [p.position for p in i.photos] != list(range(len(i.photos))):
        raise RepositoryDenied("photos keep the order the owner attached them: positions 0..n-1")
    for p in i.photos:
        if p.content_type not in PHOTO_CONTENT_TYPES:
            raise RepositoryDenied(f"a photo is one of {sorted(PHOTO_CONTENT_TYPES)}")
        if p.intake_id != i.intake_id or p.tenant_id != i.tenant_id or not p.storage_key or p.byte_size <= 0:
            raise RepositoryDenied("a photo names its intake, tenant and stored object")


class IntakeExists(Exception):
    """The booking already has its intake (one per booking, insert-only)."""


class PreVisitIntakeRepository(Protocol):
    def create(self, i: PreVisitIntake) -> PreVisitIntake: ...
    def for_booking(self, booking_id: str, *, tenant_id: str) -> Optional[PreVisitIntake]: ...


@dataclass
class InMemoryPreVisitIntakeRepository:
    _rows: dict = field(default_factory=dict)

    def create(self, i):
        validate_intake(i)
        if any(x.booking_id == i.booking_id and x.tenant_id == i.tenant_id for x in self._rows.values()):
            raise IntakeExists(i.booking_id)
        self._rows[i.intake_id] = i
        return i

    def for_booking(self, booking_id, *, tenant_id):
        return next((x for x in self._rows.values() if x.booking_id == booking_id and x.tenant_id == tenant_id), None)

"""J-O5 — an owner books a consultation with a veterinarian of their clinic; views, reschedules and cancels it
(MVC-EPC-D-001 Lane D, D2e; closes X-26 together with the session binding of the legacy /api/appointments stub).

Every identity is taken from the session: the owner is the caller, the tenant is the session tenant. The request only
SELECTS a pet, a veterinarian and a slot, and each selector is validated against the session tenant — the pet must be
the caller's own pet, the veterinarian a veterinarian identity of the same tenant. A slot is held by at most one live
booking per veterinarian (the PostgreSQL store enforces it with a partial unique index as well).

Slots: until veterinarians publish their own availability (J-V2, D3), a veterinarian's bookable slots are the clinic
default hours below — 30-minute slots, 09:00–17:00 Asia/Riyadh, the next 14 days, minus slots already booked. This is a
recorded implementation assumption (receipt D2E-DEFAULT-HOURS), not a ratified schedule; J-V2 replaces it.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import date, datetime, time, timedelta, timezone
from typing import Optional, Protocol
from zoneinfo import ZoneInfo

from repositories import RepositoryDenied

BOOKED, CANCELLED = "BOOKED", "CANCELLED"
STATUSES = (BOOKED, CANCELLED)
IN_CLINIC, VIDEO = "IN_CLINIC", "VIDEO"
MODES = (IN_CLINIC, VIDEO)

CLINIC_ZONE = ZoneInfo("Asia/Riyadh")
SLOT_MINUTES = 30
OPENS, CLOSES = time(9, 0), time(17, 0)
HORIZON_DAYS = 14
MAX_REASON = 500


class SlotTaken(RepositoryDenied):
    """The veterinarian already has a live booking at that instant."""


@dataclass(frozen=True)
class Booking:
    booking_id: str
    tenant_id: str
    owner_id: str
    pet_id: str
    veterinarian_id: str
    mode: str
    starts_at: datetime
    status: str
    reason: str
    created_by_actor_id: str
    created_at: datetime
    updated_at: datetime

    def to_read_model(self) -> dict:
        return {"booking_id": self.booking_id, "tenant_id": self.tenant_id, "owner_id": self.owner_id,
                "pet_id": self.pet_id, "veterinarian_id": self.veterinarian_id, "mode": self.mode,
                "starts_at": self.starts_at.astimezone(timezone.utc).isoformat(), "status": self.status,
                "reason": self.reason, "created_at": self.created_at.isoformat(),
                "updated_at": self.updated_at.isoformat()}


def default_slots(on: date) -> list:
    """The clinic default hours on a local calendar day, as UTC instants."""
    out, t = [], datetime.combine(on, OPENS, tzinfo=CLINIC_ZONE)
    end = datetime.combine(on, CLOSES, tzinfo=CLINIC_ZONE)
    while t < end:
        out.append(t.astimezone(timezone.utc))
        t += timedelta(minutes=SLOT_MINUTES)
    return out


def is_bookable_instant(at: datetime, *, now: datetime) -> bool:
    """A default-hours slot start, strictly in the future and inside the booking horizon."""
    if at.tzinfo is None or at <= now:
        return False
    local = at.astimezone(CLINIC_ZONE)
    if (local.date() - now.astimezone(CLINIC_ZONE).date()).days > HORIZON_DAYS:
        return False
    return at.astimezone(timezone.utc) in default_slots(local.date())


def validate_booking(b: Booking) -> None:
    if b.mode not in MODES:
        raise RepositoryDenied(f"unknown consultation mode {b.mode!r}")
    if b.status not in STATUSES:
        raise RepositoryDenied(f"unknown booking status {b.status!r}")
    if len(b.reason) > MAX_REASON:
        raise RepositoryDenied("the reason is too long")
    if not (b.owner_id and b.pet_id and b.veterinarian_id and b.tenant_id):
        raise RepositoryDenied("a booking names its owner, pet, veterinarian and tenant")


class BookingRepository(Protocol):
    def create(self, b: Booking) -> Booking: ...
    def get(self, booking_id: str, *, tenant_id: str) -> Optional[Booking]: ...
    def list_for_owner(self, owner_id: str, *, tenant_id: str) -> list: ...
    def taken_starts(self, veterinarian_id: str, *, tenant_id: str) -> set: ...
    def reschedule(self, booking_id: str, starts_at: datetime, *, tenant_id: str, at: datetime) -> Booking: ...
    def cancel(self, booking_id: str, *, tenant_id: str, at: datetime) -> Booking: ...


class InMemoryBookingRepository:
    def __init__(self) -> None:
        self._rows: dict = {}

    def _clash(self, b: Booking, starts_at: datetime) -> bool:
        return any(o.booking_id != b.booking_id and o.status == BOOKED and o.tenant_id == b.tenant_id
                   and o.veterinarian_id == b.veterinarian_id and o.starts_at == starts_at
                   for o in self._rows.values())

    def create(self, b: Booking) -> Booking:
        validate_booking(b)
        if self._clash(b, b.starts_at):
            raise SlotTaken("that slot is already booked")
        self._rows[b.booking_id] = b
        return b

    def get(self, booking_id, *, tenant_id):
        b = self._rows.get(booking_id)
        return b if b is not None and b.tenant_id == tenant_id else None

    def list_for_owner(self, owner_id, *, tenant_id):
        return sorted((b for b in self._rows.values() if b.owner_id == owner_id and b.tenant_id == tenant_id),
                      key=lambda b: (b.starts_at, b.booking_id))

    def taken_starts(self, veterinarian_id, *, tenant_id):
        return {b.starts_at for b in self._rows.values()
                if b.status == BOOKED and b.tenant_id == tenant_id and b.veterinarian_id == veterinarian_id}

    def reschedule(self, booking_id, starts_at, *, tenant_id, at):
        b = self.get(booking_id, tenant_id=tenant_id)
        if b is None or b.status != BOOKED:
            raise RepositoryDenied("only a live booking can be rescheduled")
        if self._clash(b, starts_at):
            raise SlotTaken("that slot is already booked")
        self._rows[booking_id] = replace(b, starts_at=starts_at, updated_at=at)
        return self._rows[booking_id]

    def cancel(self, booking_id, *, tenant_id, at):
        b = self.get(booking_id, tenant_id=tenant_id)
        if b is None or b.status != BOOKED:
            raise RepositoryDenied("only a live booking can be cancelled")
        self._rows[booking_id] = replace(b, status=CANCELLED, updated_at=at)
        return self._rows[booking_id]

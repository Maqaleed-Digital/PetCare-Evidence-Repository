"""J-V2 — a veterinarian publishes their availability; their queue (MVC-EPC-D-001 Lane D, D3b; R21.4 D3 veterinarian journeys).

A veterinarian publishes a WEEKLY schedule: windows (weekday, opens, closes) on the Asia/Riyadh clock, each on the 30-minute slot
grid, non-overlapping within a day. Publishing is insert-only and versioned — the latest published plan is the schedule; earlier
plans stay as the record of what was offered when. Owners' bookable slots for that veterinarian come from it (bookings.py).

A veterinarian who has never published keeps the clinic default hours (D2E-DEFAULT-HOURS, 09:00-17:00) — an implementation
assumption recorded in the D3b receipt, kept so that a clinic is bookable before its veterinarians publish. A published plan
with no window means the veterinarian offers no slots. Existing bookings are never moved or cancelled by a new plan.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, time
from typing import Optional, Protocol

from repositories import RepositoryDenied

SLOT_MINUTES = 30
WEEKDAYS = range(7)            # Python weekday(): 0 = Monday … 6 = Sunday (Asia/Riyadh calendar day)


@dataclass(frozen=True)
class Window:
    weekday: int
    opens: time
    closes: time

    def to_read_model(self) -> dict:
        return {"weekday": self.weekday, "opens": self.opens.strftime("%H:%M"), "closes": self.closes.strftime("%H:%M")}


@dataclass(frozen=True)
class AvailabilityPlan:
    plan_id: str
    tenant_id: str
    veterinarian_id: str
    windows: tuple
    published_at: datetime

    def to_read_model(self) -> dict:
        return {"plan_id": self.plan_id, "published_at": self.published_at.isoformat(),
                "windows": [w.to_read_model() for w in sorted(self.windows, key=lambda w: (w.weekday, w.opens))]}


def _on_grid(t: time) -> bool:
    return t.second == 0 and t.microsecond == 0 and t.minute % SLOT_MINUTES == 0


def validate_plan(p: AvailabilityPlan) -> None:
    if not (p.tenant_id and p.veterinarian_id):
        raise RepositoryDenied("a plan names its veterinarian and tenant")
    by_day: dict = {}
    for w in p.windows:
        if w.weekday not in WEEKDAYS:
            raise RepositoryDenied("a weekday is 0 (Monday) .. 6 (Sunday)")
        if not (_on_grid(w.opens) and _on_grid(w.closes)):
            raise RepositoryDenied(f"windows start and end on the {SLOT_MINUTES}-minute grid")
        if w.opens >= w.closes:
            raise RepositoryDenied("a window opens before it closes, within one day")
        by_day.setdefault(w.weekday, []).append(w)
    for day in by_day.values():
        day.sort(key=lambda w: w.opens)
        if any(a.closes > b.opens for a, b in zip(day, day[1:])):
            raise RepositoryDenied("windows of one day do not overlap")


class AvailabilityRepository(Protocol):
    def publish(self, p: AvailabilityPlan) -> AvailabilityPlan: ...
    def latest(self, veterinarian_id: str, *, tenant_id: str) -> Optional[AvailabilityPlan]: ...


@dataclass
class InMemoryAvailabilityRepository:
    _plans: list = field(default_factory=list)

    def publish(self, p):
        validate_plan(p)
        self._plans.append(p)
        return p

    def latest(self, veterinarian_id, *, tenant_id):
        mine = [p for p in self._plans if p.veterinarian_id == veterinarian_id and p.tenant_id == tenant_id]
        return max(mine, key=lambda p: (p.published_at, p.plan_id)) if mine else None

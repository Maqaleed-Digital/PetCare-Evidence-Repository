"""CO-10 — visit summary and care plan (MVC-EPC-D-001 Lane D, D2q; R21.4 remaining owner screens).

The owner's summary of ONE completed consultation is assembled only from records the platform already holds for that
consultation — the consultation itself, the outcome its veterinarian recorded (FR-06), and the prescriptions issued under that
consultation's session (FR-14) — plus the CARE PLAN: one insert-only record per consultation, written by that consultation's
veterinarian after the outcome, holding the home-care instructions and an optional follow-up date. Nothing is inferred:
medical records and care-due items carry no consultation link, so they are not attached to a visit by time or guesswork.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Optional, Protocol

from ksa_calendar import ksa_date
from repositories import RepositoryDenied

MAX_INSTRUCTIONS = 2000


@dataclass(frozen=True)
class CarePlan:
    session_id: str
    tenant_id: str
    instructions: str
    follow_up_on: Optional[date]
    recorded_by_actor_id: str
    recorded_at: datetime

    def to_read_model(self) -> dict:
        return {"instructions": self.instructions,
                "follow_up_on": self.follow_up_on.isoformat() if self.follow_up_on else None,
                "recorded_by_actor_id": self.recorded_by_actor_id, "recorded_at": self.recorded_at.isoformat()}


def validate_care_plan(p: CarePlan) -> None:
    if not p.instructions.strip() or len(p.instructions) > MAX_INSTRUCTIONS:
        raise RepositoryDenied(f"care-plan instructions are 1..{MAX_INSTRUCTIONS} characters")
    if p.follow_up_on is not None and p.follow_up_on < ksa_date(p.recorded_at):
        raise RepositoryDenied("a follow-up date cannot be before the care plan is recorded (Asia/Riyadh)")
    if not p.recorded_by_actor_id.strip():
        raise RepositoryDenied("a care plan names who recorded it")


class CarePlanExists(Exception):
    """The consultation already has its care plan (one per consultation, insert-only)."""


class CarePlanRepository(Protocol):
    def create(self, p: CarePlan) -> CarePlan: ...
    def for_session(self, session_id: str, *, tenant_id: str) -> Optional[CarePlan]: ...


@dataclass
class InMemoryCarePlanRepository:
    _rows: dict = field(default_factory=dict)

    def create(self, p):
        validate_care_plan(p)
        if (p.tenant_id, p.session_id) in self._rows:
            raise CarePlanExists(p.session_id)
        self._rows[(p.tenant_id, p.session_id)] = p
        return p

    def for_session(self, session_id, *, tenant_id):
        return self._rows.get((tenant_id, session_id))


def visit_summary(consultation, outcome, *, pet_name, vet_name, prescriptions, plan) -> dict:
    """The owner's summary of one COMPLETED consultation. `prescriptions` must already be those issued under this
    consultation's session for this pet; they are listed with what the owner needs to follow them."""
    return {"session_id": consultation.session_id, "pet": {"pet_id": consultation.pet_id, "name": pet_name},
            "veterinarian": {"user_id": consultation.veterinarian_id, "name": vet_name}, "mode": consultation.mode,
            "visited_at": consultation.created_at.isoformat(),
            "outcome": {"text": outcome.outcome, "recorded_at": outcome.recorded_at.isoformat()},
            "prescriptions": [{"prescription_id": rx.prescription_id, "medication_name": rx.medication_name,
                               "dosage": rx.dosage, "instructions": rx.instructions, "status": rx.status}
                              for rx in sorted(prescriptions, key=lambda r: (r.issued_at, r.prescription_id))],
            "care_plan": plan.to_read_model() if plan else None}

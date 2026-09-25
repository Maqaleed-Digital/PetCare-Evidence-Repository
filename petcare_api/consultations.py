"""FR-06 — durable consultations and the telemedicine counsel gate (MVC-BUILD-RUNNER-001 U11).

AC-FR-06-04: the consultation, its participants and its outcome are persisted and audited within
the owner's tenant. A consultation and its outcome are immutable records; status is derived
(an outcome completes it). Participants are identities of the tenant: the owner an `owner`, the
veterinarian a `veterinarian`.

AC-FR-06-05 (dependency COUNSEL:REG-02_TELEMEDICINE): remote veterinary consultation stays
FAIL-CLOSED until a counsel determination that it is lawful is RECORDED. The determination is a
governed record with no served write path — engineering cannot open the gate.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Protocol

from repositories import RepositoryDenied

MODE_IN_PERSON, MODE_REMOTE_VIDEO = "IN_PERSON", "REMOTE_VIDEO"
MODES = (MODE_IN_PERSON, MODE_REMOTE_VIDEO)
STATUS_REQUESTED, STATUS_COMPLETED = "REQUESTED", "COMPLETED"
MAX_OUTCOME = 4000

REG02_TELEMEDICINE = "REG-02_TELEMEDICINE"
LAWFUL, NOT_LAWFUL = "LAWFUL", "NOT_LAWFUL"


@dataclass(frozen=True)
class Consultation:
    session_id: str
    tenant_id: str
    pet_id: str
    owner_id: str
    veterinarian_id: str
    requested_by_actor_id: str
    mode: str
    created_at: datetime
    clinic_id: Optional[str] = None


@dataclass(frozen=True)
class ConsultationOutcome:
    session_id: str
    tenant_id: str
    outcome: str
    recorded_by_actor_id: str
    recorded_at: datetime


@dataclass(frozen=True)
class RegulatoryDetermination:
    determination_id: str
    subject: str
    decision: str
    form: str
    reference: str
    recorded_by: str
    recorded_at: datetime


def read_model(c: Consultation, o: Optional[ConsultationOutcome]) -> dict:
    return {"session_id": c.session_id, "tenant_id": c.tenant_id, "pet_id": c.pet_id, "owner_id": c.owner_id,
            "veterinarian_id": c.veterinarian_id, "clinic_id": c.clinic_id, "mode": c.mode,
            "requested_by_actor_id": c.requested_by_actor_id,
            "status": STATUS_COMPLETED if o else STATUS_REQUESTED, "created_at": c.created_at.isoformat(),
            "started_at": None, "cancelled_at": None,
            "completed_at": o.recorded_at.isoformat() if o else None,
            "outcome": None if o is None else {"outcome": o.outcome, "recorded_by_actor_id": o.recorded_by_actor_id,
                                               "recorded_at": o.recorded_at.isoformat()}}


def validate_consultation(c: Consultation) -> None:
    if c.mode not in MODES:
        raise RepositoryDenied(f"unknown consultation mode {c.mode!r}")
    for f in (c.pet_id, c.owner_id, c.veterinarian_id, c.requested_by_actor_id):
        if not f or not f.strip():
            raise RepositoryDenied("a consultation names its pet, both participants and who requested it")


def validate_outcome(o: ConsultationOutcome) -> None:
    if not o.outcome.strip() or len(o.outcome) > MAX_OUTCOME:
        raise RepositoryDenied(f"an outcome is 1..{MAX_OUTCOME} characters")
    if not o.recorded_by_actor_id.strip():
        raise RepositoryDenied("an outcome names who recorded it")


def remote_consultation_lawful(determinations: list) -> Optional[RegulatoryDetermination]:
    """The latest REG-02 determination if it says LAWFUL, else None (fail closed)."""
    reg = sorted((d for d in determinations if d.subject == REG02_TELEMEDICINE), key=lambda d: d.recorded_at)
    return reg[-1] if reg and reg[-1].decision == LAWFUL else None


class ConsultationRepository(Protocol):
    def create(self, c: Consultation) -> Consultation: ...
    def get(self, session_id: str, *, tenant_id: str): ...
    def for_tenant(self, tenant_id: str) -> list: ...
    def record_outcome(self, o: ConsultationOutcome) -> ConsultationOutcome: ...
    def outcome_of(self, session_id: str, *, tenant_id: str): ...
    def determinations(self) -> list: ...


@dataclass
class InMemoryConsultationRepository:
    tenants: object
    _consultations: dict = field(default_factory=dict)
    _outcomes: dict = field(default_factory=dict)
    _determinations: list = field(default_factory=list)

    def create(self, c):
        validate_consultation(c)
        if self.tenants.get(c.tenant_id) is None:
            raise RepositoryDenied(f"tenant {c.tenant_id!r} is not registered")
        self._consultations[c.session_id] = c
        return c

    def get(self, session_id, *, tenant_id):
        c = self._consultations.get(session_id)
        return c if c is not None and c.tenant_id == tenant_id else None

    def for_tenant(self, tenant_id):
        return sorted((c for c in self._consultations.values() if c.tenant_id == tenant_id),
                      key=lambda c: (c.created_at, c.session_id))

    def record_outcome(self, o):
        validate_outcome(o)
        if self.get(o.session_id, tenant_id=o.tenant_id) is None:
            raise RepositoryDenied("outcome refers to no consultation in this tenant")
        if o.session_id in self._outcomes:
            raise RepositoryDenied("the consultation already has an outcome")
        self._outcomes[o.session_id] = o
        return o

    def outcome_of(self, session_id, *, tenant_id):
        o = self._outcomes.get(session_id)
        return o if o is not None and o.tenant_id == tenant_id else None

    def record_determination(self, d: RegulatoryDetermination) -> RegulatoryDetermination:
        """Governed record only (counsel/Sponsor act). No served route calls this."""
        self._determinations.append(d)
        return d

    def determinations(self):
        return list(self._determinations)

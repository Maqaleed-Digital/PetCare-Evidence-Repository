"""Prescriptions as a stored record, and the transitions it may make.

FR-14. The serving layer held these in `_prescriptions`, a module-level dict.
W0-G made the argument against that shape for the audit log and it applies here
with more force: a prescription is a clinical record. A store that dies with the
process means a dispensing decision cannot be shown to have happened, a second
instance cannot see what the first one issued, and "was this dispensed?" has a
different answer depending on which process is asked.

## The state machine, and why the middle state exists

    ISSUED  ->  VET_VERIFIED  ->  DISPENSED

`VET_VERIFIED` is new. Before it the lifecycle was ISSUED -> DISPENSED and the
dispense route's only state guard was `status == "ISSUED"` — so a prescription
was dispensable the instant it existed, and the verification step the pilot
workflow is named after had no representation anywhere. Verification was not
weakly enforced; it was absent.

The transitions are defined once, here, and both repositories enforce them. The
database enforces them a second time in CHECK constraints (migration 0036).
That is deliberate duplication of a rule rather than of a mechanism: the schema
catches a writer that bypasses this module, and this module gives the writer an
error it can act on instead of an IntegrityError.

## What is NOT here

Authorization. This module answers "may the RECORD move from A to B", never "may
this CALLER move it". `main.py` answers the second question from the validated
session, and it answers it first. Merging them would put an authorization
decision behind an interface with two implementations — two places for an
authorization bug to live, which is the argument `repositories.py` already makes.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime, timezone
from typing import Optional, Protocol

from repositories import RepositoryDenied
from tenants import TenantRepository

# ---------------------------------------------------------------------------
# The governed lifecycle
# ---------------------------------------------------------------------------

STATUS_ISSUED = "ISSUED"
STATUS_VET_VERIFIED = "VET_VERIFIED"
STATUS_DISPENSED = "DISPENSED"

#: Mirrors the CHECK constraint on prescription.status in migration 0036.
PRESCRIPTION_STATUSES = frozenset(
    {STATUS_ISSUED, STATUS_VET_VERIFIED, STATUS_DISPENSED}
)

#: The ONLY moves the record may make. Stated positively and exhaustively: a
#: denylist would have to be re-checked every time a state was added, and the
#: state that was forgotten would be the one that became reachable.
#:
#: DISPENSED has no outgoing edge. That is what makes a second dispense
#: unrepresentable rather than merely unlikely — and it is asserted directly,
#: because "fails closed on re-dispense" is a governed claim, not a side effect.
ALLOWED_TRANSITIONS: dict[str, frozenset[str]] = {
    STATUS_ISSUED: frozenset({STATUS_VET_VERIFIED}),
    STATUS_VET_VERIFIED: frozenset({STATUS_DISPENSED}),
    STATUS_DISPENSED: frozenset(),
}


class PrescriptionNotFound(Exception):
    """No such prescription in the caller's scope.

    Deliberately not distinguished from "exists in another tenant" by the
    serving layer: telling a caller that a record they may not read exists is
    itself a cross-tenant disclosure.
    """


class TransitionDenied(Exception):
    """The record may not move this way from where it is."""


def assert_transition_allowed(*, from_status: str, to_status: str) -> None:
    if from_status not in ALLOWED_TRANSITIONS:
        raise TransitionDenied(f"{from_status!r} is not a known prescription status")
    if to_status not in ALLOWED_TRANSITIONS[from_status]:
        raise TransitionDenied(
            f"a prescription in {from_status!r} may not move to {to_status!r}"
        )


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


# ---------------------------------------------------------------------------
# The record
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Prescription:
    prescription_id: str
    tenant_id: str
    pet_id: str
    session_id: str
    issuing_vet_id: str
    medication_name: str
    dosage: str
    instructions: str
    status: str
    issued_at: datetime
    clinic_id: Optional[str] = None
    verified_at: Optional[datetime] = None
    verified_by_vet_id: Optional[str] = None
    dispensed_at: Optional[datetime] = None
    dispensed_by_actor_id: Optional[str] = None

    def to_read_model(self) -> dict:
        """The wire shape. Timestamps as ISO-8601 Z, never as a datetime repr."""
        def _iso(value: Optional[datetime]) -> Optional[str]:
            if value is None:
                return None
            return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")

        return {
            "prescription_id": self.prescription_id,
            "tenant_id": self.tenant_id,
            "pet_id": self.pet_id,
            "session_id": self.session_id,
            "clinic_id": self.clinic_id,
            "issuing_vet_id": self.issuing_vet_id,
            "medication_name": self.medication_name,
            "dosage": self.dosage,
            "instructions": self.instructions,
            "status": self.status,
            "issued_at": _iso(self.issued_at),
            "verified_at": _iso(self.verified_at),
            "verified_by_vet_id": self.verified_by_vet_id,
            "dispensed_at": _iso(self.dispensed_at),
            "dispensed_by_actor_id": self.dispensed_by_actor_id,
        }


@dataclass(frozen=True)
class StatusTransition:
    transition_id: str
    prescription_id: str
    from_status: Optional[str]
    to_status: str
    actor_id: str
    actor_role: str
    tenant_id: str
    occurred_at: datetime


@dataclass(frozen=True)
class PrescriptionDocument:
    document_id: str
    prescription_id: str
    tenant_id: str
    uploaded_by_actor_id: str
    filename: str
    content_type: str
    byte_size: int
    content_sha256: str
    storage_key: str
    uploaded_at: datetime

    def to_read_model(self) -> dict:
        return {
            "document_id": self.document_id,
            "prescription_id": self.prescription_id,
            "filename": self.filename,
            "content_type": self.content_type,
            "byte_size": self.byte_size,
            "content_sha256": self.content_sha256,
            "uploaded_at": self.uploaded_at.astimezone(timezone.utc)
            .isoformat()
            .replace("+00:00", "Z"),
        }
        # storage_key is deliberately absent: it is where the bytes live, and a
        # client that knows it has been handed the only thing the storage
        # adapter treats as authority to fetch them.


class PrescriptionRepository(Protocol):
    """What the serving path needs. No SQL crosses this boundary."""

    def create(self, rx: Prescription, *, actor_id: str, actor_role: str) -> Prescription: ...
    def get(self, prescription_id: str, *, tenant_id: str) -> Optional[Prescription]: ...
    def transition(
        self,
        prescription_id: str,
        *,
        tenant_id: str,
        to_status: str,
        actor_id: str,
        actor_role: str,
        at: Optional[datetime] = None,
    ) -> Prescription: ...
    def list_by_status(self, *, tenant_id: str, status: str) -> list[Prescription]: ...
    def transitions_for(self, prescription_id: str, *, tenant_id: str) -> list[StatusTransition]: ...
    def attach_document(self, doc: PrescriptionDocument) -> PrescriptionDocument: ...
    def documents_for(self, prescription_id: str, *, tenant_id: str) -> list[PrescriptionDocument]: ...
    def get_document(self, document_id: str, *, tenant_id: str) -> Optional[PrescriptionDocument]: ...


# ---------------------------------------------------------------------------
# In-memory
# ---------------------------------------------------------------------------


class InMemoryPrescriptionRepository:
    """The memory-mode store. Performs the same refusals the schema does.

    Every refusal below has a matching CHECK or FOREIGN KEY in migration 0036.
    A memory mode that refused less would mean the suite proves the weaker of
    the two implementations, and the controls would first fail in production
    against the one nobody had run — the argument `repositories.py` makes, and
    the defect shape it was written to prevent.
    """

    def __init__(self, tenants: TenantRepository) -> None:
        # REQUIRED, with no default. `tenants=None` would be a tenant-bearing
        # parameter a caller may omit, and the omission would silently disable
        # the existence check below — a repository that accepts any scope, built
        # by code that looks correct. tests/governance/test_tenant_scope_signatures
        # refuses the signature outright, which is how this was caught.
        self._rx: dict[str, Prescription] = {}
        self._transitions: list[StatusTransition] = []
        self._documents: dict[str, PrescriptionDocument] = {}
        self._tenants = tenants
        self._seq = 0

    # -- helpers ---------------------------------------------------------
    def _next_id(self, prefix: str) -> str:
        self._seq += 1
        return f"{prefix}-{self._seq:08d}"

    def _require_tenant_exists(self, tenant_id: str) -> None:
        """The in-memory stand-in for the tenant foreign key.

        Without it, memory mode accepts a scope PostgreSQL would refuse, and a
        typo'd tenant produces a new, empty, perfectly functional scope that
        nothing reports — the exact PRE-1 finding, reintroduced one layer up.
        """
        if not tenant_id or not tenant_id.strip():
            raise RepositoryDenied("a prescription cannot carry a blank tenant")
        if self._tenants.get(tenant_id) is None:
            raise RepositoryDenied(
                f"tenant {tenant_id!r} is not in the registry; a prescription "
                "cannot be written into a scope that does not exist"
            )

    # -- writes ----------------------------------------------------------
    def create(self, rx: Prescription, *, actor_id: str, actor_role: str) -> Prescription:
        if rx.status != STATUS_ISSUED:
            raise RepositoryDenied(
                f"a prescription is created in {STATUS_ISSUED}, not {rx.status!r}"
            )
        if rx.prescription_id in self._rx:
            raise RepositoryDenied(
                f"prescription {rx.prescription_id!r} already exists"
            )
        self._require_tenant_exists(rx.tenant_id)
        for field in ("pet_id", "session_id", "issuing_vet_id",
                      "medication_name", "dosage", "instructions"):
            if not (getattr(rx, field) or "").strip():
                raise RepositoryDenied(f"{field} may not be blank")
        self._rx[rx.prescription_id] = rx
        self._transitions.append(
            StatusTransition(
                transition_id=self._next_id("tr"),
                prescription_id=rx.prescription_id,
                from_status=None,
                to_status=STATUS_ISSUED,
                actor_id=actor_id,
                actor_role=actor_role,
                tenant_id=rx.tenant_id,
                occurred_at=rx.issued_at,
            )
        )
        return rx

    def transition(
        self,
        prescription_id: str,
        *,
        tenant_id: str,
        to_status: str,
        actor_id: str,
        actor_role: str,
        at: Optional[datetime] = None,
    ) -> Prescription:
        rx = self.get(prescription_id, tenant_id=tenant_id)
        if rx is None:
            raise PrescriptionNotFound(prescription_id)
        assert_transition_allowed(from_status=rx.status, to_status=to_status)
        now = at or _utc_now()
        if to_status == STATUS_VET_VERIFIED:
            moved = replace(rx, status=to_status, verified_at=now,
                            verified_by_vet_id=actor_id)
        elif to_status == STATUS_DISPENSED:
            moved = replace(rx, status=to_status, dispensed_at=now,
                            dispensed_by_actor_id=actor_id)
        else:  # pragma: no cover - unreachable while ISSUED has no inbound edge
            raise TransitionDenied(f"unsupported target status {to_status!r}")
        self._rx[prescription_id] = moved
        self._transitions.append(
            StatusTransition(
                transition_id=self._next_id("tr"),
                prescription_id=prescription_id,
                from_status=rx.status,
                to_status=to_status,
                actor_id=actor_id,
                actor_role=actor_role,
                tenant_id=rx.tenant_id,
                occurred_at=now,
            )
        )
        return moved

    def attach_document(self, doc: PrescriptionDocument) -> PrescriptionDocument:
        rx = self.get(doc.prescription_id, tenant_id=doc.tenant_id)
        if rx is None:
            raise PrescriptionNotFound(doc.prescription_id)
        if doc.byte_size <= 0:
            raise RepositoryDenied("a stored document may not be empty")
        if len(doc.content_sha256) != 64:
            raise RepositoryDenied("content_sha256 must be a hex sha-256 digest")
        for existing in self._documents.values():
            if existing.storage_key == doc.storage_key:
                raise RepositoryDenied(
                    "storage_key is already in use; two documents must never "
                    "share one object"
                )
        self._documents[doc.document_id] = doc
        return doc

    # -- reads -----------------------------------------------------------
    def get(self, prescription_id: str, *, tenant_id: str) -> Optional[Prescription]:
        rx = self._rx.get(prescription_id)
        # The tenant predicate is applied HERE rather than by callers. A read
        # helper that returned the row and left scoping to each call site is one
        # forgotten `if` away from a cross-tenant disclosure, and the forgotten
        # one is invisible at the call that looks correct.
        if rx is None or rx.tenant_id != tenant_id:
            return None
        return rx

    def list_by_status(self, *, tenant_id: str, status: str) -> list[Prescription]:
        return sorted(
            (r for r in self._rx.values()
             if r.tenant_id == tenant_id and r.status == status),
            key=lambda r: r.issued_at,
        )

    def transitions_for(self, prescription_id: str, *, tenant_id: str) -> list[StatusTransition]:
        if self.get(prescription_id, tenant_id=tenant_id) is None:
            return []
        return [t for t in self._transitions if t.prescription_id == prescription_id]

    def documents_for(self, prescription_id: str, *, tenant_id: str) -> list[PrescriptionDocument]:
        if self.get(prescription_id, tenant_id=tenant_id) is None:
            return []
        return sorted(
            (d for d in self._documents.values()
             if d.prescription_id == prescription_id),
            key=lambda d: d.uploaded_at,
        )

    def get_document(self, document_id: str, *, tenant_id: str) -> Optional[PrescriptionDocument]:
        doc = self._documents.get(document_id)
        if doc is None or doc.tenant_id != tenant_id:
            return None
        return doc

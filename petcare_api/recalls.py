"""FR-19 — batch recall resolution and owner notification (MVC-BUILD-RUNNER-001 U13).

AC-FR-19-02: a recall of (product, batch) resolves to every affected dispense and owner THROUGH STORED
RELATIONSHIPS ONLY — SUPPLY movement --prescription_id--> prescription --pet_id--> pet profile
--owner_id--> owner — never through free text. A supply whose chain does not resolve (a GENERAL/OTC
sale with no prescription, a prescription naming a pet with no stored profile) is placed in the
INDETERMINATE partition, which is always present in the output; every output carries a completeness
statement (REQ-MVC-6.22). Every resolved owner is notified.
AC-FR-19-03/04 (EXTERNAL:SFDA_API): `normalise_sfda_recall` is the ingestion boundary; the SFDA
interface contract is not held.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Protocol

from repositories import RepositoryDenied

SOURCE_STAFF, SOURCE_SFDA = "STAFF", "SFDA"


@dataclass(frozen=True)
class Recall:
    recall_id: str
    tenant_id: str
    product_id: str
    batch: str
    reason: str
    source: str
    initiated_by_actor_id: str
    created_at: datetime


@dataclass(frozen=True)
class RecallNotification:
    notification_id: str
    recall_id: str
    tenant_id: str
    owner_id: str
    movement_id: str
    rendered_body: str
    created_at: datetime


def normalise_sfda_recall(raw: dict) -> tuple:
    """(product_id, batch, reason) from an SFDA recall payload, or RepositoryDenied."""
    if not isinstance(raw, dict):
        raise RepositoryDenied("a recall is an object")
    product, batch = str(raw.get("product_id") or "").strip(), str(raw.get("batch") or "").strip()
    if not product or not batch:
        raise RepositoryDenied("a recall names the product and the batch")
    return product, batch, str(raw.get("reason") or "SFDA recall").strip()


def resolve(recall: Recall, supplies: list, prescription_of, pet_of) -> dict:
    """Partition the SUPPLY movements of the recalled (product, batch) into resolved and indeterminate.

    `prescription_of(prescription_id)` and `pet_of(pet_id)` read STORED records of the recall's tenant
    and return None when there is none. No other source is consulted.
    """
    resolved, indeterminate = [], []
    for m in supplies:
        if m.prescription_id is None:
            indeterminate.append({"movement_id": m.movement_id, "reason": "SUPPLY_WITHOUT_PRESCRIPTION"})
            continue
        rx = prescription_of(m.prescription_id)
        if rx is None:
            indeterminate.append({"movement_id": m.movement_id, "reason": "PRESCRIPTION_NOT_STORED"})
            continue
        pet = pet_of(rx.pet_id)
        if pet is None:
            indeterminate.append({"movement_id": m.movement_id, "reason": "PET_NOT_STORED",
                                  "prescription_id": rx.prescription_id})
            continue
        resolved.append({"movement_id": m.movement_id, "prescription_id": rx.prescription_id, "pet_id": pet.pet_id,
                         "owner_id": pet.owner_id, "quantity": -m.quantity_delta})
    n = len(supplies)
    return {"recall_id": recall.recall_id, "product_id": recall.product_id, "batch": recall.batch,
            "resolved": resolved, "indeterminate": indeterminate,
            "completeness": {"supplies_of_batch": n, "resolved": len(resolved), "indeterminate": len(indeterminate),
                             "complete": len(indeterminate) == 0,
                             "statement": (f"{n} supply movement(s) of {recall.product_id} batch {recall.batch} in this "
                                           f"tenant: {len(resolved)} resolved to an owner through stored records, "
                                           f"{len(indeterminate)} indeterminate (listed; not guessed).")}}


class RecallRepository(Protocol):
    def create(self, r: Recall, notifications: list) -> Recall: ...
    def get(self, recall_id: str, *, tenant_id: str): ...
    def notifications(self, recall_id: str, *, tenant_id: str) -> list: ...
    def notices_for_owner(self, owner_id: str, *, tenant_id: str) -> list: ...


@dataclass
class InMemoryRecallRepository:
    tenants: object
    _recalls: dict = field(default_factory=dict)
    _notifications: list = field(default_factory=list)

    def create(self, r, notifications):
        if self.tenants.get(r.tenant_id) is None:
            raise RepositoryDenied(f"tenant {r.tenant_id!r} is not registered")
        self._recalls[r.recall_id] = r
        self._notifications.extend(notifications)
        return r

    def get(self, recall_id, *, tenant_id):
        r = self._recalls.get(recall_id)
        return r if r is not None and r.tenant_id == tenant_id else None

    def notifications(self, recall_id, *, tenant_id):
        return [n for n in self._notifications if n.recall_id == recall_id and n.tenant_id == tenant_id]

    def notices_for_owner(self, owner_id, *, tenant_id):
        return [n for n in self._notifications if n.owner_id == owner_id and n.tenant_id == tenant_id]

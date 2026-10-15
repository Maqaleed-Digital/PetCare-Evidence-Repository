"""J-O7 — owner-uploaded external prescriptions awaiting veterinary verification (MVC-EPC-D-001 D2g; FR-14 owner part).

An owner uploads a prescription written elsewhere (a photo or PDF) for one of their own pets; it waits, AWAITING_VERIFICATION,
for a veterinarian of the clinic (J-V6, D3, decides it). The owner, tenant and actor are written from the session by
petcare_api/main.py — the request only selects the pet and carries the file. The record is separate from the governed
FR-14 prescription state machine (prescriptions.py), which only a veterinarian creates.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Protocol

from repositories import RepositoryDenied

AWAITING_VERIFICATION = "AWAITING_VERIFICATION"
STATUSES = (AWAITING_VERIFICATION,)
MAX_NOTE = 500


@dataclass(frozen=True)
class OwnerPrescriptionUpload:
    upload_id: str
    tenant_id: str
    owner_id: str
    pet_id: str
    filename: str
    content_type: str
    byte_size: int
    content_sha256: str
    storage_key: str
    note: str
    status: str
    uploaded_at: datetime

    def to_read_model(self) -> dict:
        d = asdict(self)
        d.pop("storage_key")
        d["uploaded_at"] = self.uploaded_at.isoformat()
        return d


def validate_upload_record(u: OwnerPrescriptionUpload) -> None:
    if u.status not in STATUSES:
        raise RepositoryDenied(f"unknown status {u.status!r}")
    if len(u.note) > MAX_NOTE:
        raise RepositoryDenied(f"a note is at most {MAX_NOTE} characters")
    if not (u.owner_id and u.pet_id and u.tenant_id and u.storage_key):
        raise RepositoryDenied("an upload names its owner, pet, tenant and stored object")


class OwnerPrescriptionUploadRepository(Protocol):
    def create(self, u: OwnerPrescriptionUpload) -> OwnerPrescriptionUpload: ...
    def get(self, upload_id: str, *, tenant_id: str): ...
    def list_for_owner(self, owner_id: str, *, tenant_id: str) -> list: ...
    def list_awaiting(self, *, tenant_id: str) -> list: ...


@dataclass
class InMemoryOwnerPrescriptionUploadRepository:
    _rows: dict = field(default_factory=dict)

    def create(self, u):
        validate_upload_record(u)
        self._rows[u.upload_id] = u
        return u

    def get(self, upload_id, *, tenant_id):
        u = self._rows.get(upload_id)
        return u if u is not None and u.tenant_id == tenant_id else None

    def list_for_owner(self, owner_id, *, tenant_id):
        return sorted((u for u in self._rows.values() if u.owner_id == owner_id and u.tenant_id == tenant_id),
                      key=lambda u: (u.uploaded_at, u.upload_id))

    def list_awaiting(self, *, tenant_id):
        return sorted((u for u in self._rows.values() if u.tenant_id == tenant_id and u.status == AWAITING_VERIFICATION),
                      key=lambda u: (u.uploaded_at, u.upload_id))

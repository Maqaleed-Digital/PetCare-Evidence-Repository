"""FR-02 — durable, tenant-scoped pet profiles (MVC-BUILD-RUNNER-001 U2).

Ratified criteria (MVC-ACCEPT-PACK-P1):

  AC-FR-02-01  a profile carries the BRD fields (name, species, breed, birth date,
               weight, medical conditions, allergies; BRD P373-P374), is persisted
               durably and scoped to the owner's tenant.
  AC-FR-02-02  the profile shows the pet's medical history (records, prescriptions,
               lab results) and stores owner preferences.
  AC-FR-02-03  animal identification (e.g. microchip) is a structured field with
               identifier type, value and capture date — never free text, and never
               made mandatory on an unsourced obligation (REQ-MVC-6.10).

The pet profile previously lived in the UPHR file store (`uphr_service`), a
node-local JSON file: a profile created through the served app did not survive a
second container. It now reaches the same repository boundary identity,
sessions, audit and prescriptions reach, selected by PETCARE_PERSISTENCE_MODE.
Every read and write takes the tenant as an argument and applies it itself, so
a caller cannot forget the tenant predicate at one call site.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import date, datetime
from typing import Optional, Protocol

from repositories import RepositoryDenied

#: Identification types. Structured, closed, and deliberately small: an
#: identifier outside the set is recorded as OTHER with its scheme named, never
#: as free text on the profile (AC-FR-02-03).
ID_MICROCHIP = "MICROCHIP"
ID_TATTOO = "TATTOO"
ID_OTHER = "OTHER"
IDENTIFICATION_TYPES = frozenset({ID_MICROCHIP, ID_TATTOO, ID_OTHER})

#: Medical-history record types held on the profile. Prescriptions are NOT
#: copied here: they are read from the prescription store, the single source
#: of truth for them (AC-FR-02-02).
RECORD_LAB_RESULT = "LAB_RESULT"
RECORD_CLINICAL = "CLINICAL_RECORD"
MEDICAL_RECORD_TYPES = frozenset({RECORD_LAB_RESULT, RECORD_CLINICAL})

#: Profile fields an update may change. Identity, tenant and ownership are not
#: among them.
MUTABLE_FIELDS = ("name", "species", "breed", "birth_date", "weight_kg",
                  "medical_conditions", "allergies", "preferences")


@dataclass
class PetProfile:
    pet_id: str
    tenant_id: str
    owner_id: str
    name: str
    species: str
    created_by_actor_id: str
    created_at: datetime
    updated_at: datetime
    breed: Optional[str] = None
    birth_date: Optional[date] = None
    weight_kg: Optional[float] = None
    medical_conditions: Optional[str] = None
    allergies: Optional[str] = None
    preferences: Optional[str] = None

    def to_read_model(self) -> dict:
        d = asdict(self)
        d["birth_date"] = self.birth_date.isoformat() if self.birth_date else None
        d["created_at"] = self.created_at.isoformat()
        d["updated_at"] = self.updated_at.isoformat()
        return d


@dataclass
class PetIdentification:
    identification_id: str
    pet_id: str
    tenant_id: str
    id_type: str
    id_value: str
    captured_at: date
    capture_method: str
    recorded_by_actor_id: str
    recorded_at: datetime
    issuing_scheme: Optional[str] = None

    def to_read_model(self) -> dict:
        d = asdict(self)
        d["captured_at"] = self.captured_at.isoformat()
        d["recorded_at"] = self.recorded_at.isoformat()
        return d


@dataclass
class PetMedicalRecord:
    record_id: str
    pet_id: str
    tenant_id: str
    record_type: str
    title: str
    recorded_by_actor_id: str
    recorded_at: datetime
    detail: Optional[str] = None

    def to_read_model(self) -> dict:
        d = asdict(self)
        d["recorded_at"] = self.recorded_at.isoformat()
        return d


def validate_identification(ident: PetIdentification) -> None:
    if ident.id_type not in IDENTIFICATION_TYPES:
        raise RepositoryDenied(f"identification type {ident.id_type!r} is not one of "
                               f"{sorted(IDENTIFICATION_TYPES)}")
    if not ident.id_value.strip():
        raise RepositoryDenied("identification value is required")
    if ident.id_type == ID_OTHER and not (ident.issuing_scheme or "").strip():
        raise RepositoryDenied("an OTHER identification must name its issuing scheme")


def validate_medical_record(rec: PetMedicalRecord) -> None:
    if rec.record_type not in MEDICAL_RECORD_TYPES:
        raise RepositoryDenied(f"record type {rec.record_type!r} is not one of "
                               f"{sorted(MEDICAL_RECORD_TYPES)}")
    if not rec.title.strip():
        raise RepositoryDenied("a medical record needs a title")


class PetProfileRepository(Protocol):
    def create(self, pet: PetProfile) -> PetProfile: ...
    def get(self, pet_id: str, *, tenant_id: str) -> Optional[PetProfile]: ...
    def list_for_tenant(self, *, tenant_id: str, owner_id: Optional[str] = None) -> list[PetProfile]: ...
    def update(self, pet_id: str, *, tenant_id: str, changes: dict, updated_at: datetime) -> PetProfile: ...
    def add_identification(self, ident: PetIdentification) -> PetIdentification: ...
    def identifications_for(self, pet_id: str, *, tenant_id: str) -> list[PetIdentification]: ...
    def add_medical_record(self, rec: PetMedicalRecord) -> PetMedicalRecord: ...
    def medical_records_for(self, pet_id: str, *, tenant_id: str) -> list[PetMedicalRecord]: ...


@dataclass
class InMemoryPetProfileRepository:
    """Non-production store. Refuses an unregistered tenant exactly as the
    PostgreSQL foreign key does, so the suite proves the stronger behaviour."""

    tenants: object
    _pets: dict = field(default_factory=dict)
    _idents: list = field(default_factory=list)
    _records: list = field(default_factory=list)

    def _require_tenant(self, tenant_id: str) -> None:
        if self.tenants.get(tenant_id) is None:
            raise RepositoryDenied(f"tenant {tenant_id!r} is not registered")

    def _require_pet(self, pet_id: str, tenant_id: str) -> None:
        if self.get(pet_id, tenant_id=tenant_id) is None:
            raise RepositoryDenied(f"pet {pet_id!r} is not in tenant {tenant_id!r}")

    def create(self, pet: PetProfile) -> PetProfile:
        self._require_tenant(pet.tenant_id)
        if pet.pet_id in self._pets:
            raise RepositoryDenied(f"pet {pet.pet_id!r} already exists")
        self._pets[pet.pet_id] = pet
        return pet

    def get(self, pet_id: str, *, tenant_id: str) -> Optional[PetProfile]:
        pet = self._pets.get(pet_id)
        return pet if pet is not None and pet.tenant_id == tenant_id else None

    def list_for_tenant(self, *, tenant_id: str, owner_id: Optional[str] = None) -> list[PetProfile]:
        return sorted((p for p in self._pets.values()
                       if p.tenant_id == tenant_id and (owner_id is None or p.owner_id == owner_id)),
                      key=lambda p: (p.created_at, p.pet_id))

    def update(self, pet_id: str, *, tenant_id: str, changes: dict, updated_at: datetime) -> PetProfile:
        pet = self.get(pet_id, tenant_id=tenant_id)
        if pet is None:
            raise RepositoryDenied(f"pet {pet_id!r} is not in tenant {tenant_id!r}")
        for k, v in changes.items():
            if k not in MUTABLE_FIELDS:
                raise RepositoryDenied(f"field {k!r} is not mutable")
            setattr(pet, k, v)
        pet.updated_at = updated_at
        return pet

    def add_identification(self, ident: PetIdentification) -> PetIdentification:
        validate_identification(ident)
        self._require_pet(ident.pet_id, ident.tenant_id)
        self._idents.append(ident)
        return ident

    def identifications_for(self, pet_id: str, *, tenant_id: str) -> list[PetIdentification]:
        return [i for i in self._idents if i.pet_id == pet_id and i.tenant_id == tenant_id]

    def add_medical_record(self, rec: PetMedicalRecord) -> PetMedicalRecord:
        validate_medical_record(rec)
        self._require_pet(rec.pet_id, rec.tenant_id)
        self._records.append(rec)
        return rec

    def medical_records_for(self, pet_id: str, *, tenant_id: str) -> list[PetMedicalRecord]:
        return sorted((r for r in self._records if r.pet_id == pet_id and r.tenant_id == tenant_id),
                      key=lambda r: (r.recorded_at, r.record_id))

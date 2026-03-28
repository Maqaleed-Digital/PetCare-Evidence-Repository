from __future__ import annotations

from datetime import datetime, timezone
from typing import Dict, List
from uuid import uuid4

from petcare.uphr.models import AllergyRecord, MedicationRecord, Pet


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class UPHRService:
    def __init__(self) -> None:
        self.pets: Dict[str, Pet] = {}
        self.allergies: Dict[str, List[AllergyRecord]] = {}
        self.medications: Dict[str, List[MedicationRecord]] = {}

    def create_pet(self, tenant_id: str, owner_id: str, name: str, species: str) -> Pet:
        now = utc_now_iso()
        pet = Pet(
            pet_id=str(uuid4()),
            tenant_id=tenant_id,
            owner_id=owner_id,
            clinic_id_nullable=None,
            name=name,
            species=species,
            breed_nullable=None,
            sex_nullable=None,
            birth_date_nullable=None,
            weight_latest_nullable=None,
            status="active",
            created_at=now,
            updated_at=now,
        )
        self.pets[pet.pet_id] = pet
        return pet

    def create_allergy_record(self, pet_id: str, allergen: str, severity: str, actor_id: str) -> AllergyRecord:
        now = utc_now_iso()
        record = AllergyRecord(
            allergy_record_id=str(uuid4()),
            pet_id=pet_id,
            allergen=allergen,
            severity=severity,
            reaction_nullable=None,
            status="active",
            recorded_by_actor_id=actor_id,
            recorded_at=now,
            updated_at=now,
            version_no=1,
        )
        self.allergies.setdefault(pet_id, []).append(record)
        return record

    def create_medication_record(self, pet_id: str, medication_name: str, actor_id: str) -> MedicationRecord:
        now = utc_now_iso()
        record = MedicationRecord(
            medication_record_id=str(uuid4()),
            pet_id=pet_id,
            medication_name=medication_name,
            medication_type_nullable=None,
            dose_nullable=None,
            dose_unit_nullable=None,
            route_nullable=None,
            frequency_nullable=None,
            start_date_nullable=None,
            end_date_nullable=None,
            status="active",
            prescribed_by_actor_id_nullable=actor_id,
            recorded_at=now,
            updated_at=now,
            version_no=1,
        )
        self.medications.setdefault(pet_id, []).append(record)
        return record

    def get_pet(self, pet_id: str) -> Pet:
        return self.pets[pet_id]

    def get_timeline(self, pet_id: str) -> dict:
        return {
            "pet_id": pet_id,
            "allergies": self.allergies.get(pet_id, []),
            "medications": self.medications.get(pet_id, []),
        }

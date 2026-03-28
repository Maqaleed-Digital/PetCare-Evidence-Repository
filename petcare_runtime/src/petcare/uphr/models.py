from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class Pet:
    pet_id: str
    tenant_id: str
    owner_id: str
    clinic_id_nullable: Optional[str]
    name: str
    species: str
    breed_nullable: Optional[str]
    sex_nullable: Optional[str]
    birth_date_nullable: Optional[str]
    weight_latest_nullable: Optional[float]
    status: str
    created_at: str
    updated_at: str


@dataclass
class AllergyRecord:
    allergy_record_id: str
    pet_id: str
    allergen: str
    severity: str
    reaction_nullable: Optional[str]
    status: str
    recorded_by_actor_id: str
    recorded_at: str
    updated_at: str
    version_no: int


@dataclass
class MedicationRecord:
    medication_record_id: str
    pet_id: str
    medication_name: str
    medication_type_nullable: Optional[str]
    dose_nullable: Optional[str]
    dose_unit_nullable: Optional[str]
    route_nullable: Optional[str]
    frequency_nullable: Optional[str]
    start_date_nullable: Optional[str]
    end_date_nullable: Optional[str]
    status: str
    prescribed_by_actor_id_nullable: Optional[str]
    recorded_at: str
    updated_at: str
    version_no: int

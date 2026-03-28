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


@dataclass
class VaccinationRecord:
    vaccination_record_id: str
    pet_id: str
    vaccine_name: str
    administered_at: str
    next_due_at_nullable: Optional[str]
    provider_name_nullable: Optional[str]
    batch_number_nullable: Optional[str]
    status: str
    recorded_at: str
    updated_at: str
    version_no: int


@dataclass
class LabResult:
    lab_result_id: str
    pet_id: str
    lab_name: str
    test_name: str
    result_value_nullable: Optional[str]
    result_unit_nullable: Optional[str]
    result_flag_nullable: Optional[str]
    collected_at_nullable: Optional[str]
    reported_at_nullable: Optional[str]
    attachment_document_id_nullable: Optional[str]
    recorded_at: str
    updated_at: str
    version_no: int


@dataclass
class ClinicalNote:
    clinical_note_id: str
    pet_id: str
    consultation_id_nullable: Optional[str]
    note_type: str
    content_structured_or_text: str
    author_actor_id: str
    signed_by_actor_id_nullable: Optional[str]
    signed_at_nullable: Optional[str]
    status: str
    created_at: str
    updated_at: str
    version_no: int


@dataclass
class UPHRDocument:
    uphr_document_id: str
    pet_id: str
    document_type: str
    object_storage_key: str
    mime_type: str
    size_bytes: int
    uploaded_by_actor_id: str
    visibility_scope: str
    checksum_sha256: str
    created_at: str

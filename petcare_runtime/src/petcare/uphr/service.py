from __future__ import annotations

from dataclasses import asdict
from datetime import datetime, timezone
from typing import Dict, List
from uuid import uuid4

from petcare.uphr.document_validation import validate_document_metadata
from petcare.uphr.models import (
    AllergyRecord,
    ClinicalNote,
    LabResult,
    MedicationRecord,
    Pet,
    UPHRDocument,
    VaccinationRecord,
)
from petcare.uphr.prompt_redaction import redact_prompt_safe_text
from petcare.uphr.repository import FileBackedRepository


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class UPHRService:
    def __init__(self, repository: FileBackedRepository | None = None) -> None:
        self.repository = repository or FileBackedRepository("petcare_runtime/data/uphr_store.json")
        self._cache = self.repository.load()

    def _save(self) -> None:
        self.repository.save(self._cache)

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
        self._cache["pets"][pet.pet_id] = asdict(pet)
        self._save()
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
        self._cache["allergies"].setdefault(pet_id, []).append(asdict(record))
        self._save()
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
        self._cache["medications"].setdefault(pet_id, []).append(asdict(record))
        self._save()
        return record

    def create_vaccination_record(self, pet_id: str, vaccine_name: str, administered_at: str) -> VaccinationRecord:
        now = utc_now_iso()
        record = VaccinationRecord(
            vaccination_record_id=str(uuid4()),
            pet_id=pet_id,
            vaccine_name=vaccine_name,
            administered_at=administered_at,
            next_due_at_nullable=None,
            provider_name_nullable=None,
            batch_number_nullable=None,
            status="recorded",
            recorded_at=now,
            updated_at=now,
            version_no=1,
        )
        self._cache["vaccinations"].setdefault(pet_id, []).append(asdict(record))
        self._save()
        return record

    def create_lab_result(self, pet_id: str, lab_name: str, test_name: str) -> LabResult:
        now = utc_now_iso()
        record = LabResult(
            lab_result_id=str(uuid4()),
            pet_id=pet_id,
            lab_name=lab_name,
            test_name=test_name,
            result_value_nullable=None,
            result_unit_nullable=None,
            result_flag_nullable=None,
            collected_at_nullable=None,
            reported_at_nullable=None,
            attachment_document_id_nullable=None,
            recorded_at=now,
            updated_at=now,
            version_no=1,
        )
        self._cache["labs"].setdefault(pet_id, []).append(asdict(record))
        self._save()
        return record

    def create_clinical_note(self, pet_id: str, note_type: str, content: str, actor_id: str) -> ClinicalNote:
        now = utc_now_iso()
        record = ClinicalNote(
            clinical_note_id=str(uuid4()),
            pet_id=pet_id,
            consultation_id_nullable=None,
            note_type=note_type,
            content_structured_or_text=content,
            author_actor_id=actor_id,
            signed_by_actor_id_nullable=None,
            signed_at_nullable=None,
            status="draft",
            created_at=now,
            updated_at=now,
            version_no=1,
        )
        self._cache["clinical_notes"].setdefault(pet_id, []).append(asdict(record))
        self._save()
        return record

    def create_document(
        self,
        pet_id: str,
        document_type: str,
        object_storage_key: str,
        mime_type: str,
        size_bytes: int,
        uploaded_by_actor_id: str,
        visibility_scope: str,
        checksum_sha256: str,
    ) -> UPHRDocument:
        validation = validate_document_metadata(
            mime_type=mime_type,
            size_bytes=size_bytes,
            checksum_sha256=checksum_sha256,
        )
        if not validation.valid:
            raise ValueError(validation.reason_code)

        now = utc_now_iso()
        record = UPHRDocument(
            uphr_document_id=str(uuid4()),
            pet_id=pet_id,
            document_type=document_type,
            object_storage_key=object_storage_key,
            mime_type=mime_type,
            size_bytes=size_bytes,
            uploaded_by_actor_id=uploaded_by_actor_id,
            visibility_scope=visibility_scope,
            checksum_sha256=checksum_sha256,
            created_at=now,
        )
        self._cache["documents"].setdefault(pet_id, []).append(asdict(record))
        self._save()
        return record

    def get_pet(self, pet_id: str) -> Pet:
        return Pet(**self._cache["pets"][pet_id])

    def get_timeline(
        self,
        pet_id: str,
        category: str | None = None,
        search_term: str | None = None,
    ) -> Dict[str, List[dict] | str]:
        timeline = {
            "pet_id": pet_id,
            "allergies": self._cache["allergies"].get(pet_id, []),
            "medications": self._cache["medications"].get(pet_id, []),
            "vaccinations": self._cache["vaccinations"].get(pet_id, []),
            "labs": self._cache["labs"].get(pet_id, []),
            "clinical_notes": self._cache["clinical_notes"].get(pet_id, []),
            "documents": self._cache["documents"].get(pet_id, []),
        }

        if category:
            filtered = {category: timeline.get(category, [])}
            filtered["pet_id"] = pet_id
            timeline = filtered

        if search_term:
            lowered = search_term.lower()
            for key, items in list(timeline.items()):
                if key == "pet_id":
                    continue
                timeline[key] = [
                    item for item in items
                    if lowered in str(item).lower()
                ]

        return timeline

    def build_prompt_safe_timeline_summary(self, pet_id: str) -> str:
        timeline = self.get_timeline(pet_id=pet_id)
        raw_text = str(timeline)
        redaction = redact_prompt_safe_text(raw_text)
        return redaction.redacted_text

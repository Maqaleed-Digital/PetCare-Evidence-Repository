from __future__ import annotations

import os
import uuid
from typing import Optional

from .models import EmergencyPartnerAvailabilityRecord, utc_now_iso
from .repository import FileEmergencyPartnerAvailabilityRepository


class EmergencyPartnerAvailabilityService:
    ALLOWED_OPEN_STATUS = {"open", "closed", "limited"}
    ALLOWED_CAPACITY_STATUS = {"available", "near_capacity", "full"}

    def __init__(self, repository: FileEmergencyPartnerAvailabilityRepository) -> None:
        self.repository = repository

    def _normalize_notes(self, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        normalized = value.strip()
        return normalized if normalized else None

    def upsert_partner_availability(
        self,
        *,
        tenant_id: str,
        partner_clinic_id: str,
        clinic_name: str,
        city: str,
        open_status: str,
        capacity_status: str,
        emergency_ready: bool,
        estimated_eta_minutes: int,
        failover_eligible: bool,
        on_call_vet_available: bool,
        accepts_walk_in_emergency: bool,
        operational_notes: Optional[str],
    ) -> EmergencyPartnerAvailabilityRecord:
        if open_status not in self.ALLOWED_OPEN_STATUS:
            raise ValueError("invalid_open_status")
        if capacity_status not in self.ALLOWED_CAPACITY_STATUS:
            raise ValueError("invalid_capacity_status")
        if estimated_eta_minutes < 0:
            raise ValueError("invalid_estimated_eta_minutes")

        existing = self.repository.find_by_partner_clinic_id(
            tenant_id=tenant_id,
            partner_clinic_id=partner_clinic_id,
        )

        record = EmergencyPartnerAvailabilityRecord(
            id=existing.id if existing is not None else str(uuid.uuid4()),
            tenant_id=tenant_id,
            partner_clinic_id=partner_clinic_id,
            clinic_name=clinic_name.strip(),
            city=city.strip(),
            open_status=open_status,
            capacity_status=capacity_status,
            emergency_ready=emergency_ready,
            estimated_eta_minutes=estimated_eta_minutes,
            failover_eligible=failover_eligible,
            on_call_vet_available=on_call_vet_available,
            accepts_walk_in_emergency=accepts_walk_in_emergency,
            operational_notes=self._normalize_notes(operational_notes),
            last_updated_at=utc_now_iso(),
            ai_execution_authority=False,
        )
        return self.repository.save(record)

    def get_partner_availability(self, record_id: str) -> Optional[EmergencyPartnerAvailabilityRecord]:
        return self.repository.get(record_id)

    def list_partner_availability(self, tenant_id: str) -> list[EmergencyPartnerAvailabilityRecord]:
        return self.repository.list_for_tenant(tenant_id)

    def list_emergency_ready_partners(self, tenant_id: str) -> list[EmergencyPartnerAvailabilityRecord]:
        records = self.repository.list_for_tenant(tenant_id)
        return [
            record
            for record in records
            if record.emergency_ready is True
            and record.open_status in {"open", "limited"}
            and record.capacity_status in {"available", "near_capacity"}
        ]


def build_default_emergency_partner_availability_service() -> EmergencyPartnerAvailabilityService:
    base_path = os.environ.get(
        "PETCARE_EMERGENCY_NETWORK_DIR",
        "petcare_runtime/runtime_data/emergency_network",
    )
    repository = FileEmergencyPartnerAvailabilityRepository(base_path)
    return EmergencyPartnerAvailabilityService(repository)

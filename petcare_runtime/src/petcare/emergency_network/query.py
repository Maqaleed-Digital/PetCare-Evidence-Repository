from __future__ import annotations

from dataclasses import asdict
from typing import Iterable, List, Optional

from .models import EmergencyPartnerAvailabilityRecord
from .repository import FileEmergencyPartnerAvailabilityRepository


class EmergencyPartnerAvailabilityQueryService:
    def __init__(self, repository: FileEmergencyPartnerAvailabilityRepository) -> None:
        self.repository = repository

    def _sorted_records(
        self,
        records: Iterable[EmergencyPartnerAvailabilityRecord],
    ) -> List[EmergencyPartnerAvailabilityRecord]:
        return sorted(
            list(records),
            key=lambda item: (
                item.estimated_eta_minutes,
                item.city.lower(),
                item.clinic_name.lower(),
                item.partner_clinic_id,
            ),
        )

    def list_all_for_tenant(
        self,
        tenant_id: str,
    ) -> List[EmergencyPartnerAvailabilityRecord]:
        return self._sorted_records(self.repository.list_for_tenant(tenant_id))

    def filter_partners(
        self,
        *,
        tenant_id: str,
        city: Optional[str] = None,
        open_status: Optional[str] = None,
        capacity_status: Optional[str] = None,
        emergency_ready: Optional[bool] = None,
        failover_eligible: Optional[bool] = None,
        on_call_vet_available: Optional[bool] = None,
        accepts_walk_in_emergency: Optional[bool] = None,
        max_eta_minutes: Optional[int] = None,
    ) -> List[EmergencyPartnerAvailabilityRecord]:
        records = self.repository.list_for_tenant(tenant_id)

        if city is not None:
            city_normalized = city.strip().lower()
            records = [item for item in records if item.city.strip().lower() == city_normalized]

        if open_status is not None:
            records = [item for item in records if item.open_status == open_status]

        if capacity_status is not None:
            records = [item for item in records if item.capacity_status == capacity_status]

        if emergency_ready is not None:
            records = [item for item in records if item.emergency_ready is emergency_ready]

        if failover_eligible is not None:
            records = [item for item in records if item.failover_eligible is failover_eligible]

        if on_call_vet_available is not None:
            records = [item for item in records if item.on_call_vet_available is on_call_vet_available]

        if accepts_walk_in_emergency is not None:
            records = [item for item in records if item.accepts_walk_in_emergency is accepts_walk_in_emergency]

        if max_eta_minutes is not None:
            records = [item for item in records if item.estimated_eta_minutes <= max_eta_minutes]

        return self._sorted_records(records)

    def list_failover_candidates(
        self,
        *,
        tenant_id: str,
        city: Optional[str] = None,
        max_eta_minutes: Optional[int] = None,
    ) -> List[EmergencyPartnerAvailabilityRecord]:
        return self.filter_partners(
            tenant_id=tenant_id,
            city=city,
            open_status=None,
            capacity_status=None,
            emergency_ready=True,
            failover_eligible=True,
            on_call_vet_available=True,
            accepts_walk_in_emergency=True,
            max_eta_minutes=max_eta_minutes,
        )

    def summarize_operational_readiness(
        self,
        tenant_id: str,
    ) -> dict:
        records = self.repository.list_for_tenant(tenant_id)
        return {
            "tenant_id": tenant_id,
            "total_partners": len(records),
            "open_count": sum(1 for item in records if item.open_status == "open"),
            "limited_count": sum(1 for item in records if item.open_status == "limited"),
            "closed_count": sum(1 for item in records if item.open_status == "closed"),
            "available_capacity_count": sum(1 for item in records if item.capacity_status == "available"),
            "near_capacity_count": sum(1 for item in records if item.capacity_status == "near_capacity"),
            "full_capacity_count": sum(1 for item in records if item.capacity_status == "full"),
            "emergency_ready_count": sum(1 for item in records if item.emergency_ready is True),
            "failover_eligible_count": sum(1 for item in records if item.failover_eligible is True),
            "walk_in_ready_count": sum(1 for item in records if item.accepts_walk_in_emergency is True),
        }

    def serialize_records(
        self,
        records: Iterable[EmergencyPartnerAvailabilityRecord],
    ) -> List[dict]:
        return [asdict(item) for item in records]

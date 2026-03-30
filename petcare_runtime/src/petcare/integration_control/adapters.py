from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class AdapterType(str, Enum):
    ERP = "erp"
    ACCOUNTING_EXPORT = "accounting_export"
    PAYMENT_GATEWAY = "payment_gateway"


class AdapterDirection(str, Enum):
    EXPORT_ONLY = "export_only"
    INGEST_ONLY = "ingest_only"
    BIDIRECTIONAL_PASSIVE = "bidirectional_passive"


@dataclass(frozen=True)
class AdapterContract:
    adapter_id: str
    adapter_type: AdapterType
    direction: AdapterDirection
    execution_mode: str
    contract_version: str

    def __post_init__(self) -> None:
        if not self.adapter_id:
            raise ValueError("adapter_id is required")
        if self.execution_mode not in {
            "passive_export_only",
            "passive_ingest_only",
            "passive_bidirectional",
        }:
            raise ValueError("execution_mode must be passive")
        if not self.contract_version:
            raise ValueError("contract_version is required")


@dataclass(frozen=True)
class ExternalReferenceMap:
    mapping_id: str
    internal_entity_id: str
    external_system: str
    external_reference_id: str
    created_at: str

    def __post_init__(self) -> None:
        if not self.mapping_id:
            raise ValueError("mapping_id is required")
        if not self.internal_entity_id:
            raise ValueError("internal_entity_id is required")
        if not self.external_system:
            raise ValueError("external_system is required")
        if not self.external_reference_id:
            raise ValueError("external_reference_id is required")
        if not self.created_at:
            raise ValueError("created_at is required")


def build_adapter_contract(
    adapter_id: str,
    adapter_type: AdapterType,
    direction: AdapterDirection,
    contract_version: str,
) -> AdapterContract:
    mode_map = {
        AdapterDirection.EXPORT_ONLY: "passive_export_only",
        AdapterDirection.INGEST_ONLY: "passive_ingest_only",
        AdapterDirection.BIDIRECTIONAL_PASSIVE: "passive_bidirectional",
    }
    return AdapterContract(
        adapter_id=adapter_id,
        adapter_type=adapter_type,
        direction=direction,
        execution_mode=mode_map[direction],
        contract_version=contract_version,
    )


def build_external_reference_map(
    mapping_id: str,
    internal_entity_id: str,
    external_system: str,
    external_reference_id: str,
    created_at: str,
) -> ExternalReferenceMap:
    return ExternalReferenceMap(
        mapping_id=mapping_id,
        internal_entity_id=internal_entity_id,
        external_system=external_system,
        external_reference_id=external_reference_id,
        created_at=created_at,
    )

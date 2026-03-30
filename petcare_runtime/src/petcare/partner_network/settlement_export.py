from dataclasses import dataclass, field
from typing import Dict, List, Optional


SETTLEMENT_EXPORT_STATUS_PREPARED = "PREPARED"
SETTLEMENT_EXPORT_STATUS_HANDOFF_READY = "HANDOFF_READY"

DECISION_CLASSIFICATION_NON_AUTONOMOUS = "NON_AUTONOMOUS_DECISION"


@dataclass(frozen=True)
class SettlementExportInput:
    export_package_id: str
    review_id: str
    prepared_by: str
    handoff_target: str
    notes: Optional[str] = None

    def validate(self) -> None:
        if not self.export_package_id.strip():
            raise ValueError("export_package_id is required")
        if not self.review_id.strip():
            raise ValueError("review_id is required")
        if not self.prepared_by.strip():
            raise ValueError("prepared_by is required")
        if not self.handoff_target.strip():
            raise ValueError("handoff_target is required")


@dataclass(frozen=True)
class SettlementExportManifest:
    manifest_id: str
    export_package_id: str
    review_id: str
    settlement_preparation_id: str
    order_id: str
    partner_id: str
    quoted_final_price: float
    currency: str
    manifest_version: str
    immutable_fields: Dict[str, object]
    human_approved: bool
    handoff_only: bool = True
    decision_classification: str = DECISION_CLASSIFICATION_NON_AUTONOMOUS
    ai_execution_authority: bool = False

    def validate(self) -> None:
        if not self.manifest_id.strip():
            raise ValueError("manifest_id is required")
        if not self.export_package_id.strip():
            raise ValueError("export_package_id is required")
        if not self.review_id.strip():
            raise ValueError("review_id is required")
        if not self.settlement_preparation_id.strip():
            raise ValueError("settlement_preparation_id is required")
        if not self.order_id.strip():
            raise ValueError("order_id is required")
        if not self.partner_id.strip():
            raise ValueError("partner_id is required")
        if self.quoted_final_price < 0:
            raise ValueError("quoted_final_price cannot be negative")
        if not self.manifest_version.strip():
            raise ValueError("manifest_version is required")
        if self.ai_execution_authority:
            raise ValueError("ai_execution_authority must remain false")
        if self.decision_classification != DECISION_CLASSIFICATION_NON_AUTONOMOUS:
            raise ValueError("decision_classification must remain NON_AUTONOMOUS_DECISION")
        if not self.human_approved:
            raise ValueError("human_approved must remain true for export manifest")
        if not self.handoff_only:
            raise ValueError("handoff_only must remain true")


@dataclass(frozen=True)
class SettlementExportPackage:
    export_package_id: str
    review_id: str
    settlement_preparation_id: str
    order_id: str
    partner_id: str
    status: str
    handoff_target: str
    export_delivery_executed: bool
    manifest: SettlementExportManifest
    audit_trace: Dict[str, object] = field(default_factory=dict)
    decision_classification: str = DECISION_CLASSIFICATION_NON_AUTONOMOUS
    ai_execution_authority: bool = False

    def validate(self) -> None:
        if not self.export_package_id.strip():
            raise ValueError("export_package_id is required")
        if not self.review_id.strip():
            raise ValueError("review_id is required")
        if not self.settlement_preparation_id.strip():
            raise ValueError("settlement_preparation_id is required")
        if not self.order_id.strip():
            raise ValueError("order_id is required")
        if not self.partner_id.strip():
            raise ValueError("partner_id is required")
        if self.status not in {SETTLEMENT_EXPORT_STATUS_PREPARED, SETTLEMENT_EXPORT_STATUS_HANDOFF_READY}:
            raise ValueError("invalid settlement export status")
        if not self.handoff_target.strip():
            raise ValueError("handoff_target is required")
        if self.export_delivery_executed:
            raise ValueError("export_delivery_executed must remain false in Wave-09")
        if self.ai_execution_authority:
            raise ValueError("ai_execution_authority must remain false")
        if self.decision_classification != DECISION_CLASSIFICATION_NON_AUTONOMOUS:
            raise ValueError("decision_classification must remain NON_AUTONOMOUS_DECISION")
        self.manifest.validate()


@dataclass(frozen=True)
class SettlementExportSummary:
    partner_id: str
    total_packages: int
    handoff_ready_count: int
    decision_classification: str
    ai_execution_authority: bool
    packages: List[SettlementExportPackage] = field(default_factory=list)

    def validate(self) -> None:
        if not self.partner_id.strip():
            raise ValueError("partner_id is required")
        if self.total_packages != len(self.packages):
            raise ValueError("total_packages must equal number of packages")
        if self.ai_execution_authority:
            raise ValueError("ai_execution_authority must remain false")
        if self.decision_classification != DECISION_CLASSIFICATION_NON_AUTONOMOUS:
            raise ValueError("decision_classification must remain NON_AUTONOMOUS_DECISION")

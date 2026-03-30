from dataclasses import dataclass, field
from typing import Dict, List, Optional


SETTLEMENT_PREPARATION_STATUS_DRAFT = "DRAFT"
SETTLEMENT_PREPARATION_STATUS_READY_FOR_REVIEW = "READY_FOR_REVIEW"
SETTLEMENT_PREPARATION_STATUS_BLOCKED = "BLOCKED"

EXPORT_STATUS_NOT_EXPORTED = "NOT_EXPORTED"

DECISION_CLASSIFICATION_NON_AUTONOMOUS = "NON_AUTONOMOUS_DECISION"


@dataclass(frozen=True)
class SettlementPreparationInput:
    settlement_preparation_id: str
    order_id: str
    prepared_by: str
    notes: Optional[str] = None

    def validate(self) -> None:
        if not self.settlement_preparation_id.strip():
            raise ValueError("settlement_preparation_id is required")
        if not self.order_id.strip():
            raise ValueError("order_id is required")
        if not self.prepared_by.strip():
            raise ValueError("prepared_by is required")


@dataclass(frozen=True)
class SettlementPreparationRecord:
    settlement_preparation_id: str
    order_id: str
    partner_id: str
    pricing_rule_id: str
    quoted_final_price: float
    currency: str
    execution_latest_event_type: Optional[str]
    status: str
    boundary_reason: str
    export_status: str
    human_review_required: bool
    decision_classification: str = DECISION_CLASSIFICATION_NON_AUTONOMOUS
    ai_execution_authority: bool = False
    audit_trace: Dict[str, object] = field(default_factory=dict)

    def validate(self) -> None:
        if not self.settlement_preparation_id.strip():
            raise ValueError("settlement_preparation_id is required")
        if not self.order_id.strip():
            raise ValueError("order_id is required")
        if not self.partner_id.strip():
            raise ValueError("partner_id is required")
        if not self.pricing_rule_id.strip():
            raise ValueError("pricing_rule_id is required")
        if self.quoted_final_price < 0:
            raise ValueError("quoted_final_price cannot be negative")
        if self.status not in {
            SETTLEMENT_PREPARATION_STATUS_DRAFT,
            SETTLEMENT_PREPARATION_STATUS_READY_FOR_REVIEW,
            SETTLEMENT_PREPARATION_STATUS_BLOCKED,
        }:
            raise ValueError("invalid settlement preparation status")
        if self.export_status != EXPORT_STATUS_NOT_EXPORTED:
            raise ValueError("export_status must remain NOT_EXPORTED in Wave-07")
        if self.ai_execution_authority:
            raise ValueError("ai_execution_authority must remain false")
        if self.decision_classification != DECISION_CLASSIFICATION_NON_AUTONOMOUS:
            raise ValueError("decision_classification must remain NON_AUTONOMOUS_DECISION")
        if not self.human_review_required:
            raise ValueError("human_review_required must remain true")


@dataclass(frozen=True)
class SettlementPreparationSummary:
    partner_id: str
    total_records: int
    ready_for_review_count: int
    blocked_count: int
    total_quoted_value: float
    currency: str
    decision_classification: str
    ai_execution_authority: bool
    records: List[SettlementPreparationRecord] = field(default_factory=list)

    def validate(self) -> None:
        if not self.partner_id.strip():
            raise ValueError("partner_id is required")
        if self.total_records != len(self.records):
            raise ValueError("total_records must equal number of records")
        if self.ai_execution_authority:
            raise ValueError("ai_execution_authority must remain false")
        if self.decision_classification != DECISION_CLASSIFICATION_NON_AUTONOMOUS:
            raise ValueError("decision_classification must remain NON_AUTONOMOUS_DECISION")

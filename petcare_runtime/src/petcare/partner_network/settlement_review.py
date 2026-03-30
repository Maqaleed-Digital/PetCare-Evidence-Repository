from dataclasses import dataclass, field
from typing import Dict, List, Optional


SETTLEMENT_REVIEW_STATUS_IN_QUEUE = "IN_QUEUE"
SETTLEMENT_REVIEW_STATUS_APPROVED = "APPROVED"
SETTLEMENT_REVIEW_STATUS_REJECTED = "REJECTED"

REVIEW_DECISION_APPROVE = "APPROVE"
REVIEW_DECISION_REJECT = "REJECT"

DECISION_CLASSIFICATION_NON_AUTONOMOUS = "NON_AUTONOMOUS_DECISION"


@dataclass(frozen=True)
class SettlementReviewQueueItem:
    review_id: str
    settlement_preparation_id: str
    order_id: str
    partner_id: str
    quoted_final_price: float
    currency: str
    status: str
    human_review_required: bool
    decision_classification: str = DECISION_CLASSIFICATION_NON_AUTONOMOUS
    ai_execution_authority: bool = False
    audit_events: List[str] = field(default_factory=list)

    def validate(self) -> None:
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
        if self.status not in {
            SETTLEMENT_REVIEW_STATUS_IN_QUEUE,
            SETTLEMENT_REVIEW_STATUS_APPROVED,
            SETTLEMENT_REVIEW_STATUS_REJECTED,
        }:
            raise ValueError("invalid settlement review status")
        if self.ai_execution_authority:
            raise ValueError("ai_execution_authority must remain false")
        if self.decision_classification != DECISION_CLASSIFICATION_NON_AUTONOMOUS:
            raise ValueError("decision_classification must remain NON_AUTONOMOUS_DECISION")
        if not self.human_review_required:
            raise ValueError("human_review_required must remain true")


@dataclass(frozen=True)
class SettlementReviewDecisionInput:
    review_id: str
    reviewer_id: str
    decision: str
    reason_code: str
    notes: Optional[str] = None

    def validate(self) -> None:
        if not self.review_id.strip():
            raise ValueError("review_id is required")
        if not self.reviewer_id.strip():
            raise ValueError("reviewer_id is required")
        if self.decision not in {REVIEW_DECISION_APPROVE, REVIEW_DECISION_REJECT}:
            raise ValueError("invalid review decision")
        if not self.reason_code.strip():
            raise ValueError("reason_code is required")


@dataclass(frozen=True)
class SettlementReviewDecisionRecord:
    decision_id: str
    review_id: str
    settlement_preparation_id: str
    reviewer_id: str
    decision: str
    reason_code: str
    notes: Optional[str]
    queue_status_after_decision: str
    immutable_audit: Dict[str, object]
    human_review_required: bool = True
    decision_classification: str = DECISION_CLASSIFICATION_NON_AUTONOMOUS
    ai_execution_authority: bool = False

    def validate(self) -> None:
        if not self.decision_id.strip():
            raise ValueError("decision_id is required")
        if not self.review_id.strip():
            raise ValueError("review_id is required")
        if not self.settlement_preparation_id.strip():
            raise ValueError("settlement_preparation_id is required")
        if not self.reviewer_id.strip():
            raise ValueError("reviewer_id is required")
        if self.decision not in {REVIEW_DECISION_APPROVE, REVIEW_DECISION_REJECT}:
            raise ValueError("invalid decision")
        if self.queue_status_after_decision not in {
            SETTLEMENT_REVIEW_STATUS_APPROVED,
            SETTLEMENT_REVIEW_STATUS_REJECTED,
        }:
            raise ValueError("invalid queue_status_after_decision")
        if self.ai_execution_authority:
            raise ValueError("ai_execution_authority must remain false")
        if self.decision_classification != DECISION_CLASSIFICATION_NON_AUTONOMOUS:
            raise ValueError("decision_classification must remain NON_AUTONOMOUS_DECISION")
        if not self.human_review_required:
            raise ValueError("human_review_required must remain true")


@dataclass(frozen=True)
class SettlementReviewQueueSummary:
    partner_id: str
    total_items: int
    in_queue_count: int
    approved_count: int
    rejected_count: int
    decision_classification: str
    ai_execution_authority: bool
    items: List[SettlementReviewQueueItem] = field(default_factory=list)

    def validate(self) -> None:
        if not self.partner_id.strip():
            raise ValueError("partner_id is required")
        if self.total_items != len(self.items):
            raise ValueError("total_items must equal number of items")
        if self.ai_execution_authority:
            raise ValueError("ai_execution_authority must remain false")
        if self.decision_classification != DECISION_CLASSIFICATION_NON_AUTONOMOUS:
            raise ValueError("decision_classification must remain NON_AUTONOMOUS_DECISION")

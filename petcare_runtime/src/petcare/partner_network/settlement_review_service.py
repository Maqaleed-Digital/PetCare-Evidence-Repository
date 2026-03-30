from .settlement_preparation import SETTLEMENT_PREPARATION_STATUS_READY_FOR_REVIEW
from .settlement_preparation_repository import SettlementPreparationRepository
from .settlement_review import (
    DECISION_CLASSIFICATION_NON_AUTONOMOUS,
    REVIEW_DECISION_APPROVE,
    REVIEW_DECISION_REJECT,
    SETTLEMENT_REVIEW_STATUS_APPROVED,
    SETTLEMENT_REVIEW_STATUS_IN_QUEUE,
    SETTLEMENT_REVIEW_STATUS_REJECTED,
    SettlementReviewDecisionInput,
    SettlementReviewDecisionRecord,
    SettlementReviewQueueItem,
    SettlementReviewQueueSummary,
)
from .settlement_review_repository import SettlementReviewRepository


class SettlementReviewService:
    def __init__(
        self,
        settlement_review_repository: SettlementReviewRepository,
        settlement_preparation_repository: SettlementPreparationRepository,
    ) -> None:
        self._settlement_review_repository = settlement_review_repository
        self._settlement_preparation_repository = settlement_preparation_repository

    def enqueue_review_item(self, review_id: str, settlement_preparation_id: str) -> SettlementReviewQueueItem:
        if not review_id.strip():
            raise ValueError("review_id is required")
        if not settlement_preparation_id.strip():
            raise ValueError("settlement_preparation_id is required")

        if self._settlement_review_repository.get_queue_item(review_id) is not None:
            raise ValueError("review_id already exists")

        if self._settlement_review_repository.get_queue_item_by_settlement_preparation_id(settlement_preparation_id) is not None:
            raise ValueError("settlement_preparation_id already has a review item")

        settlement_preparation = self._settlement_preparation_repository.get(settlement_preparation_id)
        if settlement_preparation is None:
            raise ValueError("settlement_preparation_id not found")

        if settlement_preparation.status != SETTLEMENT_PREPARATION_STATUS_READY_FOR_REVIEW:
            raise ValueError("settlement preparation must be READY_FOR_REVIEW before queueing")

        item = SettlementReviewQueueItem(
            review_id=review_id,
            settlement_preparation_id=settlement_preparation.settlement_preparation_id,
            order_id=settlement_preparation.order_id,
            partner_id=settlement_preparation.partner_id,
            quoted_final_price=settlement_preparation.quoted_final_price,
            currency=settlement_preparation.currency,
            status=SETTLEMENT_REVIEW_STATUS_IN_QUEUE,
            human_review_required=True,
            decision_classification=DECISION_CLASSIFICATION_NON_AUTONOMOUS,
            ai_execution_authority=False,
            audit_events=["settlement_review.queued"],
        )
        return self._settlement_review_repository.save_queue_item(item)

    def record_decision(self, decision_input: SettlementReviewDecisionInput) -> SettlementReviewDecisionRecord:
        decision_input.validate()

        queue_item = self._settlement_review_repository.get_queue_item(decision_input.review_id)
        if queue_item is None:
            raise ValueError("review_id not found")

        if queue_item.status != SETTLEMENT_REVIEW_STATUS_IN_QUEUE:
            raise ValueError("review item already decided")

        existing_decision = self._settlement_review_repository.get_decision_record_by_review_id(decision_input.review_id)
        if existing_decision is not None:
            raise ValueError("review decision already exists")

        if decision_input.decision == REVIEW_DECISION_APPROVE:
            status_after_decision = SETTLEMENT_REVIEW_STATUS_APPROVED
            audit_event = "settlement_review.approved"
        else:
            status_after_decision = SETTLEMENT_REVIEW_STATUS_REJECTED
            audit_event = "settlement_review.rejected"

        updated_queue_item = SettlementReviewQueueItem(
            review_id=queue_item.review_id,
            settlement_preparation_id=queue_item.settlement_preparation_id,
            order_id=queue_item.order_id,
            partner_id=queue_item.partner_id,
            quoted_final_price=queue_item.quoted_final_price,
            currency=queue_item.currency,
            status=status_after_decision,
            human_review_required=True,
            decision_classification=DECISION_CLASSIFICATION_NON_AUTONOMOUS,
            ai_execution_authority=False,
            audit_events=queue_item.audit_events + [audit_event],
        )
        self._settlement_review_repository.save_queue_item(updated_queue_item)

        decision_record = SettlementReviewDecisionRecord(
            decision_id=f"{decision_input.review_id}-decision-1",
            review_id=queue_item.review_id,
            settlement_preparation_id=queue_item.settlement_preparation_id,
            reviewer_id=decision_input.reviewer_id,
            decision=decision_input.decision,
            reason_code=decision_input.reason_code,
            notes=decision_input.notes,
            queue_status_after_decision=status_after_decision,
            immutable_audit={
                "human_reviewer_id": decision_input.reviewer_id,
                "decision": decision_input.decision,
                "reason_code": decision_input.reason_code,
                "notes": decision_input.notes,
                "financial_execution_enabled": False,
                "payment_execution_enabled": False,
                "settlement_execution_enabled": False,
            },
            human_review_required=True,
            decision_classification=DECISION_CLASSIFICATION_NON_AUTONOMOUS,
            ai_execution_authority=False,
        )
        return self._settlement_review_repository.save_decision_record(decision_record)

    def summarize_partner_queue(self, partner_id: str) -> SettlementReviewQueueSummary:
        items = self._settlement_review_repository.list_queue_items_for_partner(partner_id)
        if not items:
            raise ValueError("no settlement review items found for partner")

        in_queue_count = len([item for item in items if item.status == SETTLEMENT_REVIEW_STATUS_IN_QUEUE])
        approved_count = len([item for item in items if item.status == SETTLEMENT_REVIEW_STATUS_APPROVED])
        rejected_count = len([item for item in items if item.status == SETTLEMENT_REVIEW_STATUS_REJECTED])

        summary = SettlementReviewQueueSummary(
            partner_id=partner_id,
            total_items=len(items),
            in_queue_count=in_queue_count,
            approved_count=approved_count,
            rejected_count=rejected_count,
            decision_classification=DECISION_CLASSIFICATION_NON_AUTONOMOUS,
            ai_execution_authority=False,
            items=items,
        )
        summary.validate()
        return summary

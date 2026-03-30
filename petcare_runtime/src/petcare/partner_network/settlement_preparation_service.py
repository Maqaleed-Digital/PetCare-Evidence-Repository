from .execution_visibility import EXECUTION_EVENT_COMPLETED, EXECUTION_EVENT_FAILED
from .execution_visibility_repository import ExecutionVisibilityRepository
from .orders import ORDER_STATUS_ROUTED
from .orders_repository import OrdersRepository
from .settlement_preparation import (
    DECISION_CLASSIFICATION_NON_AUTONOMOUS,
    EXPORT_STATUS_NOT_EXPORTED,
    SETTLEMENT_PREPARATION_STATUS_BLOCKED,
    SETTLEMENT_PREPARATION_STATUS_READY_FOR_REVIEW,
    SettlementPreparationInput,
    SettlementPreparationRecord,
    SettlementPreparationSummary,
)
from .settlement_preparation_repository import SettlementPreparationRepository


class SettlementPreparationService:
    def __init__(
        self,
        settlement_preparation_repository: SettlementPreparationRepository,
        orders_repository: OrdersRepository,
        execution_visibility_repository: ExecutionVisibilityRepository,
    ) -> None:
        self._settlement_preparation_repository = settlement_preparation_repository
        self._orders_repository = orders_repository
        self._execution_visibility_repository = execution_visibility_repository

    def prepare_record(self, settlement_input: SettlementPreparationInput) -> SettlementPreparationRecord:
        settlement_input.validate()

        if self._settlement_preparation_repository.get(settlement_input.settlement_preparation_id) is not None:
            raise ValueError("settlement_preparation_id already exists")

        if self._settlement_preparation_repository.get_by_order_id(settlement_input.order_id) is not None:
            raise ValueError("order_id already has a settlement preparation record")

        order = self._orders_repository.get(settlement_input.order_id)
        if order is None:
            raise ValueError("order not found")

        if order.status != ORDER_STATUS_ROUTED:
            raise ValueError("order must be ROUTED before settlement preparation")

        execution_events = self._execution_visibility_repository.list_events_for_order(settlement_input.order_id)
        if not execution_events:
            raise ValueError("execution visibility events are required before settlement preparation")

        latest_event_type = execution_events[-1].event_type
        has_failed_event = any(event.event_type == EXECUTION_EVENT_FAILED for event in execution_events)

        if has_failed_event:
            status = SETTLEMENT_PREPARATION_STATUS_BLOCKED
            boundary_reason = "execution_failed_requires_manual_review"
        elif latest_event_type == EXECUTION_EVENT_COMPLETED:
            status = SETTLEMENT_PREPARATION_STATUS_READY_FOR_REVIEW
            boundary_reason = "completed_execution_ready_for_human_financial_review"
        else:
            status = SETTLEMENT_PREPARATION_STATUS_BLOCKED
            boundary_reason = "execution_not_completed_financial_boundary_closed"

        record = SettlementPreparationRecord(
            settlement_preparation_id=settlement_input.settlement_preparation_id,
            order_id=order.order_id,
            partner_id=order.partner_id,
            pricing_rule_id=order.pricing_rule_id,
            quoted_final_price=order.quoted_final_price,
            currency=order.currency,
            execution_latest_event_type=latest_event_type,
            status=status,
            boundary_reason=boundary_reason,
            export_status=EXPORT_STATUS_NOT_EXPORTED,
            human_review_required=True,
            decision_classification=DECISION_CLASSIFICATION_NON_AUTONOMOUS,
            ai_execution_authority=False,
            audit_trace={
                "prepared_by": settlement_input.prepared_by,
                "notes": settlement_input.notes,
                "order_status": order.status,
                "execution_latest_event_type": latest_event_type,
                "event_count": len(execution_events),
                "financial_execution_enabled": False,
                "payment_execution_enabled": False,
                "settlement_execution_enabled": False,
            },
        )
        return self._settlement_preparation_repository.save(record)

    def summarize_partner_records(self, partner_id: str) -> SettlementPreparationSummary:
        records = self._settlement_preparation_repository.list_for_partner(partner_id)
        if not records:
            raise ValueError("no settlement preparation records found for partner")

        ready_for_review_count = len(
            [record for record in records if record.status == SETTLEMENT_PREPARATION_STATUS_READY_FOR_REVIEW]
        )
        blocked_count = len(
            [record for record in records if record.status == SETTLEMENT_PREPARATION_STATUS_BLOCKED]
        )
        total_quoted_value = round(sum(record.quoted_final_price for record in records), 2)
        currency = records[0].currency

        summary = SettlementPreparationSummary(
            partner_id=partner_id,
            total_records=len(records),
            ready_for_review_count=ready_for_review_count,
            blocked_count=blocked_count,
            total_quoted_value=total_quoted_value,
            currency=currency,
            decision_classification=DECISION_CLASSIFICATION_NON_AUTONOMOUS,
            ai_execution_authority=False,
            records=records,
        )
        summary.validate()
        return summary

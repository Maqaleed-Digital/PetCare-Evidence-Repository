from petcare.partner_network.execution_visibility import (
    EXECUTION_EVENT_ACCEPTED,
    EXECUTION_EVENT_COMPLETED,
    EXECUTION_EVENT_IN_PROGRESS,
    ExecutionEventInput,
)
from petcare.partner_network.execution_visibility_repository import ExecutionVisibilityRepository
from petcare.partner_network.execution_visibility_service import ExecutionVisibilityService
from petcare.partner_network.orders import StructuredOrderInput
from petcare.partner_network.orders_repository import OrdersRepository
from petcare.partner_network.orders_service import OrdersService
from petcare.partner_network.pricing import PricingRule
from petcare.partner_network.pricing_repository import PricingRepository
from petcare.partner_network.settlement_preparation import SettlementPreparationInput
from petcare.partner_network.settlement_preparation_repository import SettlementPreparationRepository
from petcare.partner_network.settlement_preparation_service import SettlementPreparationService
from petcare.partner_network.settlement_review import (
    REVIEW_DECISION_APPROVE,
    REVIEW_DECISION_REJECT,
    SETTLEMENT_REVIEW_STATUS_APPROVED,
    SETTLEMENT_REVIEW_STATUS_IN_QUEUE,
    SETTLEMENT_REVIEW_STATUS_REJECTED,
    SettlementReviewDecisionInput,
)
from petcare.partner_network.settlement_review_query import SettlementReviewQuery
from petcare.partner_network.settlement_review_repository import SettlementReviewRepository
from petcare.partner_network.settlement_review_service import SettlementReviewService


def build_services():
    pricing_repository = PricingRepository()
    orders_repository = OrdersRepository()
    execution_visibility_repository = ExecutionVisibilityRepository()
    settlement_preparation_repository = SettlementPreparationRepository()
    settlement_review_repository = SettlementReviewRepository()

    orders_service = OrdersService(orders_repository, pricing_repository)
    execution_visibility_service = ExecutionVisibilityService(
        execution_visibility_repository,
        orders_repository,
    )
    settlement_preparation_service = SettlementPreparationService(
        settlement_preparation_repository,
        orders_repository,
        execution_visibility_repository,
    )
    settlement_review_service = SettlementReviewService(
        settlement_review_repository,
        settlement_preparation_repository,
    )
    return (
        pricing_repository,
        settlement_preparation_repository,
        settlement_review_repository,
        orders_service,
        execution_visibility_service,
        settlement_preparation_service,
        settlement_review_service,
    )


def seed_ready_for_review_record(
    pricing_repository,
    orders_service,
    execution_visibility_service,
    settlement_preparation_service,
    order_id,
    settlement_preparation_id,
):
    pricing_repository.save_rule(
        PricingRule(
            rule_id=f"rule-{order_id}",
            partner_id="partner-001",
            catalog_item_id="catalog-001",
            base_price=100.0,
            margin_percentage=10.0,
            promo_percentage=5.0,
            min_quantity=1,
            max_quantity=10,
            active=True,
            ai_execution_authority=False,
        )
    )
    orders_service.create_order(
        StructuredOrderInput(
            order_id=order_id,
            partner_id="partner-001",
            catalog_item_id="catalog-001",
            quantity=2,
            requested_by="ops.user",
            pricing_rule_id=f"rule-{order_id}",
            quoted_final_price=209.0,
            currency="SAR",
        )
    )
    orders_service.validate_order(order_id)
    orders_service.route_order(order_id)
    execution_visibility_service.record_event(ExecutionEventInput(order_id=order_id, event_type=EXECUTION_EVENT_ACCEPTED, recorded_by="partner.ops", partner_id="partner-001"))
    execution_visibility_service.record_event(ExecutionEventInput(order_id=order_id, event_type=EXECUTION_EVENT_IN_PROGRESS, recorded_by="partner.ops", partner_id="partner-001"))
    execution_visibility_service.record_event(ExecutionEventInput(order_id=order_id, event_type=EXECUTION_EVENT_COMPLETED, recorded_by="partner.ops", partner_id="partner-001"))
    settlement_preparation_service.prepare_record(
        SettlementPreparationInput(settlement_preparation_id=settlement_preparation_id, order_id=order_id, prepared_by="finance.ops")
    )


def test_settlement_review_queue_and_approve_decision() -> None:
    (pricing_repository, _, settlement_review_repository, orders_service, execution_visibility_service, settlement_preparation_service, settlement_review_service) = build_services()

    seed_ready_for_review_record(pricing_repository, orders_service, execution_visibility_service, settlement_preparation_service, "order-review-001", "settlement-prep-review-001")

    queue_item = settlement_review_service.enqueue_review_item("review-001", "settlement-prep-review-001")
    assert queue_item.status == SETTLEMENT_REVIEW_STATUS_IN_QUEUE
    assert queue_item.audit_events == ["settlement_review.queued"]

    decision = settlement_review_service.record_decision(
        SettlementReviewDecisionInput(review_id="review-001", reviewer_id="finance.reviewer", decision=REVIEW_DECISION_APPROVE, reason_code="MATCHED_EXECUTION_EVIDENCE")
    )
    assert decision.queue_status_after_decision == SETTLEMENT_REVIEW_STATUS_APPROVED
    assert decision.immutable_audit["financial_execution_enabled"] is False

    updated = settlement_review_repository.get_queue_item("review-001")
    assert updated.status == SETTLEMENT_REVIEW_STATUS_APPROVED
    assert updated.audit_events == ["settlement_review.queued", "settlement_review.approved"]


def test_settlement_review_reject_decision() -> None:
    (pricing_repository, _, settlement_review_repository, orders_service, execution_visibility_service, settlement_preparation_service, settlement_review_service) = build_services()

    seed_ready_for_review_record(pricing_repository, orders_service, execution_visibility_service, settlement_preparation_service, "order-review-002", "settlement-prep-review-002")
    settlement_review_service.enqueue_review_item("review-002", "settlement-prep-review-002")

    decision = settlement_review_service.record_decision(
        SettlementReviewDecisionInput(review_id="review-002", reviewer_id="finance.reviewer", decision=REVIEW_DECISION_REJECT, reason_code="MISMATCH_REQUIRES_INVESTIGATION", notes="manual discrepancy identified")
    )
    assert decision.queue_status_after_decision == SETTLEMENT_REVIEW_STATUS_REJECTED

    updated = settlement_review_repository.get_queue_item("review-002")
    assert updated.status == SETTLEMENT_REVIEW_STATUS_REJECTED
    assert updated.audit_events == ["settlement_review.queued", "settlement_review.rejected"]


def test_settlement_review_requires_ready_for_review_preparation() -> None:
    (_, settlement_preparation_repository, _, _, _, _, settlement_review_service) = build_services()

    try:
        settlement_review_service.enqueue_review_item("review-003", "missing-settlement-preparation")
        assert False
    except ValueError as exc:
        assert str(exc) == "settlement_preparation_id not found"

    from petcare.partner_network.settlement_preparation import SettlementPreparationRecord
    settlement_preparation_repository.save(
        SettlementPreparationRecord(
            settlement_preparation_id="settlement-prep-review-003",
            order_id="order-review-003",
            partner_id="partner-001",
            pricing_rule_id="rule-order-review-003",
            quoted_final_price=209.0,
            currency="SAR",
            execution_latest_event_type="FAILED",
            status="BLOCKED",
            boundary_reason="execution_failed_requires_manual_review",
            export_status="NOT_EXPORTED",
            human_review_required=True,
            audit_trace={},
        )
    )

    try:
        settlement_review_service.enqueue_review_item("review-003b", "settlement-prep-review-003")
        assert False
    except ValueError as exc:
        assert str(exc) == "settlement preparation must be READY_FOR_REVIEW before queueing"


def test_settlement_review_rejects_duplicate_decision() -> None:
    (pricing_repository, _, _, orders_service, execution_visibility_service, settlement_preparation_service, settlement_review_service) = build_services()

    seed_ready_for_review_record(pricing_repository, orders_service, execution_visibility_service, settlement_preparation_service, "order-review-004", "settlement-prep-review-004")
    settlement_review_service.enqueue_review_item("review-004", "settlement-prep-review-004")
    settlement_review_service.record_decision(SettlementReviewDecisionInput(review_id="review-004", reviewer_id="finance.reviewer", decision=REVIEW_DECISION_APPROVE, reason_code="MATCHED_EXECUTION_EVIDENCE"))

    try:
        settlement_review_service.record_decision(SettlementReviewDecisionInput(review_id="review-004", reviewer_id="finance.reviewer", decision=REVIEW_DECISION_REJECT, reason_code="SHOULD_NOT_WRITE_SECOND_DECISION"))
        assert False
    except ValueError as exc:
        assert str(exc) == "review item already decided"


def test_settlement_review_query_and_summary() -> None:
    (pricing_repository, _, settlement_review_repository, orders_service, execution_visibility_service, settlement_preparation_service, settlement_review_service) = build_services()
    query = SettlementReviewQuery()

    for order_id, prep_id, review_id in [
        ("order-review-005", "settlement-prep-review-005", "review-005"),
        ("order-review-006", "settlement-prep-review-006", "review-006"),
        ("order-review-007", "settlement-prep-review-007", "review-007"),
    ]:
        seed_ready_for_review_record(pricing_repository, orders_service, execution_visibility_service, settlement_preparation_service, order_id, prep_id)
        settlement_review_service.enqueue_review_item(review_id, prep_id)

    settlement_review_service.record_decision(SettlementReviewDecisionInput(review_id="review-006", reviewer_id="finance.reviewer", decision=REVIEW_DECISION_APPROVE, reason_code="MATCHED_EXECUTION_EVIDENCE"))
    settlement_review_service.record_decision(SettlementReviewDecisionInput(review_id="review-007", reviewer_id="finance.reviewer", decision=REVIEW_DECISION_REJECT, reason_code="MANUAL_EXCEPTION_REQUIRES_REWORK"))

    items = settlement_review_repository.list_queue_items_for_partner("partner-001")
    assert len(query.list_in_queue(items)) == 1
    assert len(query.list_approved(items)) == 1
    assert len(query.list_rejected(items)) == 1

    summary = settlement_review_service.summarize_partner_queue("partner-001")
    assert summary.total_items == 3
    assert summary.in_queue_count == 1
    assert summary.approved_count == 1
    assert summary.rejected_count == 1

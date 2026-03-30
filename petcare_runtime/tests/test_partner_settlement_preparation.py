from petcare.partner_network.execution_visibility import (
    EXECUTION_EVENT_ACCEPTED,
    EXECUTION_EVENT_COMPLETED,
    EXECUTION_EVENT_FAILED,
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
from petcare.partner_network.settlement_preparation import (
    SETTLEMENT_PREPARATION_STATUS_BLOCKED,
    SETTLEMENT_PREPARATION_STATUS_READY_FOR_REVIEW,
    SettlementPreparationInput,
)
from petcare.partner_network.settlement_preparation_query import SettlementPreparationQuery
from petcare.partner_network.settlement_preparation_repository import SettlementPreparationRepository
from petcare.partner_network.settlement_preparation_service import SettlementPreparationService


def build_services():
    pricing_repository = PricingRepository()
    orders_repository = OrdersRepository()
    execution_visibility_repository = ExecutionVisibilityRepository()
    settlement_preparation_repository = SettlementPreparationRepository()

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
    return (
        pricing_repository,
        orders_repository,
        execution_visibility_repository,
        settlement_preparation_repository,
        orders_service,
        execution_visibility_service,
        settlement_preparation_service,
    )


def seed_routed_order(orders_service: OrdersService, pricing_repository: PricingRepository, order_id: str) -> None:
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


def test_settlement_preparation_ready_for_review_after_completed_execution() -> None:
    (
        pricing_repository,
        _,
        _,
        _,
        orders_service,
        execution_visibility_service,
        settlement_preparation_service,
    ) = build_services()

    order_id = "order-settle-001"
    seed_routed_order(orders_service, pricing_repository, order_id)

    execution_visibility_service.record_event(
        ExecutionEventInput(order_id=order_id, event_type=EXECUTION_EVENT_ACCEPTED, recorded_by="partner.ops", partner_id="partner-001", sla_reference="SLA-01")
    )
    execution_visibility_service.record_event(
        ExecutionEventInput(order_id=order_id, event_type=EXECUTION_EVENT_IN_PROGRESS, recorded_by="partner.ops", partner_id="partner-001", sla_reference="SLA-01")
    )
    execution_visibility_service.record_event(
        ExecutionEventInput(order_id=order_id, event_type=EXECUTION_EVENT_COMPLETED, recorded_by="partner.ops", partner_id="partner-001", sla_reference="SLA-01")
    )

    record = settlement_preparation_service.prepare_record(
        SettlementPreparationInput(settlement_preparation_id="settlement-prep-001", order_id=order_id, prepared_by="finance.ops")
    )

    assert record.status == SETTLEMENT_PREPARATION_STATUS_READY_FOR_REVIEW
    assert record.boundary_reason == "completed_execution_ready_for_human_financial_review"
    assert record.export_status == "NOT_EXPORTED"
    assert record.human_review_required is True
    assert record.ai_execution_authority is False


def test_settlement_preparation_blocks_failed_execution() -> None:
    (
        pricing_repository,
        _,
        _,
        _,
        orders_service,
        execution_visibility_service,
        settlement_preparation_service,
    ) = build_services()

    order_id = "order-settle-002"
    seed_routed_order(orders_service, pricing_repository, order_id)

    execution_visibility_service.record_event(
        ExecutionEventInput(order_id=order_id, event_type=EXECUTION_EVENT_ACCEPTED, recorded_by="partner.ops", partner_id="partner-001")
    )
    execution_visibility_service.record_event(
        ExecutionEventInput(order_id=order_id, event_type=EXECUTION_EVENT_FAILED, recorded_by="partner.ops", partner_id="partner-001", notes="partner reported failure")
    )

    record = settlement_preparation_service.prepare_record(
        SettlementPreparationInput(settlement_preparation_id="settlement-prep-002", order_id=order_id, prepared_by="finance.ops")
    )

    assert record.status == SETTLEMENT_PREPARATION_STATUS_BLOCKED
    assert record.boundary_reason == "execution_failed_requires_manual_review"


def test_settlement_preparation_requires_execution_visibility_events() -> None:
    (pricing_repository, _, _, _, orders_service, _, settlement_preparation_service) = build_services()

    order_id = "order-settle-003"
    seed_routed_order(orders_service, pricing_repository, order_id)

    try:
        settlement_preparation_service.prepare_record(
            SettlementPreparationInput(settlement_preparation_id="settlement-prep-003", order_id=order_id, prepared_by="finance.ops")
        )
        assert False, "Expected execution visibility prerequisite failure"
    except ValueError as exc:
        assert str(exc) == "execution visibility events are required before settlement preparation"


def test_settlement_preparation_rejects_duplicate_order_record() -> None:
    (
        pricing_repository,
        _,
        _,
        _,
        orders_service,
        execution_visibility_service,
        settlement_preparation_service,
    ) = build_services()

    order_id = "order-settle-004"
    seed_routed_order(orders_service, pricing_repository, order_id)

    execution_visibility_service.record_event(ExecutionEventInput(order_id=order_id, event_type=EXECUTION_EVENT_ACCEPTED, recorded_by="partner.ops", partner_id="partner-001"))
    execution_visibility_service.record_event(ExecutionEventInput(order_id=order_id, event_type=EXECUTION_EVENT_IN_PROGRESS, recorded_by="partner.ops", partner_id="partner-001"))
    execution_visibility_service.record_event(ExecutionEventInput(order_id=order_id, event_type=EXECUTION_EVENT_COMPLETED, recorded_by="partner.ops", partner_id="partner-001"))

    settlement_preparation_service.prepare_record(
        SettlementPreparationInput(settlement_preparation_id="settlement-prep-004", order_id=order_id, prepared_by="finance.ops")
    )

    try:
        settlement_preparation_service.prepare_record(
            SettlementPreparationInput(settlement_preparation_id="settlement-prep-004b", order_id=order_id, prepared_by="finance.ops")
        )
        assert False, "Expected duplicate order settlement preparation failure"
    except ValueError as exc:
        assert str(exc) == "order_id already has a settlement preparation record"


def test_settlement_preparation_query_and_summary() -> None:
    (
        pricing_repository,
        _,
        _,
        settlement_preparation_repository,
        orders_service,
        execution_visibility_service,
        settlement_preparation_service,
    ) = build_services()
    query = SettlementPreparationQuery()

    ready_order_id = "order-settle-005"
    blocked_order_id = "order-settle-006"

    seed_routed_order(orders_service, pricing_repository, ready_order_id)
    execution_visibility_service.record_event(ExecutionEventInput(order_id=ready_order_id, event_type=EXECUTION_EVENT_ACCEPTED, recorded_by="partner.ops", partner_id="partner-001"))
    execution_visibility_service.record_event(ExecutionEventInput(order_id=ready_order_id, event_type=EXECUTION_EVENT_IN_PROGRESS, recorded_by="partner.ops", partner_id="partner-001"))
    execution_visibility_service.record_event(ExecutionEventInput(order_id=ready_order_id, event_type=EXECUTION_EVENT_COMPLETED, recorded_by="partner.ops", partner_id="partner-001"))
    settlement_preparation_service.prepare_record(SettlementPreparationInput(settlement_preparation_id="settlement-prep-005", order_id=ready_order_id, prepared_by="finance.ops"))

    seed_routed_order(orders_service, pricing_repository, blocked_order_id)
    execution_visibility_service.record_event(ExecutionEventInput(order_id=blocked_order_id, event_type=EXECUTION_EVENT_ACCEPTED, recorded_by="partner.ops", partner_id="partner-001"))
    execution_visibility_service.record_event(ExecutionEventInput(order_id=blocked_order_id, event_type=EXECUTION_EVENT_FAILED, recorded_by="partner.ops", partner_id="partner-001"))
    settlement_preparation_service.prepare_record(SettlementPreparationInput(settlement_preparation_id="settlement-prep-006", order_id=blocked_order_id, prepared_by="finance.ops"))

    records = settlement_preparation_repository.list_for_partner("partner-001")
    ready_records = query.list_ready_for_review(records)
    blocked_records = query.list_blocked(records)
    summary = settlement_preparation_service.summarize_partner_records("partner-001")

    assert len(ready_records) == 1
    assert ready_records[0].status == SETTLEMENT_PREPARATION_STATUS_READY_FOR_REVIEW
    assert len(blocked_records) == 1
    assert blocked_records[0].status == SETTLEMENT_PREPARATION_STATUS_BLOCKED
    assert summary.total_records == 2
    assert summary.ready_for_review_count == 1
    assert summary.blocked_count == 1
    assert summary.total_quoted_value == 418.0

from petcare.partner_network.execution_visibility import (
    EXECUTION_EVENT_ACCEPTED,
    EXECUTION_EVENT_COMPLETED,
    EXECUTION_EVENT_FAILED,
    EXECUTION_EVENT_IN_PROGRESS,
    ExecutionEventInput,
)
from petcare.partner_network.execution_visibility_query import ExecutionVisibilityQuery
from petcare.partner_network.execution_visibility_repository import ExecutionVisibilityRepository
from petcare.partner_network.execution_visibility_service import ExecutionVisibilityService
from petcare.partner_network.orders import StructuredOrderInput
from petcare.partner_network.orders_repository import OrdersRepository
from petcare.partner_network.orders_service import OrdersService
from petcare.partner_network.pricing import PricingRule
from petcare.partner_network.pricing_repository import PricingRepository


def build_services():
    pricing_repository = PricingRepository()
    orders_repository = OrdersRepository()
    execution_visibility_repository = ExecutionVisibilityRepository()

    orders_service = OrdersService(orders_repository, pricing_repository)
    execution_visibility_service = ExecutionVisibilityService(
        execution_visibility_repository,
        orders_repository,
    )
    return pricing_repository, orders_repository, execution_visibility_repository, orders_service, execution_visibility_service


def seed_routed_order(orders_service: OrdersService, pricing_repository: PricingRepository) -> str:
    pricing_repository.save_rule(
        PricingRule(
            rule_id="rule-wave06-001",
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
            order_id="order-wave06-001",
            partner_id="partner-001",
            catalog_item_id="catalog-001",
            quantity=2,
            requested_by="ops.user",
            pricing_rule_id="rule-wave06-001",
            quoted_final_price=209.0,
            currency="SAR",
        )
    )
    orders_service.validate_order("order-wave06-001")
    orders_service.route_order("order-wave06-001")
    return "order-wave06-001"


def test_execution_visibility_records_append_only_timeline() -> None:
    pricing_repository, _, _, orders_service, execution_visibility_service = build_services()
    order_id = seed_routed_order(orders_service, pricing_repository)

    accepted = execution_visibility_service.record_event(
        ExecutionEventInput(
            order_id=order_id,
            event_type=EXECUTION_EVENT_ACCEPTED,
            recorded_by="partner.ops",
            partner_id="partner-001",
            sla_reference="SLA-01",
        )
    )
    assert accepted.sequence_number == 1
    assert accepted.observational_only is True
    assert accepted.ai_execution_authority is False

    in_progress = execution_visibility_service.record_event(
        ExecutionEventInput(
            order_id=order_id,
            event_type=EXECUTION_EVENT_IN_PROGRESS,
            recorded_by="partner.ops",
            partner_id="partner-001",
            sla_reference="SLA-01",
        )
    )
    assert in_progress.sequence_number == 2

    completed = execution_visibility_service.record_event(
        ExecutionEventInput(
            order_id=order_id,
            event_type=EXECUTION_EVENT_COMPLETED,
            recorded_by="partner.ops",
            partner_id="partner-001",
            sla_reference="SLA-01",
        )
    )
    assert completed.sequence_number == 3

    timeline = execution_visibility_service.get_timeline(order_id)
    assert timeline.total_events == 3
    assert timeline.latest_event_type == EXECUTION_EVENT_COMPLETED
    assert timeline.sla_reference == "SLA-01"


def test_execution_visibility_rejects_unrouted_order() -> None:
    pricing_repository, _, _, orders_service, execution_visibility_service = build_services()

    pricing_repository.save_rule(
        PricingRule(
            rule_id="rule-wave06-002",
            partner_id="partner-001",
            catalog_item_id="catalog-001",
            base_price=100.0,
            active=True,
            ai_execution_authority=False,
        )
    )

    orders_service.create_order(
        StructuredOrderInput(
            order_id="order-wave06-002",
            partner_id="partner-001",
            catalog_item_id="catalog-001",
            quantity=1,
            requested_by="ops.user",
            pricing_rule_id="rule-wave06-002",
            quoted_final_price=100.0,
        )
    )

    try:
        execution_visibility_service.record_event(
            ExecutionEventInput(
                order_id="order-wave06-002",
                event_type=EXECUTION_EVENT_ACCEPTED,
                recorded_by="partner.ops",
                partner_id="partner-001",
            )
        )
        assert False, "Expected ROUTED prerequisite failure"
    except ValueError as exc:
        assert str(exc) == "order must be ROUTED before execution visibility events can be recorded"


def test_execution_visibility_rejects_invalid_transition() -> None:
    pricing_repository, _, _, orders_service, execution_visibility_service = build_services()
    order_id = seed_routed_order(orders_service, pricing_repository)

    execution_visibility_service.record_event(
        ExecutionEventInput(
            order_id=order_id,
            event_type=EXECUTION_EVENT_ACCEPTED,
            recorded_by="partner.ops",
            partner_id="partner-001",
        )
    )

    try:
        execution_visibility_service.record_event(
            ExecutionEventInput(
                order_id=order_id,
                event_type=EXECUTION_EVENT_COMPLETED,
                recorded_by="partner.ops",
                partner_id="partner-001",
            )
        )
        assert False, "Expected invalid transition failure"
    except ValueError as exc:
        assert str(exc) == "invalid execution event transition"


def test_execution_visibility_rejects_partner_mismatch() -> None:
    pricing_repository, _, _, orders_service, execution_visibility_service = build_services()
    order_id = seed_routed_order(orders_service, pricing_repository)

    try:
        execution_visibility_service.record_event(
            ExecutionEventInput(
                order_id=order_id,
                event_type=EXECUTION_EVENT_ACCEPTED,
                recorded_by="partner.ops",
                partner_id="partner-999",
            )
        )
        assert False, "Expected partner mismatch failure"
    except ValueError as exc:
        assert str(exc) == "execution event partner mismatch"


def test_execution_visibility_query_lists_failed_events() -> None:
    pricing_repository, _, execution_visibility_repository, orders_service, execution_visibility_service = build_services()
    order_id = seed_routed_order(orders_service, pricing_repository)
    query = ExecutionVisibilityQuery()

    execution_visibility_service.record_event(
        ExecutionEventInput(
            order_id=order_id,
            event_type=EXECUTION_EVENT_ACCEPTED,
            recorded_by="partner.ops",
            partner_id="partner-001",
        )
    )
    execution_visibility_service.record_event(
        ExecutionEventInput(
            order_id=order_id,
            event_type=EXECUTION_EVENT_FAILED,
            recorded_by="partner.ops",
            partner_id="partner-001",
            notes="inventory unavailable",
        )
    )

    failed_events = query.list_failed_events(
        execution_visibility_repository.list_events_for_order(order_id)
    )

    assert len(failed_events) == 1
    assert failed_events[0].event_type == EXECUTION_EVENT_FAILED
    assert failed_events[0].notes == "inventory unavailable"

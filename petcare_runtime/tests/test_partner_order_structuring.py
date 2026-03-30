from petcare.partner_network.orders import (
    ORDER_STATUS_CREATED,
    ORDER_STATUS_ROUTED,
    ORDER_STATUS_VALIDATED,
    StructuredOrderInput,
)
from petcare.partner_network.orders_query import OrdersQuery
from petcare.partner_network.orders_repository import OrdersRepository
from petcare.partner_network.orders_service import OrdersService
from petcare.partner_network.pricing import PricingRule
from petcare.partner_network.pricing_repository import PricingRepository


def build_service() -> tuple[OrdersService, OrdersRepository, PricingRepository]:
    orders_repository = OrdersRepository()
    pricing_repository = PricingRepository()
    service = OrdersService(orders_repository, pricing_repository)
    return service, orders_repository, pricing_repository


def seed_pricing_rule(pricing_repository: PricingRepository) -> PricingRule:
    rule = PricingRule(
        rule_id="rule-ep07-w05-001",
        partner_id="partner-001",
        catalog_item_id="catalog-001",
        base_price=100.0,
        margin_percentage=10.0,
        promo_percentage=5.0,
        min_quantity=1,
        max_quantity=10,
        currency="SAR",
        active=True,
        ai_execution_authority=False,
    )
    pricing_repository.save_rule(rule)
    return rule


def test_order_lifecycle_created_validated_routed() -> None:
    service, _, pricing_repository = build_service()
    pricing_rule = seed_pricing_rule(pricing_repository)

    created = service.create_order(
        StructuredOrderInput(
            order_id="order-001",
            partner_id="partner-001",
            catalog_item_id="catalog-001",
            quantity=2,
            requested_by="ops.user",
            pricing_rule_id=pricing_rule.rule_id,
            quoted_final_price=209.0,
            currency="SAR",
        )
    )
    assert created.status == ORDER_STATUS_CREATED
    assert created.audit_trace.events == ["order.created"]
    assert created.ai_execution_authority is False
    assert created.decision_classification == "NON_AUTONOMOUS_DECISION"

    validated = service.validate_order("order-001")
    assert validated.status == ORDER_STATUS_VALIDATED
    assert validated.audit_trace.events == ["order.created", "order.validated"]

    routed = service.route_order("order-001")
    assert routed.status == ORDER_STATUS_ROUTED
    assert routed.route_partner_id == "partner-001"
    assert routed.route_reason == "deterministic_partner_route_from_pricing_reference"
    assert routed.audit_trace.events == ["order.created", "order.validated", "order.routed"]


def test_order_rejects_missing_pricing_rule() -> None:
    service, _, _ = build_service()

    try:
        service.create_order(
            StructuredOrderInput(
                order_id="order-002",
                partner_id="partner-001",
                catalog_item_id="catalog-001",
                quantity=1,
                requested_by="ops.user",
                pricing_rule_id="missing-rule",
                quoted_final_price=100.0,
            )
        )
        assert False, "Expected missing pricing rule failure"
    except ValueError as exc:
        assert str(exc) == "pricing_rule_id not found"


def test_order_rejects_pricing_partner_mismatch() -> None:
    service, _, pricing_repository = build_service()
    pricing_rule = seed_pricing_rule(pricing_repository)

    try:
        service.create_order(
            StructuredOrderInput(
                order_id="order-003",
                partner_id="partner-999",
                catalog_item_id="catalog-001",
                quantity=1,
                requested_by="ops.user",
                pricing_rule_id=pricing_rule.rule_id,
                quoted_final_price=100.0,
            )
        )
        assert False, "Expected pricing rule partner mismatch"
    except ValueError as exc:
        assert str(exc) == "pricing rule partner mismatch"


def test_route_requires_validated_state() -> None:
    service, _, pricing_repository = build_service()
    pricing_rule = seed_pricing_rule(pricing_repository)

    service.create_order(
        StructuredOrderInput(
            order_id="order-004",
            partner_id="partner-001",
            catalog_item_id="catalog-001",
            quantity=1,
            requested_by="ops.user",
            pricing_rule_id=pricing_rule.rule_id,
            quoted_final_price=104.5,
        )
    )

    try:
        service.route_order("order-004")
        assert False, "Expected VALIDATED prerequisite failure"
    except ValueError as exc:
        assert str(exc) == "order must be VALIDATED before routing"


def test_orders_query_filters_routed_orders() -> None:
    service, orders_repository, pricing_repository = build_service()
    pricing_rule = seed_pricing_rule(pricing_repository)
    query = OrdersQuery()

    service.create_order(
        StructuredOrderInput(
            order_id="order-005",
            partner_id="partner-001",
            catalog_item_id="catalog-001",
            quantity=1,
            requested_by="ops.user",
            pricing_rule_id=pricing_rule.rule_id,
            quoted_final_price=104.5,
        )
    )
    service.validate_order("order-005")
    service.route_order("order-005")

    all_orders = orders_repository.list_for_partner("partner-001")
    routed_orders = query.list_routed_orders(all_orders)

    assert len(routed_orders) == 1
    assert routed_orders[0].order_id == "order-005"
    assert routed_orders[0].status == ORDER_STATUS_ROUTED

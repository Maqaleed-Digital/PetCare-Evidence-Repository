from .orders import (
    DECISION_CLASSIFICATION_NON_AUTONOMOUS,
    ORDER_STATUS_CREATED,
    ORDER_STATUS_ROUTED,
    ORDER_STATUS_VALIDATED,
    OrderAuditTrace,
    StructuredOrder,
    StructuredOrderInput,
)
from .orders_repository import OrdersRepository
from .pricing_repository import PricingRepository


class OrdersService:
    def __init__(self, orders_repository: OrdersRepository, pricing_repository: PricingRepository) -> None:
        self._orders_repository = orders_repository
        self._pricing_repository = pricing_repository

    def create_order(self, order_input: StructuredOrderInput) -> StructuredOrder:
        order_input.validate()

        if self._orders_repository.get(order_input.order_id) is not None:
            raise ValueError("order_id already exists")

        pricing_rule = self._pricing_repository.get_rule(order_input.pricing_rule_id)
        if pricing_rule is None:
            raise ValueError("pricing_rule_id not found")

        if not pricing_rule.active:
            raise ValueError("pricing rule is inactive")

        if pricing_rule.partner_id != order_input.partner_id:
            raise ValueError("pricing rule partner mismatch")

        if pricing_rule.catalog_item_id != order_input.catalog_item_id:
            raise ValueError("pricing rule catalog item mismatch")

        order = StructuredOrder(
            order_id=order_input.order_id,
            partner_id=order_input.partner_id,
            catalog_item_id=order_input.catalog_item_id,
            quantity=order_input.quantity,
            requested_by=order_input.requested_by,
            pricing_rule_id=order_input.pricing_rule_id,
            quoted_final_price=round(order_input.quoted_final_price, 2),
            currency=order_input.currency,
            status=ORDER_STATUS_CREATED,
            route_partner_id=None,
            route_reason=None,
            decision_classification=DECISION_CLASSIFICATION_NON_AUTONOMOUS,
            ai_execution_authority=False,
            audit_trace=OrderAuditTrace(
                pricing_rule_id=order_input.pricing_rule_id,
                quoted_final_price=round(order_input.quoted_final_price, 2),
                currency=order_input.currency,
                events=["order.created"],
            ),
            metadata={
                "notes": order_input.notes,
            },
        )
        return self._orders_repository.save(order)

    def validate_order(self, order_id: str) -> StructuredOrder:
        order = self._orders_repository.get(order_id)
        if order is None:
            raise ValueError("order not found")

        pricing_rule = self._pricing_repository.get_rule(order.pricing_rule_id)
        if pricing_rule is None:
            raise ValueError("pricing rule not found for order")

        if pricing_rule.partner_id != order.partner_id:
            raise ValueError("order partner no longer matches pricing rule")

        if pricing_rule.catalog_item_id != order.catalog_item_id:
            raise ValueError("order catalog item no longer matches pricing rule")

        if order.quantity < pricing_rule.min_quantity:
            raise ValueError("order quantity below pricing rule minimum")

        if pricing_rule.max_quantity is not None and order.quantity > pricing_rule.max_quantity:
            raise ValueError("order quantity above pricing rule maximum")

        validated = StructuredOrder(
            order_id=order.order_id,
            partner_id=order.partner_id,
            catalog_item_id=order.catalog_item_id,
            quantity=order.quantity,
            requested_by=order.requested_by,
            pricing_rule_id=order.pricing_rule_id,
            quoted_final_price=order.quoted_final_price,
            currency=order.currency,
            status=ORDER_STATUS_VALIDATED,
            route_partner_id=None,
            route_reason=None,
            decision_classification=DECISION_CLASSIFICATION_NON_AUTONOMOUS,
            ai_execution_authority=False,
            audit_trace=OrderAuditTrace(
                pricing_rule_id=order.audit_trace.pricing_rule_id,
                quoted_final_price=order.audit_trace.quoted_final_price,
                currency=order.audit_trace.currency,
                events=order.audit_trace.events + ["order.validated"],
            ),
            metadata=order.metadata,
        )
        return self._orders_repository.save(validated)

    def route_order(self, order_id: str) -> StructuredOrder:
        order = self._orders_repository.get(order_id)
        if order is None:
            raise ValueError("order not found")

        if order.status != ORDER_STATUS_VALIDATED:
            raise ValueError("order must be VALIDATED before routing")

        routed = StructuredOrder(
            order_id=order.order_id,
            partner_id=order.partner_id,
            catalog_item_id=order.catalog_item_id,
            quantity=order.quantity,
            requested_by=order.requested_by,
            pricing_rule_id=order.pricing_rule_id,
            quoted_final_price=order.quoted_final_price,
            currency=order.currency,
            status=ORDER_STATUS_ROUTED,
            route_partner_id=order.partner_id,
            route_reason="deterministic_partner_route_from_pricing_reference",
            decision_classification=DECISION_CLASSIFICATION_NON_AUTONOMOUS,
            ai_execution_authority=False,
            audit_trace=OrderAuditTrace(
                pricing_rule_id=order.audit_trace.pricing_rule_id,
                quoted_final_price=order.audit_trace.quoted_final_price,
                currency=order.audit_trace.currency,
                events=order.audit_trace.events + ["order.routed"],
            ),
            metadata=order.metadata,
        )
        return self._orders_repository.save(routed)

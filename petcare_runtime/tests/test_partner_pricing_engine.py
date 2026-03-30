from petcare.partner_network.pricing import PricingInput, PricingRule
from petcare.partner_network.pricing_query import PricingQuery
from petcare.partner_network.pricing_repository import PricingRepository
from petcare.partner_network.pricing_service import PricingService


def build_service() -> PricingService:
    repository = PricingRepository()
    return PricingService(repository)


def test_create_rule_and_calculate_offer_with_explainability() -> None:
    service = build_service()

    rule = PricingRule(
        rule_id="rule-001",
        partner_id="partner-001",
        catalog_item_id="catalog-001",
        base_price=100.0,
        margin_percentage=10.0,
        promo_percentage=5.0,
        min_quantity=1,
        max_quantity=10,
    )
    service.create_rule(rule)

    result = service.calculate_offer(
        PricingInput(
            partner_id="partner-001",
            catalog_item_id="catalog-001",
            quantity=2,
        )
    )

    assert result.base_total == 200.0
    assert result.margin_amount == 20.0
    assert result.promo_discount_amount == 11.0
    assert result.final_price == 209.0
    assert result.explanation.human_override_required is True
    assert result.explanation.ai_execution_authority is False
    assert result.audit_trace["decision_classification"] == "NON_AUTONOMOUS_DECISION"


def test_quantity_below_minimum_is_rejected() -> None:
    service = build_service()
    service.create_rule(
        PricingRule(
            rule_id="rule-002",
            partner_id="partner-002",
            catalog_item_id="catalog-002",
            base_price=50.0,
            min_quantity=2,
        )
    )

    try:
        service.calculate_offer(
            PricingInput(
                partner_id="partner-002",
                catalog_item_id="catalog-002",
                quantity=1,
            )
        )
        assert False, "Expected ValueError for quantity below min_quantity"
    except ValueError as exc:
        assert str(exc) == "quantity is below min_quantity"


def test_best_offer_selection_is_deterministic() -> None:
    repository = PricingRepository()
    service = PricingService(repository)
    query = PricingQuery()

    service.create_rule(
        PricingRule(
            rule_id="rule-a",
            partner_id="partner-a",
            catalog_item_id="catalog-x",
            base_price=100.0,
            margin_percentage=10.0,
        )
    )
    service.create_rule(
        PricingRule(
            rule_id="rule-b",
            partner_id="partner-b",
            catalog_item_id="catalog-x",
            base_price=95.0,
            margin_percentage=10.0,
        )
    )

    offers = [
        service.calculate_offer(
            PricingInput(partner_id="partner-a", catalog_item_id="catalog-x", quantity=1)
        ),
        service.calculate_offer(
            PricingInput(partner_id="partner-b", catalog_item_id="catalog-x", quantity=1)
        ),
    ]

    best_offer = query.select_best_offer(offers)

    assert best_offer.partner_id == "partner-b"
    assert best_offer.final_price == 104.5


def test_override_request_requires_reason() -> None:
    try:
        PricingInput(
            partner_id="partner-003",
            catalog_item_id="catalog-003",
            quantity=1,
            override_requested=True,
            override_reason=None,
        ).validate()
        assert False, "Expected ValueError when override_requested is true without a reason"
    except ValueError as exc:
        assert str(exc) == "override_reason is required when override_requested is true"

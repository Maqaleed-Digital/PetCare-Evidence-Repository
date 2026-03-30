from .pricing import (
    DECISION_CLASSIFICATION_NON_AUTONOMOUS,
    PricingExplanation,
    PricingInput,
    PricingOutput,
    PricingRule,
)
from .pricing_repository import PricingRepository


class PricingService:
    def __init__(self, repository: PricingRepository) -> None:
        self._repository = repository

    def create_rule(self, rule: PricingRule) -> PricingRule:
        return self._repository.save_rule(rule)

    def calculate_offer(self, pricing_input: PricingInput) -> PricingOutput:
        pricing_input.validate()

        rule = self._repository.find_active_rule(
            partner_id=pricing_input.partner_id,
            catalog_item_id=pricing_input.catalog_item_id,
        )
        if rule is None:
            raise ValueError("No active pricing rule found")

        rule.validate()

        if pricing_input.quantity < rule.min_quantity:
            raise ValueError("quantity is below min_quantity")
        if rule.max_quantity is not None and pricing_input.quantity > rule.max_quantity:
            raise ValueError("quantity is above max_quantity")

        unit_base_price = round(rule.base_price, 2)
        base_total = round(unit_base_price * pricing_input.quantity, 2)
        margin_amount = round(base_total * (rule.margin_percentage / 100.0), 2)
        subtotal_after_margin = round(base_total + margin_amount, 2)
        promo_discount_amount = round(subtotal_after_margin * (rule.promo_percentage / 100.0), 2)
        final_price = round(subtotal_after_margin - promo_discount_amount, 2)

        explanation = PricingExplanation(
            components={
                "unit_base_price": unit_base_price,
                "base_total": base_total,
                "margin_percentage": round(rule.margin_percentage, 2),
                "margin_amount": margin_amount,
                "promo_percentage": round(rule.promo_percentage, 2),
                "promo_discount_amount": promo_discount_amount,
                "final_price": final_price,
            },
            rule_trace=[
                f"rule_id={rule.rule_id}",
                "calculation=base_total_plus_margin_minus_promo_discount",
                "selection=deterministic_single_active_rule",
            ],
            human_override_required=True,
            ai_execution_authority=False,
            decision_classification=DECISION_CLASSIFICATION_NON_AUTONOMOUS,
        )

        audit_trace = {
            "rule_id": rule.rule_id,
            "partner_id": rule.partner_id,
            "catalog_item_id": rule.catalog_item_id,
            "quantity": pricing_input.quantity,
            "override_requested": pricing_input.override_requested,
            "override_reason": pricing_input.override_reason,
            "decision_classification": DECISION_CLASSIFICATION_NON_AUTONOMOUS,
            "ai_execution_authority": False,
        }

        return PricingOutput(
            partner_id=pricing_input.partner_id,
            catalog_item_id=pricing_input.catalog_item_id,
            quantity=pricing_input.quantity,
            currency=rule.currency,
            unit_base_price=unit_base_price,
            base_total=base_total,
            margin_amount=margin_amount,
            promo_discount_amount=promo_discount_amount,
            final_price=final_price,
            explanation=explanation,
            audit_trace=audit_trace,
        )

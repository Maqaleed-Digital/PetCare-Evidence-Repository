from dataclasses import dataclass, field
from typing import Dict, List, Optional


DECISION_CLASSIFICATION_NON_AUTONOMOUS = "NON_AUTONOMOUS_DECISION"


@dataclass(frozen=True)
class PricingRule:
    rule_id: str
    partner_id: str
    catalog_item_id: str
    base_price: float
    margin_percentage: float = 0.0
    promo_percentage: float = 0.0
    min_quantity: int = 1
    max_quantity: Optional[int] = None
    currency: str = "SAR"
    active: bool = True
    ai_execution_authority: bool = False

    def validate(self) -> None:
        if not self.rule_id.strip():
            raise ValueError("rule_id is required")
        if not self.partner_id.strip():
            raise ValueError("partner_id is required")
        if not self.catalog_item_id.strip():
            raise ValueError("catalog_item_id is required")
        if self.base_price < 0:
            raise ValueError("base_price cannot be negative")
        if not 0 <= self.margin_percentage <= 100:
            raise ValueError("margin_percentage must be between 0 and 100")
        if not 0 <= self.promo_percentage <= 100:
            raise ValueError("promo_percentage must be between 0 and 100")
        if self.min_quantity < 1:
            raise ValueError("min_quantity must be at least 1")
        if self.max_quantity is not None and self.max_quantity < self.min_quantity:
            raise ValueError("max_quantity must be greater than or equal to min_quantity")
        if self.ai_execution_authority:
            raise ValueError("ai_execution_authority must remain false")


@dataclass(frozen=True)
class PricingInput:
    partner_id: str
    catalog_item_id: str
    quantity: int
    override_requested: bool = False
    override_reason: Optional[str] = None

    def validate(self) -> None:
        if not self.partner_id.strip():
            raise ValueError("partner_id is required")
        if not self.catalog_item_id.strip():
            raise ValueError("catalog_item_id is required")
        if self.quantity < 1:
            raise ValueError("quantity must be at least 1")
        if self.override_requested and not (self.override_reason and self.override_reason.strip()):
            raise ValueError("override_reason is required when override_requested is true")


@dataclass(frozen=True)
class PricingExplanation:
    components: Dict[str, float]
    rule_trace: List[str]
    human_override_required: bool
    ai_execution_authority: bool = False
    decision_classification: str = DECISION_CLASSIFICATION_NON_AUTONOMOUS


@dataclass(frozen=True)
class PricingOutput:
    partner_id: str
    catalog_item_id: str
    quantity: int
    currency: str
    unit_base_price: float
    base_total: float
    margin_amount: float
    promo_discount_amount: float
    final_price: float
    explanation: PricingExplanation
    audit_trace: Dict[str, object] = field(default_factory=dict)

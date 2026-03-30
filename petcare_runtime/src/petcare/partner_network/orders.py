from dataclasses import dataclass, field
from typing import Dict, List, Optional


ORDER_STATUS_CREATED = "CREATED"
ORDER_STATUS_VALIDATED = "VALIDATED"
ORDER_STATUS_ROUTED = "ROUTED"

DECISION_CLASSIFICATION_NON_AUTONOMOUS = "NON_AUTONOMOUS_DECISION"


@dataclass(frozen=True)
class StructuredOrderInput:
    order_id: str
    partner_id: str
    catalog_item_id: str
    quantity: int
    requested_by: str
    pricing_rule_id: str
    quoted_final_price: float
    currency: str = "SAR"
    notes: Optional[str] = None

    def validate(self) -> None:
        if not self.order_id.strip():
            raise ValueError("order_id is required")
        if not self.partner_id.strip():
            raise ValueError("partner_id is required")
        if not self.catalog_item_id.strip():
            raise ValueError("catalog_item_id is required")
        if not self.requested_by.strip():
            raise ValueError("requested_by is required")
        if not self.pricing_rule_id.strip():
            raise ValueError("pricing_rule_id is required")
        if self.quantity < 1:
            raise ValueError("quantity must be at least 1")
        if self.quoted_final_price < 0:
            raise ValueError("quoted_final_price cannot be negative")
        if not self.currency.strip():
            raise ValueError("currency is required")


@dataclass(frozen=True)
class OrderAuditTrace:
    pricing_rule_id: str
    quoted_final_price: float
    currency: str
    decision_classification: str = DECISION_CLASSIFICATION_NON_AUTONOMOUS
    ai_execution_authority: bool = False
    human_override_required: bool = True
    events: List[str] = field(default_factory=list)


@dataclass(frozen=True)
class StructuredOrder:
    order_id: str
    partner_id: str
    catalog_item_id: str
    quantity: int
    requested_by: str
    pricing_rule_id: str
    quoted_final_price: float
    currency: str
    status: str
    route_partner_id: Optional[str]
    route_reason: Optional[str]
    decision_classification: str
    ai_execution_authority: bool
    audit_trace: OrderAuditTrace
    metadata: Dict[str, object] = field(default_factory=dict)

    def validate(self) -> None:
        if self.status not in {ORDER_STATUS_CREATED, ORDER_STATUS_VALIDATED, ORDER_STATUS_ROUTED}:
            raise ValueError("invalid order status")
        if self.ai_execution_authority:
            raise ValueError("ai_execution_authority must remain false")
        if self.decision_classification != DECISION_CLASSIFICATION_NON_AUTONOMOUS:
            raise ValueError("decision_classification must remain NON_AUTONOMOUS_DECISION")

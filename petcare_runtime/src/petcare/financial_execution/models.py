from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from enum import Enum
from typing import Dict, List


TWO_DP = Decimal("0.01")


def q(value: Decimal | str | int | float) -> Decimal:
    return Decimal(str(value)).quantize(TWO_DP)


class SettlementStatus(str, Enum):
    PREPARED = "prepared"
    APPROVED = "approved"
    INSTRUCTION_READY = "instruction_ready"
    EXECUTED = "executed"
    RECONCILED = "reconciled"
    BLOCKED = "blocked"
    REVERSED = "reversed"


class PaymentMethod(str, Enum):
    MANUAL_BANK_TRANSFER = "manual_bank_transfer"
    ERP_EXPORT = "erp_export"
    GATEWAY_PLACEHOLDER = "gateway_placeholder"


@dataclass(frozen=True)
class CurrencyAmount:
    currency: str
    amount: Decimal

    def __post_init__(self) -> None:
        object.__setattr__(self, "amount", q(self.amount))
        if self.amount < Decimal("0.00"):
            raise ValueError("currency amount must be non-negative")
        if not self.currency:
            raise ValueError("currency is required")


@dataclass(frozen=True)
class SettlementLine:
    order_id: str
    partner_id: str
    currency: str
    gross_amount: Decimal
    platform_fee_amount: Decimal
    net_payout_amount: Decimal

    def __post_init__(self) -> None:
        gross = q(self.gross_amount)
        fee = q(self.platform_fee_amount)
        net = q(self.net_payout_amount)

        object.__setattr__(self, "gross_amount", gross)
        object.__setattr__(self, "platform_fee_amount", fee)
        object.__setattr__(self, "net_payout_amount", net)

        if not self.order_id:
            raise ValueError("order_id is required")
        if not self.partner_id:
            raise ValueError("partner_id is required")
        if not self.currency:
            raise ValueError("currency is required")
        if gross <= Decimal("0.00"):
            raise ValueError("gross_amount must be positive")
        if fee < Decimal("0.00"):
            raise ValueError("platform_fee_amount must be non-negative")
        if net < Decimal("0.00"):
            raise ValueError("net_payout_amount must be non-negative")
        if gross != fee + net:
            raise ValueError("gross_amount must equal platform_fee_amount + net_payout_amount")


@dataclass(frozen=True)
class ApprovalRecord:
    approval_id: str
    approved_by: str
    approved_at: str
    reason: str

    def __post_init__(self) -> None:
        if not self.approval_id:
            raise ValueError("approval_id is required")
        if not self.approved_by:
            raise ValueError("approved_by is required")
        if not self.approved_at:
            raise ValueError("approved_at is required")
        if not self.reason:
            raise ValueError("reason is required")


@dataclass(frozen=True)
class SettlementPackage:
    settlement_id: str
    prepared_at: str
    lines: List[SettlementLine]
    status: SettlementStatus = SettlementStatus.PREPARED
    approval: ApprovalRecord | None = None

    def __post_init__(self) -> None:
        if not self.settlement_id:
            raise ValueError("settlement_id is required")
        if not self.prepared_at:
            raise ValueError("prepared_at is required")
        if not self.lines:
            raise ValueError("at least one settlement line is required")

        currencies = {line.currency for line in self.lines}
        if len(currencies) != 1:
            raise ValueError("all settlement lines must use the same currency")


@dataclass(frozen=True)
class ExecutionInstruction:
    instruction_id: str
    settlement_id: str
    payment_method: PaymentMethod
    currency: str
    gross_total: Decimal
    platform_fee_total: Decimal
    net_payout_total: Decimal
    created_by: str
    created_at: str
    settlement_approval_id: str
    payload_checksum: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "gross_total", q(self.gross_total))
        object.__setattr__(self, "platform_fee_total", q(self.platform_fee_total))
        object.__setattr__(self, "net_payout_total", q(self.net_payout_total))

        if not self.instruction_id:
            raise ValueError("instruction_id is required")
        if not self.settlement_id:
            raise ValueError("settlement_id is required")
        if not self.currency:
            raise ValueError("currency is required")
        if not self.created_by:
            raise ValueError("created_by is required")
        if not self.created_at:
            raise ValueError("created_at is required")
        if not self.settlement_approval_id:
            raise ValueError("settlement_approval_id is required")
        if self.gross_total != self.platform_fee_total + self.net_payout_total:
            raise ValueError("gross_total must equal platform_fee_total + net_payout_total")


@dataclass(frozen=True)
class ExecutionRecord:
    execution_id: str
    instruction_id: str
    executed_by: str
    executed_at: str
    execution_approval_id: str
    status: SettlementStatus = SettlementStatus.EXECUTED

    def __post_init__(self) -> None:
        if not self.execution_id:
            raise ValueError("execution_id is required")
        if not self.instruction_id:
            raise ValueError("instruction_id is required")
        if not self.executed_by:
            raise ValueError("executed_by is required")
        if not self.executed_at:
            raise ValueError("executed_at is required")
        if not self.execution_approval_id:
            raise ValueError("execution_approval_id is required")


@dataclass(frozen=True)
class InvoiceLine:
    order_id: str
    gross_amount: Decimal
    platform_fee_amount: Decimal
    net_amount: Decimal

    def __post_init__(self) -> None:
        object.__setattr__(self, "gross_amount", q(self.gross_amount))
        object.__setattr__(self, "platform_fee_amount", q(self.platform_fee_amount))
        object.__setattr__(self, "net_amount", q(self.net_amount))
        if self.gross_amount != self.platform_fee_amount + self.net_amount:
            raise ValueError("invoice line must balance")


@dataclass(frozen=True)
class Invoice:
    invoice_id: str
    partner_id: str
    settlement_id: str
    currency: str
    issued_at: str
    lines: List[InvoiceLine]
    gross_total: Decimal
    platform_fee_total: Decimal
    net_total: Decimal

    def __post_init__(self) -> None:
        object.__setattr__(self, "gross_total", q(self.gross_total))
        object.__setattr__(self, "platform_fee_total", q(self.platform_fee_total))
        object.__setattr__(self, "net_total", q(self.net_total))
        if self.gross_total != self.platform_fee_total + self.net_total:
            raise ValueError("invoice totals must balance")


@dataclass(frozen=True)
class ReconciliationVariance:
    field_name: str
    expected_amount: Decimal
    actual_amount: Decimal

    def __post_init__(self) -> None:
        object.__setattr__(self, "expected_amount", q(self.expected_amount))
        object.__setattr__(self, "actual_amount", q(self.actual_amount))


@dataclass(frozen=True)
class ReconciliationReport:
    report_id: str
    instruction_id: str
    checked_at: str
    currency: str
    matched: bool
    variances: List[ReconciliationVariance] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.report_id:
            raise ValueError("report_id is required")
        if not self.instruction_id:
            raise ValueError("instruction_id is required")
        if not self.checked_at:
            raise ValueError("checked_at is required")
        if not self.currency:
            raise ValueError("currency is required")


@dataclass(frozen=True)
class LedgerEntry:
    entry_id: str
    settlement_id: str
    reference_id: str
    event_type: str
    occurred_at: str
    payload_checksum: str
    metadata: Dict[str, str]

    def __post_init__(self) -> None:
        if not self.entry_id:
            raise ValueError("entry_id is required")
        if not self.settlement_id:
            raise ValueError("settlement_id is required")
        if not self.reference_id:
            raise ValueError("reference_id is required")
        if not self.event_type:
            raise ValueError("event_type is required")
        if not self.occurred_at:
            raise ValueError("occurred_at is required")
        if not self.payload_checksum:
            raise ValueError("payload_checksum is required")

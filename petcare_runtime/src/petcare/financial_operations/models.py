from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from enum import Enum


TWO_DP = Decimal("0.01")


def q(value: Decimal | str | int | float) -> Decimal:
    return Decimal(str(value)).quantize(TWO_DP)


class InvoiceOpsStatus(str, Enum):
    DRAFT = "draft"
    ISSUED = "issued"
    ACKNOWLEDGED = "acknowledged"
    DISPUTED = "disputed"
    RESOLVED = "resolved"
    CLOSED = "closed"


class PaymentTrackingStatus(str, Enum):
    PENDING_EXTERNAL = "pending_external"
    RECEIVED_EXTERNAL_SIGNAL = "received_external_signal"
    UNDER_REVIEW = "under_review"
    MATCHED = "matched"
    MISMATCHED = "mismatched"
    CLOSED = "closed"


class ReconciliationStatus(str, Enum):
    DETECTED = "detected"
    UNDER_REVIEW = "under_review"
    RESOLVED = "resolved"
    CLOSED = "closed"


class DisputeStatus(str, Enum):
    OPEN = "open"
    UNDER_REVIEW = "under_review"
    RESOLVED = "resolved"
    CLOSED = "closed"


@dataclass(frozen=True)
class InvoiceLifecycleRecord:
    invoice_id: str
    partner_id: str
    settlement_id: str
    currency: str
    issued_at: str | None
    status: InvoiceOpsStatus
    gross_total: Decimal
    platform_fee_total: Decimal
    net_total: Decimal
    last_transition_at: str
    acknowledged_at: str | None = None
    closed_at: str | None = None
    dispute_case_id: str | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "gross_total", q(self.gross_total))
        object.__setattr__(self, "platform_fee_total", q(self.platform_fee_total))
        object.__setattr__(self, "net_total", q(self.net_total))
        if not self.invoice_id:
            raise ValueError("invoice_id is required")
        if not self.partner_id:
            raise ValueError("partner_id is required")
        if not self.settlement_id:
            raise ValueError("settlement_id is required")
        if not self.currency:
            raise ValueError("currency is required")
        if not self.last_transition_at:
            raise ValueError("last_transition_at is required")
        if self.gross_total != self.platform_fee_total + self.net_total:
            raise ValueError("invoice totals must balance")


@dataclass(frozen=True)
class PaymentStatusRecord:
    instruction_id: str
    external_reference_id: str | None
    status: PaymentTrackingStatus
    last_updated_at: str
    last_signal_source: str | None = None
    last_signal_payload_ref: str | None = None

    def __post_init__(self) -> None:
        if not self.instruction_id:
            raise ValueError("instruction_id is required")
        if not self.last_updated_at:
            raise ValueError("last_updated_at is required")


@dataclass(frozen=True)
class ReconciliationResolutionRecord:
    resolution_id: str
    resolved_by: str
    resolved_at: str
    reason: str

    def __post_init__(self) -> None:
        if not self.resolution_id:
            raise ValueError("resolution_id is required")
        if not self.resolved_by:
            raise ValueError("resolved_by is required")
        if not self.resolved_at:
            raise ValueError("resolved_at is required")
        if not self.reason:
            raise ValueError("reason is required")


@dataclass(frozen=True)
class ReconciliationCase:
    case_id: str
    instruction_id: str
    currency: str
    expected_total: Decimal
    actual_total: Decimal
    variance_total: Decimal
    status: ReconciliationStatus
    detected_at: str
    resolution: ReconciliationResolutionRecord | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "expected_total", q(self.expected_total))
        object.__setattr__(self, "actual_total", q(self.actual_total))
        object.__setattr__(self, "variance_total", q(self.variance_total))
        if not self.case_id:
            raise ValueError("case_id is required")
        if not self.instruction_id:
            raise ValueError("instruction_id is required")
        if not self.currency:
            raise ValueError("currency is required")
        if not self.detected_at:
            raise ValueError("detected_at is required")


@dataclass(frozen=True)
class DisputeEvidenceRef:
    evidence_id: str
    reference_uri: str
    uploaded_at: str

    def __post_init__(self) -> None:
        if not self.evidence_id:
            raise ValueError("evidence_id is required")
        if not self.reference_uri:
            raise ValueError("reference_uri is required")
        if not self.uploaded_at:
            raise ValueError("uploaded_at is required")


@dataclass(frozen=True)
class DisputeResolutionRecord:
    resolution_id: str
    resolved_by: str
    resolved_at: str
    reason: str

    def __post_init__(self) -> None:
        if not self.resolution_id:
            raise ValueError("resolution_id is required")
        if not self.resolved_by:
            raise ValueError("resolved_by is required")
        if not self.resolved_at:
            raise ValueError("resolved_at is required")
        if not self.reason:
            raise ValueError("reason is required")


@dataclass(frozen=True)
class DisputeCase:
    dispute_id: str
    invoice_id: str
    partner_id: str
    status: DisputeStatus
    opened_at: str
    opened_by: str
    reason: str
    evidence_refs: list[DisputeEvidenceRef] = field(default_factory=list)
    resolution: DisputeResolutionRecord | None = None
    closed_at: str | None = None

    def __post_init__(self) -> None:
        if not self.dispute_id:
            raise ValueError("dispute_id is required")
        if not self.invoice_id:
            raise ValueError("invoice_id is required")
        if not self.partner_id:
            raise ValueError("partner_id is required")
        if not self.opened_at:
            raise ValueError("opened_at is required")
        if not self.opened_by:
            raise ValueError("opened_by is required")
        if not self.reason:
            raise ValueError("reason is required")


@dataclass(frozen=True)
class PartnerStatementLine:
    invoice_id: str
    settlement_id: str
    invoice_status: str
    gross_total: Decimal
    net_total: Decimal

    def __post_init__(self) -> None:
        object.__setattr__(self, "gross_total", q(self.gross_total))
        object.__setattr__(self, "net_total", q(self.net_total))
        if not self.invoice_id:
            raise ValueError("invoice_id is required")
        if not self.settlement_id:
            raise ValueError("settlement_id is required")
        if not self.invoice_status:
            raise ValueError("invoice_status is required")


@dataclass(frozen=True)
class PartnerStatement:
    statement_id: str
    partner_id: str
    currency: str
    generated_at: str
    lines: list[PartnerStatementLine]
    gross_total: Decimal
    net_total: Decimal
    open_invoice_count: int

    def __post_init__(self) -> None:
        object.__setattr__(self, "gross_total", q(self.gross_total))
        object.__setattr__(self, "net_total", q(self.net_total))
        if not self.statement_id:
            raise ValueError("statement_id is required")
        if not self.partner_id:
            raise ValueError("partner_id is required")
        if not self.currency:
            raise ValueError("currency is required")
        if not self.generated_at:
            raise ValueError("generated_at is required")


@dataclass(frozen=True)
class FinancialVisibilitySnapshot:
    snapshot_id: str
    generated_at: str
    open_invoice_count: int
    disputed_invoice_count: int
    unresolved_variance_count: int
    partner_exposure_total: Decimal

    def __post_init__(self) -> None:
        object.__setattr__(self, "partner_exposure_total", q(self.partner_exposure_total))
        if not self.snapshot_id:
            raise ValueError("snapshot_id is required")
        if not self.generated_at:
            raise ValueError("generated_at is required")

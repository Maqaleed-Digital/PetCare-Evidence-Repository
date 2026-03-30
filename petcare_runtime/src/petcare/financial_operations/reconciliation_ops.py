from __future__ import annotations

from decimal import Decimal

from .models import (
    ReconciliationCase,
    ReconciliationResolutionRecord,
    ReconciliationStatus,
    q,
)


def detect_reconciliation_case(
    case_id: str,
    instruction_id: str,
    currency: str,
    expected_total: Decimal,
    actual_total: Decimal,
    detected_at: str,
) -> ReconciliationCase:
    expected = q(expected_total)
    actual = q(actual_total)
    variance = q(actual - expected)
    return ReconciliationCase(
        case_id=case_id,
        instruction_id=instruction_id,
        currency=currency,
        expected_total=expected,
        actual_total=actual,
        variance_total=variance,
        status=ReconciliationStatus.DETECTED,
        detected_at=detected_at,
    )


def resolve_reconciliation_case(
    case: ReconciliationCase,
    resolution: ReconciliationResolutionRecord,
) -> ReconciliationCase:
    if case.status not in {ReconciliationStatus.DETECTED, ReconciliationStatus.UNDER_REVIEW}:
        raise ValueError("reconciliation case cannot be resolved from current state")
    return ReconciliationCase(
        case_id=case.case_id,
        instruction_id=case.instruction_id,
        currency=case.currency,
        expected_total=case.expected_total,
        actual_total=case.actual_total,
        variance_total=case.variance_total,
        status=ReconciliationStatus.RESOLVED,
        detected_at=case.detected_at,
        resolution=resolution,
    )

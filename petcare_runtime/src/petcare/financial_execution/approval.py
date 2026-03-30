from __future__ import annotations

from .models import ApprovalRecord, SettlementPackage, SettlementStatus


def approve_settlement(
    settlement: SettlementPackage,
    approval: ApprovalRecord,
) -> SettlementPackage:
    if settlement.status != SettlementStatus.PREPARED:
        raise ValueError("only prepared settlements can be approved")

    return SettlementPackage(
        settlement_id=settlement.settlement_id,
        prepared_at=settlement.prepared_at,
        lines=settlement.lines,
        status=SettlementStatus.APPROVED,
        approval=approval,
    )


def approve_execution(approval: ApprovalRecord) -> ApprovalRecord:
    return approval

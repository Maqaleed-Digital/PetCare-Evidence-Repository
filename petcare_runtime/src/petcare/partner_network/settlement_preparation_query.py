from typing import List

from .settlement_preparation import (
    SETTLEMENT_PREPARATION_STATUS_BLOCKED,
    SETTLEMENT_PREPARATION_STATUS_READY_FOR_REVIEW,
    SettlementPreparationRecord,
)


class SettlementPreparationQuery:
    def list_ready_for_review(self, records: List[SettlementPreparationRecord]) -> List[SettlementPreparationRecord]:
        return sorted(
            [record for record in records if record.status == SETTLEMENT_PREPARATION_STATUS_READY_FOR_REVIEW],
            key=lambda item: item.settlement_preparation_id,
        )

    def list_blocked(self, records: List[SettlementPreparationRecord]) -> List[SettlementPreparationRecord]:
        return sorted(
            [record for record in records if record.status == SETTLEMENT_PREPARATION_STATUS_BLOCKED],
            key=lambda item: item.settlement_preparation_id,
        )

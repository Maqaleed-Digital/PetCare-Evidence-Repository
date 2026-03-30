from typing import List

from .settlement_review import (
    SETTLEMENT_REVIEW_STATUS_APPROVED,
    SETTLEMENT_REVIEW_STATUS_IN_QUEUE,
    SETTLEMENT_REVIEW_STATUS_REJECTED,
    SettlementReviewQueueItem,
)


class SettlementReviewQuery:
    def list_in_queue(self, items: List[SettlementReviewQueueItem]) -> List[SettlementReviewQueueItem]:
        return sorted(
            [item for item in items if item.status == SETTLEMENT_REVIEW_STATUS_IN_QUEUE],
            key=lambda item: item.review_id,
        )

    def list_approved(self, items: List[SettlementReviewQueueItem]) -> List[SettlementReviewQueueItem]:
        return sorted(
            [item for item in items if item.status == SETTLEMENT_REVIEW_STATUS_APPROVED],
            key=lambda item: item.review_id,
        )

    def list_rejected(self, items: List[SettlementReviewQueueItem]) -> List[SettlementReviewQueueItem]:
        return sorted(
            [item for item in items if item.status == SETTLEMENT_REVIEW_STATUS_REJECTED],
            key=lambda item: item.review_id,
        )

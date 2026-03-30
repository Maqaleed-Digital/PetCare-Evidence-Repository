from typing import Dict, List, Optional

from .settlement_review import SettlementReviewDecisionRecord, SettlementReviewQueueItem


class SettlementReviewRepository:
    def __init__(self) -> None:
        self._queue_items: Dict[str, SettlementReviewQueueItem] = {}
        self._decision_records: Dict[str, SettlementReviewDecisionRecord] = {}

    def save_queue_item(self, item: SettlementReviewQueueItem) -> SettlementReviewQueueItem:
        item.validate()
        self._queue_items[item.review_id] = item
        return item

    def get_queue_item(self, review_id: str) -> Optional[SettlementReviewQueueItem]:
        return self._queue_items.get(review_id)

    def get_queue_item_by_settlement_preparation_id(self, settlement_preparation_id: str) -> Optional[SettlementReviewQueueItem]:
        matches = [
            item
            for item in self._queue_items.values()
            if item.settlement_preparation_id == settlement_preparation_id
        ]
        matches.sort(key=lambda item: item.review_id)
        return matches[0] if matches else None

    def list_queue_items_for_partner(self, partner_id: str) -> List[SettlementReviewQueueItem]:
        return sorted(
            [item for item in self._queue_items.values() if item.partner_id == partner_id],
            key=lambda item: item.review_id,
        )

    def save_decision_record(self, record: SettlementReviewDecisionRecord) -> SettlementReviewDecisionRecord:
        record.validate()
        self._decision_records[record.decision_id] = record
        return record

    def get_decision_record_by_review_id(self, review_id: str) -> Optional[SettlementReviewDecisionRecord]:
        matches = [
            record
            for record in self._decision_records.values()
            if record.review_id == review_id
        ]
        matches.sort(key=lambda item: item.decision_id)
        return matches[0] if matches else None

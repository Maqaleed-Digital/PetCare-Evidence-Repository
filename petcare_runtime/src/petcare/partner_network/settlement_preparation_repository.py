from typing import Dict, List, Optional

from .settlement_preparation import SettlementPreparationRecord


class SettlementPreparationRepository:
    def __init__(self) -> None:
        self._records: Dict[str, SettlementPreparationRecord] = {}

    def save(self, record: SettlementPreparationRecord) -> SettlementPreparationRecord:
        record.validate()
        self._records[record.settlement_preparation_id] = record
        return record

    def get(self, settlement_preparation_id: str) -> Optional[SettlementPreparationRecord]:
        return self._records.get(settlement_preparation_id)

    def get_by_order_id(self, order_id: str) -> Optional[SettlementPreparationRecord]:
        matches = [record for record in self._records.values() if record.order_id == order_id]
        matches.sort(key=lambda item: item.settlement_preparation_id)
        return matches[0] if matches else None

    def list_for_partner(self, partner_id: str) -> List[SettlementPreparationRecord]:
        return sorted(
            [record for record in self._records.values() if record.partner_id == partner_id],
            key=lambda item: item.settlement_preparation_id,
        )

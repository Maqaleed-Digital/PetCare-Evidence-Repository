from typing import Dict, List, Optional

from .orders import StructuredOrder


class OrdersRepository:
    def __init__(self) -> None:
        self._orders: Dict[str, StructuredOrder] = {}

    def save(self, order: StructuredOrder) -> StructuredOrder:
        order.validate()
        self._orders[order.order_id] = order
        return order

    def get(self, order_id: str) -> Optional[StructuredOrder]:
        return self._orders.get(order_id)

    def list_for_partner(self, partner_id: str) -> List[StructuredOrder]:
        return sorted(
            [order for order in self._orders.values() if order.partner_id == partner_id],
            key=lambda item: item.order_id,
        )

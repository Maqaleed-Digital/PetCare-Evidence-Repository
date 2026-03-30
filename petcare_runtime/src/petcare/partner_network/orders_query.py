from typing import List

from .orders import StructuredOrder


class OrdersQuery:
    def list_by_status(self, orders: List[StructuredOrder], status: str) -> List[StructuredOrder]:
        return sorted(
            [order for order in orders if order.status == status],
            key=lambda item: item.order_id,
        )

    def list_routed_orders(self, orders: List[StructuredOrder]) -> List[StructuredOrder]:
        return sorted(
            [order for order in orders if order.route_partner_id is not None],
            key=lambda item: item.order_id,
        )

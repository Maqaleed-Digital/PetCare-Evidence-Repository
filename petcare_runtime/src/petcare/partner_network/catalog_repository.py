from __future__ import annotations

from typing import Dict, List

from petcare.partner_network.catalog import PartnerCatalogItem


class PartnerCatalogRepository:
    def __init__(self) -> None:
        self._items: Dict[str, PartnerCatalogItem] = {}

    def add_item(self, item: PartnerCatalogItem) -> None:
        self._items[item.catalog_item_id] = item

    def get_item(self, catalog_item_id: str) -> PartnerCatalogItem:
        return self._items[catalog_item_id]

    def list_items(self) -> List[PartnerCatalogItem]:
        return sorted(self._items.values(), key=lambda item: item.catalog_item_id)

    def list_items_by_partner(self, partner_id: str) -> List[PartnerCatalogItem]:
        return sorted(
            [item for item in self._items.values() if item.partner_id == partner_id],
            key=lambda item: item.catalog_item_id,
        )

    def list_items_by_status(self, status: str) -> List[PartnerCatalogItem]:
        return sorted(
            [item for item in self._items.values() if item.status == status],
            key=lambda item: item.catalog_item_id,
        )

    def list_items_by_category(self, normalized_category: str) -> List[PartnerCatalogItem]:
        return sorted(
            [item for item in self._items.values() if item.normalized_category == normalized_category],
            key=lambda item: item.catalog_item_id,
        )

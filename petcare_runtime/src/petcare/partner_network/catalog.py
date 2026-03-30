from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional


CATALOG_ITEM_TYPES = {
    "service",
    "product",
}

CATALOG_ITEM_STATUSES = {
    "draft",
    "normalized",
    "published",
    "suspended",
}

NORMALIZED_CATEGORIES = {
    "consultation",
    "emergency",
    "pharmacy",
    "diagnostics",
    "logistics",
    "wellness",
}


@dataclass(frozen=True)
class PartnerCatalogItem:
    catalog_item_id: str
    partner_id: str
    tenant_id: str
    item_type: str
    source_name: str
    normalized_name: str
    normalized_category: str
    status: str
    source_code: Optional[str]
    description: Optional[str]
    tags: List[str]
    created_at: str
    updated_at: str


def validate_item_type(item_type: str) -> None:
    if item_type not in CATALOG_ITEM_TYPES:
        raise ValueError("invalid item_type")


def validate_item_status(status: str) -> None:
    if status not in CATALOG_ITEM_STATUSES:
        raise ValueError("invalid item_status")


def validate_normalized_category(category: str) -> None:
    if category not in NORMALIZED_CATEGORIES:
        raise ValueError("invalid normalized_category")

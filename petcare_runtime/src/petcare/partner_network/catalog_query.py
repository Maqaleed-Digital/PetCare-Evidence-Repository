from __future__ import annotations

from typing import List

from petcare.partner_network.catalog import PartnerCatalogItem
from petcare.partner_network.catalog_repository import PartnerCatalogRepository


def get_partner_catalog(repo: PartnerCatalogRepository, partner_id: str) -> List[PartnerCatalogItem]:
    return repo.list_items_by_partner(partner_id)


def get_published_catalog_items(repo: PartnerCatalogRepository) -> List[PartnerCatalogItem]:
    return repo.list_items_by_status("published")


def get_catalog_items_by_category(
    repo: PartnerCatalogRepository,
    normalized_category: str,
) -> List[PartnerCatalogItem]:
    return repo.list_items_by_category(normalized_category)

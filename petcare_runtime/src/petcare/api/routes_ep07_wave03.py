from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter
from pydantic import BaseModel

from petcare.partner_network.catalog_repository import PartnerCatalogRepository
from petcare.partner_network.catalog_service import (
    ingest_catalog_item,
    transition_catalog_item_status,
)
from petcare.partner_network.catalog_query import (
    get_catalog_items_by_category,
    get_partner_catalog,
    get_published_catalog_items,
)

router = APIRouter(tags=["ep07-wave03"])

repo = PartnerCatalogRepository()


class CatalogItemCreateRequest(BaseModel):
    catalog_item_id: str
    partner_id: str
    tenant_id: str
    item_type: str
    source_name: str
    fallback_category: str
    source_code: Optional[str] = None
    description: Optional[str] = None
    tags: List[str]


class CatalogItemStateRequest(BaseModel):
    catalog_item_id: str
    new_status: str


@router.post("/ep07/catalog/items")
def create_catalog_item_api(payload: CatalogItemCreateRequest):
    item = ingest_catalog_item(
        repo=repo,
        catalog_item_id=payload.catalog_item_id,
        partner_id=payload.partner_id,
        tenant_id=payload.tenant_id,
        item_type=payload.item_type,
        source_name=payload.source_name,
        fallback_category=payload.fallback_category,
        source_code=payload.source_code,
        description=payload.description,
        tags=payload.tags,
    )
    return item.__dict__


@router.post("/ep07/catalog/items/state")
def update_catalog_item_state_api(payload: CatalogItemStateRequest):
    item = transition_catalog_item_status(
        repo=repo,
        catalog_item_id=payload.catalog_item_id,
        new_status=payload.new_status,
    )
    return item.__dict__


@router.get("/ep07/catalog/partners/{partner_id}")
def list_partner_catalog(partner_id: str):
    return [item.__dict__ for item in get_partner_catalog(repo, partner_id)]


@router.get("/ep07/catalog/published")
def list_published_catalog():
    return [item.__dict__ for item in get_published_catalog_items(repo)]


@router.get("/ep07/catalog/category/{normalized_category}")
def list_catalog_by_category(normalized_category: str):
    return [item.__dict__ for item in get_catalog_items_by_category(repo, normalized_category)]

from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from petcare.partner_network.catalog import (
    PartnerCatalogItem,
    validate_item_status,
    validate_item_type,
    validate_normalized_category,
)
from petcare.partner_network.catalog_repository import PartnerCatalogRepository


NORMALIZATION_MAP = {
    "emergency consultation": ("Emergency Consultation", "emergency"),
    "er consult": ("Emergency Consultation", "emergency"),
    "general consultation": ("General Consultation", "consultation"),
    "tele consultation": ("Tele Consultation", "consultation"),
    "blood test": ("Blood Test", "diagnostics"),
    "xray imaging": ("XRay Imaging", "diagnostics"),
    "cold chain delivery": ("Cold Chain Delivery", "logistics"),
    "medication dispensing": ("Medication Dispensing", "pharmacy"),
    "vaccination package": ("Vaccination Package", "wellness"),
}


def _now() -> str:
    return datetime.utcnow().isoformat() + "Z"


def _normalize_source_name(source_name: str) -> str:
    return " ".join(str(source_name).strip().lower().split())


def normalize_catalog_item(source_name: str, fallback_category: str) -> tuple[str, str]:
    normalized_source = _normalize_source_name(source_name)
    if normalized_source in NORMALIZATION_MAP:
        return NORMALIZATION_MAP[normalized_source]
    validate_normalized_category(fallback_category)
    return (str(source_name).strip().title(), fallback_category)


def ingest_catalog_item(
    repo: PartnerCatalogRepository,
    catalog_item_id: str,
    partner_id: str,
    tenant_id: str,
    item_type: str,
    source_name: str,
    fallback_category: str,
    source_code: Optional[str],
    description: Optional[str],
    tags: List[str],
) -> PartnerCatalogItem:
    validate_item_type(item_type)
    normalized_name, normalized_category = normalize_catalog_item(
        source_name=source_name,
        fallback_category=fallback_category,
    )

    item = PartnerCatalogItem(
        catalog_item_id=catalog_item_id,
        partner_id=partner_id,
        tenant_id=tenant_id,
        item_type=item_type,
        source_name=source_name,
        normalized_name=normalized_name,
        normalized_category=normalized_category,
        status="normalized",
        source_code=source_code,
        description=description,
        tags=sorted(set(str(tag).strip().lower() for tag in tags if str(tag).strip())),
        created_at=_now(),
        updated_at=_now(),
    )
    repo.add_item(item)
    return item


def transition_catalog_item_status(
    repo: PartnerCatalogRepository,
    catalog_item_id: str,
    new_status: str,
) -> PartnerCatalogItem:
    validate_item_status(new_status)
    current = repo.get_item(catalog_item_id)

    updated = PartnerCatalogItem(
        catalog_item_id=current.catalog_item_id,
        partner_id=current.partner_id,
        tenant_id=current.tenant_id,
        item_type=current.item_type,
        source_name=current.source_name,
        normalized_name=current.normalized_name,
        normalized_category=current.normalized_category,
        status=new_status,
        source_code=current.source_code,
        description=current.description,
        tags=list(current.tags),
        created_at=current.created_at,
        updated_at=_now(),
    )
    repo.add_item(updated)
    return updated

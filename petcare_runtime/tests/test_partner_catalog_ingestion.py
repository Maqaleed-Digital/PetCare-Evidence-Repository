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


def test_ingest_catalog_item_normalizes_known_name():
    repo = PartnerCatalogRepository()

    item = ingest_catalog_item(
        repo=repo,
        catalog_item_id="ci1",
        partner_id="p1",
        tenant_id="t1",
        item_type="service",
        source_name="ER Consult",
        fallback_category="consultation",
        source_code="SRC-001",
        description="Emergency partner consult",
        tags=["Urgent", "After Hours"],
    )

    assert item.catalog_item_id == "ci1"
    assert item.normalized_name == "Emergency Consultation"
    assert item.normalized_category == "emergency"
    assert item.status == "normalized"
    assert item.tags == ["after hours", "urgent"]


def test_ingest_catalog_item_uses_fallback_category_for_unknown_name():
    repo = PartnerCatalogRepository()

    item = ingest_catalog_item(
        repo=repo,
        catalog_item_id="ci2",
        partner_id="p2",
        tenant_id="t1",
        item_type="product",
        source_name="Custom Recovery Kit",
        fallback_category="wellness",
        source_code=None,
        description=None,
        tags=["kit"],
    )

    assert item.normalized_name == "Custom Recovery Kit"
    assert item.normalized_category == "wellness"


def test_transition_catalog_item_status_and_query_published():
    repo = PartnerCatalogRepository()

    ingest_catalog_item(
        repo=repo,
        catalog_item_id="ci3",
        partner_id="p3",
        tenant_id="t1",
        item_type="service",
        source_name="General Consultation",
        fallback_category="consultation",
        source_code="SRC-003",
        description="Routine consult",
        tags=["general"],
    )

    transition_catalog_item_status(repo, "ci3", "published")

    published_items = get_published_catalog_items(repo)

    assert len(published_items) == 1
    assert published_items[0].catalog_item_id == "ci3"
    assert published_items[0].status == "published"


def test_query_partner_catalog_and_category():
    repo = PartnerCatalogRepository()

    ingest_catalog_item(
        repo=repo,
        catalog_item_id="ci4",
        partner_id="p4",
        tenant_id="t1",
        item_type="service",
        source_name="Blood Test",
        fallback_category="diagnostics",
        source_code="SRC-004",
        description="Lab blood panel",
        tags=["lab"],
    )
    ingest_catalog_item(
        repo=repo,
        catalog_item_id="ci5",
        partner_id="p4",
        tenant_id="t1",
        item_type="product",
        source_name="Medication Dispensing",
        fallback_category="pharmacy",
        source_code="SRC-005",
        description="Dispensing workflow",
        tags=["medication"],
    )

    partner_items = get_partner_catalog(repo, "p4")
    diagnostics_items = get_catalog_items_by_category(repo, "diagnostics")

    assert [item.catalog_item_id for item in partner_items] == ["ci4", "ci5"]
    assert [item.catalog_item_id for item in diagnostics_items] == ["ci4"]


def test_invalid_catalog_status_rejected():
    repo = PartnerCatalogRepository()

    ingest_catalog_item(
        repo=repo,
        catalog_item_id="ci6",
        partner_id="p6",
        tenant_id="t1",
        item_type="service",
        source_name="Tele Consultation",
        fallback_category="consultation",
        source_code="SRC-006",
        description="Remote consult",
        tags=["remote"],
    )

    try:
        transition_catalog_item_status(repo, "ci6", "invalid_status")
        assert False
    except ValueError:
        assert True

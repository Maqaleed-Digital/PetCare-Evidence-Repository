BEGIN;

CREATE TABLE IF NOT EXISTS partner_catalog_items_wave03 (
    catalog_item_id TEXT PRIMARY KEY,
    partner_id TEXT NOT NULL,
    tenant_id TEXT NOT NULL,
    item_type TEXT NOT NULL,
    source_name TEXT NOT NULL,
    normalized_name TEXT NOT NULL,
    normalized_category TEXT NOT NULL,
    status TEXT NOT NULL,
    source_code TEXT NULL,
    description TEXT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS partner_catalog_item_tags_wave03 (
    catalog_item_id TEXT NOT NULL,
    tag_value TEXT NOT NULL,
    PRIMARY KEY (catalog_item_id, tag_value)
);

COMMIT;

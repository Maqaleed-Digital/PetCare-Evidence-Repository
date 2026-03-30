CREATE TABLE IF NOT EXISTS partner_pricing_rules (
    rule_id TEXT PRIMARY KEY,
    partner_id TEXT NOT NULL,
    catalog_item_id TEXT NOT NULL,
    base_price NUMERIC(12,2) NOT NULL CHECK (base_price >= 0),
    margin_percentage NUMERIC(5,2) NOT NULL DEFAULT 0 CHECK (margin_percentage >= 0 AND margin_percentage <= 100),
    promo_percentage NUMERIC(5,2) NOT NULL DEFAULT 0 CHECK (promo_percentage >= 0 AND promo_percentage <= 100),
    min_quantity INTEGER NOT NULL DEFAULT 1 CHECK (min_quantity >= 1),
    max_quantity INTEGER NULL,
    currency TEXT NOT NULL DEFAULT 'SAR',
    active BOOLEAN NOT NULL DEFAULT TRUE,
    ai_execution_authority BOOLEAN NOT NULL DEFAULT FALSE CHECK (ai_execution_authority = FALSE),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CHECK (max_quantity IS NULL OR max_quantity >= min_quantity)
);

CREATE INDEX IF NOT EXISTS idx_partner_pricing_rules_partner_catalog
ON partner_pricing_rules (partner_id, catalog_item_id, active);

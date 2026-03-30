CREATE TABLE IF NOT EXISTS partner_orders (
    order_id TEXT PRIMARY KEY,
    partner_id TEXT NOT NULL,
    catalog_item_id TEXT NOT NULL,
    quantity INTEGER NOT NULL CHECK (quantity >= 1),
    requested_by TEXT NOT NULL,
    pricing_rule_id TEXT NOT NULL,
    quoted_final_price NUMERIC(12,2) NOT NULL CHECK (quoted_final_price >= 0),
    currency TEXT NOT NULL DEFAULT 'SAR',
    status TEXT NOT NULL CHECK (status IN ('CREATED', 'VALIDATED', 'ROUTED')),
    route_partner_id TEXT NULL,
    route_reason TEXT NULL,
    decision_classification TEXT NOT NULL DEFAULT 'NON_AUTONOMOUS_DECISION',
    ai_execution_authority BOOLEAN NOT NULL DEFAULT FALSE CHECK (ai_execution_authority = FALSE),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_partner_orders_partner_status
ON partner_orders (partner_id, status);

-- 0050 · FR-15 smart order routing (MVC-BUILD-RUNNER-001 U18)
--
-- Ratified AC-FR-15-01 (OPTIMAL_ROUTING_RULE) and AC-FR-15-04 (each decision recorded with its inputs and the
-- chosen pharmacy). Pharmacy coordinates live on the location; establishment licences per supply class are a
-- governed register (MVC-PHARM-001 §6c) with no served write path. Decisions are insert-only. Additive only.

ALTER TABLE inventory_location ADD COLUMN IF NOT EXISTS latitude NUMERIC NULL;
ALTER TABLE inventory_location ADD COLUMN IF NOT EXISTS longitude NUMERIC NULL;

CREATE TABLE IF NOT EXISTS pharmacy_licence (
    location_id TEXT NOT NULL REFERENCES inventory_location(location_id),
    supply_class TEXT NOT NULL CHECK (supply_class IN ('GENERAL', 'OTC', 'POM', 'RESTRICTED', 'CONTROLLED')),
    source TEXT NOT NULL CHECK (length(TRIM(source)) > 0),
    PRIMARY KEY (location_id, supply_class)
);

CREATE TABLE IF NOT EXISTS routing_decision (
    decision_id TEXT PRIMARY KEY,
    order_id TEXT NOT NULL REFERENCES customer_order(order_id),
    tenant_id TEXT NOT NULL REFERENCES tenant(tenant_id),
    owner_latitude NUMERIC NOT NULL,
    owner_longitude NUMERIC NOT NULL,
    candidates JSONB NOT NULL CHECK (jsonb_typeof(candidates) = 'array' AND jsonb_array_length(candidates) > 0),
    chosen_location_id TEXT NULL REFERENCES inventory_location(location_id),
    rule_version TEXT NOT NULL,
    decided_by TEXT NOT NULL,
    decided_at TIMESTAMP NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_routing_decision_order ON routing_decision (tenant_id, order_id, decided_at);

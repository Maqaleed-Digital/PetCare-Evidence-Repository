-- 0041 · FR-13 multi-location inventory as an immutable movement ledger (MVC-BUILD-RUNNER-001 U8)
--
-- Ratified AC-FR-13-02: stock is an immutable movement ledger with a derived balance
-- (REQ-MVC-7.30). No table stores a quantity as authoritative mutable state; a balance
-- is only ever SUM(quantity_delta) over the movements for (location, product, batch).
-- UPDATE and DELETE on stock_movement are refused by the database itself, so no code
-- path can rewrite a movement. A correction is a new, compensating movement.
--
-- AC-FR-13-04 / MVC-PHARM-001 §5: supply class is taken from product registration
-- (AC-FR-04-03: never set by MyVetiCare or tenant staff; an unregistered product is
-- treated as POM). No served route writes product_registration. Each movement records
-- the class resolved at the moment of the act.
--
-- Additive only.

CREATE TABLE IF NOT EXISTS inventory_location (
    location_id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL REFERENCES tenant(tenant_id),
    name TEXT NOT NULL CHECK (length(TRIM(name)) > 0),
    created_at TIMESTAMP NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_inventory_location_tenant ON inventory_location (tenant_id);

CREATE TABLE IF NOT EXISTS product_registration (
    product_id TEXT PRIMARY KEY CHECK (length(TRIM(product_id)) > 0),
    name TEXT NOT NULL,
    supply_class TEXT NOT NULL
        CHECK (supply_class IN ('GENERAL', 'OTC', 'POM', 'RESTRICTED', 'CONTROLLED')),
    source TEXT NOT NULL CHECK (source IN ('SFDA_REGISTRATION')),
    registered_at TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS stock_movement (
    movement_id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL REFERENCES tenant(tenant_id),
    location_id TEXT NOT NULL REFERENCES inventory_location(location_id),
    product_id TEXT NOT NULL CHECK (length(TRIM(product_id)) > 0),
    batch TEXT NOT NULL CHECK (length(TRIM(batch)) > 0),
    quantity_delta INTEGER NOT NULL CHECK (quantity_delta <> 0),
    reason TEXT NOT NULL CHECK (reason IN ('RECEIPT', 'ADJUSTMENT', 'TRANSFER_OUT', 'TRANSFER_IN')),
    supply_class TEXT NOT NULL
        CHECK (supply_class IN ('GENERAL', 'OTC', 'POM', 'RESTRICTED', 'CONTROLLED')),
    transfer_id TEXT,
    actor_id TEXT NOT NULL CHECK (length(TRIM(actor_id)) > 0),
    actor_role TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL
);
-- AC-FR-13-03 (NFR-04 sub-second inventory check): balances are read per tenant and
-- per location; this index covers the filter and the grouping key.
CREATE INDEX IF NOT EXISTS idx_stock_movement_balance
    ON stock_movement (tenant_id, location_id, product_id, batch) INCLUDE (quantity_delta);
-- The inventory check for one product across the tenant's locations (FR-15 routing reads it).
CREATE INDEX IF NOT EXISTS idx_stock_movement_product
    ON stock_movement (tenant_id, product_id) INCLUDE (location_id, batch, quantity_delta);

CREATE OR REPLACE FUNCTION stock_movement_is_immutable() RETURNS trigger AS $$
BEGIN
    RAISE EXCEPTION 'stock_movement is an immutable ledger: % refused (AC-FR-13-02)', TG_OP
        USING ERRCODE = 'restrict_violation';
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS stock_movement_no_update_delete ON stock_movement;
CREATE TRIGGER stock_movement_no_update_delete
    BEFORE UPDATE OR DELETE ON stock_movement
    FOR EACH ROW EXECUTE FUNCTION stock_movement_is_immutable();

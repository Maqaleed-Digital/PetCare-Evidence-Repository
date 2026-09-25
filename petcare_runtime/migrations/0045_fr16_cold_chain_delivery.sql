-- 0045 · FR-16 temperature-controlled delivery tracking (MVC-BUILD-RUNNER-001 U12)
--
-- Ratified AC-FR-16-01/04. The storage requirement lives on the product registration (BRD P393; a
-- registration fact, never set by tenant staff). A delivery copies the range at creation. Readings,
-- alerts and completion are insert-only; an out-of-range reading is stored and flagged, never dropped.
-- Additive only.

ALTER TABLE product_registration ADD COLUMN IF NOT EXISTS storage_min_c NUMERIC NULL;
ALTER TABLE product_registration ADD COLUMN IF NOT EXISTS storage_max_c NUMERIC NULL;
ALTER TABLE product_registration DROP CONSTRAINT IF EXISTS product_registration_storage_range;
ALTER TABLE product_registration ADD CONSTRAINT product_registration_storage_range
    CHECK ((storage_min_c IS NULL) = (storage_max_c IS NULL) AND (storage_min_c IS NULL OR storage_min_c < storage_max_c));

CREATE TABLE IF NOT EXISTS delivery (
    delivery_id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL REFERENCES tenant(tenant_id),
    owner_id TEXT NOT NULL REFERENCES user_identity(user_id),
    product_id TEXT NOT NULL CHECK (length(TRIM(product_id)) > 0),
    created_by_actor_id TEXT NOT NULL CHECK (length(TRIM(created_by_actor_id)) > 0),
    created_at TIMESTAMP NOT NULL,
    temp_min_c NUMERIC NULL,
    temp_max_c NUMERIC NULL,
    CHECK ((temp_min_c IS NULL) = (temp_max_c IS NULL))
);
CREATE INDEX IF NOT EXISTS idx_delivery_tenant ON delivery (tenant_id, created_at);

CREATE TABLE IF NOT EXISTS temperature_reading (
    reading_id TEXT PRIMARY KEY,
    delivery_id TEXT NOT NULL REFERENCES delivery(delivery_id),
    tenant_id TEXT NOT NULL REFERENCES tenant(tenant_id),
    recorded_at TIMESTAMP NOT NULL,
    celsius NUMERIC NOT NULL,
    source TEXT NOT NULL CHECK (source IN ('STAFF', 'PARTNER')),
    recorded_by TEXT NOT NULL CHECK (length(TRIM(recorded_by)) > 0),
    out_of_range BOOLEAN NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_temperature_reading_delivery ON temperature_reading (tenant_id, delivery_id, recorded_at);

CREATE TABLE IF NOT EXISTS delivery_alert (
    alert_id TEXT PRIMARY KEY,
    delivery_id TEXT NOT NULL REFERENCES delivery(delivery_id),
    tenant_id TEXT NOT NULL REFERENCES tenant(tenant_id),
    reading_id TEXT NOT NULL UNIQUE REFERENCES temperature_reading(reading_id),
    kind TEXT NOT NULL CHECK (kind IN ('TEMPERATURE_OUT_OF_RANGE')),
    raised_at TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS delivery_completion (
    delivery_id TEXT PRIMARY KEY REFERENCES delivery(delivery_id),
    tenant_id TEXT NOT NULL REFERENCES tenant(tenant_id),
    completed_by_actor_id TEXT NOT NULL CHECK (length(TRIM(completed_by_actor_id)) > 0),
    completed_at TIMESTAMP NOT NULL
);

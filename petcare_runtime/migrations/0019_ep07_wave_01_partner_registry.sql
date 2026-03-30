BEGIN;

CREATE TABLE IF NOT EXISTS partner_registry_wave01 (
    partner_id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL,
    partner_type TEXT NOT NULL,
    verification_state TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

COMMIT;

-- 0046 · FR-19 batch tracking and recall notifications (MVC-BUILD-RUNNER-001 U13)
--
-- Ratified AC-FR-19-01: every stock movement and dispense records the batch (BRD P392 'batch_number,
-- expiry_date'); a receipt also records the batch expiry. Dispensing now draws from stock, so a dispense
-- IS a SUPPLY movement carrying the batch and the prescription (migration 0042).
-- Ratified AC-FR-19-02: a recall of (product, batch) resolves through stored relationships only
-- (SUPPLY movement -> prescription -> pet -> owner) and every resolved owner is notified. Insert-only.

ALTER TABLE stock_movement ADD COLUMN IF NOT EXISTS batch_expiry DATE NULL;

CREATE TABLE IF NOT EXISTS recall (
    recall_id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL REFERENCES tenant(tenant_id),
    product_id TEXT NOT NULL CHECK (length(TRIM(product_id)) > 0),
    batch TEXT NOT NULL CHECK (length(TRIM(batch)) > 0),
    reason TEXT NOT NULL CHECK (length(TRIM(reason)) > 0),
    source TEXT NOT NULL CHECK (source IN ('STAFF', 'SFDA')),
    initiated_by_actor_id TEXT NOT NULL CHECK (length(TRIM(initiated_by_actor_id)) > 0),
    created_at TIMESTAMP NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_recall_tenant ON recall (tenant_id, created_at);

CREATE TABLE IF NOT EXISTS recall_notification (
    notification_id TEXT PRIMARY KEY,
    recall_id TEXT NOT NULL REFERENCES recall(recall_id),
    tenant_id TEXT NOT NULL REFERENCES tenant(tenant_id),
    owner_id TEXT NOT NULL REFERENCES user_identity(user_id),
    movement_id TEXT NOT NULL REFERENCES stock_movement(movement_id),
    rendered_body TEXT NOT NULL CHECK (length(TRIM(rendered_body)) > 0),
    created_at TIMESTAMP NOT NULL,
    UNIQUE (recall_id, movement_id)
);
CREATE INDEX IF NOT EXISTS idx_recall_notification_owner ON recall_notification (tenant_id, owner_id);

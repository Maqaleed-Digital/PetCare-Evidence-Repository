CREATE TABLE IF NOT EXISTS partner_settlement_export_packages (
    export_package_id TEXT PRIMARY KEY,
    review_id TEXT NOT NULL UNIQUE,
    settlement_preparation_id TEXT NOT NULL,
    order_id TEXT NOT NULL,
    partner_id TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('PREPARED', 'HANDOFF_READY')),
    handoff_target TEXT NOT NULL,
    export_delivery_executed BOOLEAN NOT NULL DEFAULT FALSE CHECK (export_delivery_executed = FALSE),
    decision_classification TEXT NOT NULL DEFAULT 'NON_AUTONOMOUS_DECISION',
    ai_execution_authority BOOLEAN NOT NULL DEFAULT FALSE CHECK (ai_execution_authority = FALSE),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS partner_settlement_export_manifests (
    manifest_id TEXT PRIMARY KEY,
    export_package_id TEXT NOT NULL UNIQUE,
    review_id TEXT NOT NULL,
    settlement_preparation_id TEXT NOT NULL,
    order_id TEXT NOT NULL,
    partner_id TEXT NOT NULL,
    quoted_final_price NUMERIC(12,2) NOT NULL CHECK (quoted_final_price >= 0),
    currency TEXT NOT NULL DEFAULT 'SAR',
    manifest_version TEXT NOT NULL,
    human_approved BOOLEAN NOT NULL DEFAULT TRUE CHECK (human_approved = TRUE),
    handoff_only BOOLEAN NOT NULL DEFAULT TRUE CHECK (handoff_only = TRUE),
    decision_classification TEXT NOT NULL DEFAULT 'NON_AUTONOMOUS_DECISION',
    ai_execution_authority BOOLEAN NOT NULL DEFAULT FALSE CHECK (ai_execution_authority = FALSE),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_partner_settlement_export_packages_partner_status
ON partner_settlement_export_packages (partner_id, status);

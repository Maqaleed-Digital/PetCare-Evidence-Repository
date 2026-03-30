CREATE TABLE IF NOT EXISTS partner_settlement_preparation (
    settlement_preparation_id TEXT PRIMARY KEY,
    order_id TEXT NOT NULL UNIQUE,
    partner_id TEXT NOT NULL,
    pricing_rule_id TEXT NOT NULL,
    quoted_final_price NUMERIC(12,2) NOT NULL CHECK (quoted_final_price >= 0),
    currency TEXT NOT NULL DEFAULT 'SAR',
    execution_latest_event_type TEXT NULL,
    status TEXT NOT NULL CHECK (status IN ('DRAFT', 'READY_FOR_REVIEW', 'BLOCKED')),
    boundary_reason TEXT NOT NULL,
    export_status TEXT NOT NULL DEFAULT 'NOT_EXPORTED' CHECK (export_status = 'NOT_EXPORTED'),
    human_review_required BOOLEAN NOT NULL DEFAULT TRUE CHECK (human_review_required = TRUE),
    decision_classification TEXT NOT NULL DEFAULT 'NON_AUTONOMOUS_DECISION',
    ai_execution_authority BOOLEAN NOT NULL DEFAULT FALSE CHECK (ai_execution_authority = FALSE),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_partner_settlement_preparation_partner_status
ON partner_settlement_preparation (partner_id, status);

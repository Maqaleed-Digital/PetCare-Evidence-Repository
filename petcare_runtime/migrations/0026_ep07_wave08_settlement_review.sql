CREATE TABLE IF NOT EXISTS partner_settlement_review_queue (
    review_id TEXT PRIMARY KEY,
    settlement_preparation_id TEXT NOT NULL UNIQUE,
    order_id TEXT NOT NULL,
    partner_id TEXT NOT NULL,
    quoted_final_price NUMERIC(12,2) NOT NULL CHECK (quoted_final_price >= 0),
    currency TEXT NOT NULL DEFAULT 'SAR',
    status TEXT NOT NULL CHECK (status IN ('IN_QUEUE', 'APPROVED', 'REJECTED')),
    human_review_required BOOLEAN NOT NULL DEFAULT TRUE CHECK (human_review_required = TRUE),
    decision_classification TEXT NOT NULL DEFAULT 'NON_AUTONOMOUS_DECISION',
    ai_execution_authority BOOLEAN NOT NULL DEFAULT FALSE CHECK (ai_execution_authority = FALSE),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS partner_settlement_review_decisions (
    decision_id TEXT PRIMARY KEY,
    review_id TEXT NOT NULL UNIQUE,
    settlement_preparation_id TEXT NOT NULL,
    reviewer_id TEXT NOT NULL,
    decision TEXT NOT NULL CHECK (decision IN ('APPROVE', 'REJECT')),
    reason_code TEXT NOT NULL,
    notes TEXT NULL,
    queue_status_after_decision TEXT NOT NULL CHECK (queue_status_after_decision IN ('APPROVED', 'REJECTED')),
    human_review_required BOOLEAN NOT NULL DEFAULT TRUE CHECK (human_review_required = TRUE),
    decision_classification TEXT NOT NULL DEFAULT 'NON_AUTONOMOUS_DECISION',
    ai_execution_authority BOOLEAN NOT NULL DEFAULT FALSE CHECK (ai_execution_authority = FALSE),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_partner_settlement_review_queue_partner_status
ON partner_settlement_review_queue (partner_id, status);

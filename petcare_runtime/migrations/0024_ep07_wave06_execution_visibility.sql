CREATE TABLE IF NOT EXISTS partner_order_execution_events (
    event_id TEXT PRIMARY KEY,
    order_id TEXT NOT NULL,
    partner_id TEXT NOT NULL,
    event_type TEXT NOT NULL CHECK (event_type IN ('ACCEPTED', 'IN_PROGRESS', 'COMPLETED', 'FAILED')),
    recorded_by TEXT NOT NULL,
    notes TEXT NULL,
    sla_reference TEXT NULL,
    sequence_number INTEGER NOT NULL CHECK (sequence_number >= 1),
    decision_classification TEXT NOT NULL DEFAULT 'NON_AUTONOMOUS_DECISION',
    ai_execution_authority BOOLEAN NOT NULL DEFAULT FALSE CHECK (ai_execution_authority = FALSE),
    observational_only BOOLEAN NOT NULL DEFAULT TRUE CHECK (observational_only = TRUE),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_partner_order_execution_events_order_sequence
ON partner_order_execution_events (order_id, sequence_number);

CREATE INDEX IF NOT EXISTS idx_partner_order_execution_events_order_type
ON partner_order_execution_events (order_id, event_type);

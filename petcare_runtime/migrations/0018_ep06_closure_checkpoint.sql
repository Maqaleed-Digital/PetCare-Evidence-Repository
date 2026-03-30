BEGIN;

CREATE TABLE IF NOT EXISTS emergency_network_ep06_closure_checkpoint (
    checkpoint_id TEXT PRIMARY KEY,
    created_at TEXT NOT NULL,
    closure_status TEXT NOT NULL,
    decision_classification TEXT NOT NULL,
    notes TEXT NOT NULL
);

INSERT INTO emergency_network_ep06_closure_checkpoint (
    checkpoint_id,
    created_at,
    closure_status,
    decision_classification,
    notes
)
VALUES (
    'ep06-closure',
    '2026-03-30T00:00:00Z',
    'EP06_GOVERNED_CLOSED',
    'NON_AUTONOMOUS_DECISION',
    'EP-06 closure checkpoint for cross-wave emergency network integrity and assistive-only boundary verification'
)
ON CONFLICT (checkpoint_id) DO NOTHING;

COMMIT;

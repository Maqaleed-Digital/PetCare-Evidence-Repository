BEGIN;

CREATE TABLE IF NOT EXISTS emergency_referral_wave04_checkpoint (
    checkpoint_id TEXT PRIMARY KEY,
    created_at TEXT NOT NULL,
    package_status TEXT NOT NULL,
    decision_classification TEXT NOT NULL,
    notes TEXT NOT NULL
);

INSERT INTO emergency_referral_wave04_checkpoint (
    checkpoint_id,
    created_at,
    package_status,
    decision_classification,
    notes
)
VALUES (
    'ep06-wave04',
    '2026-03-30T00:00:00Z',
    'OPERATOR_REVIEW_REQUIRED',
    'NON_AUTONOMOUS_DECISION',
    'Emergency referral packaging checkpoint for pre-arrival packet and operator review surface'
)
ON CONFLICT (checkpoint_id) DO NOTHING;

COMMIT;

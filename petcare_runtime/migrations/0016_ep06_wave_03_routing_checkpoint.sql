BEGIN;

CREATE TABLE IF NOT EXISTS emergency_routing_wave03_checkpoint (
    checkpoint_id TEXT PRIMARY KEY,
    created_at TEXT NOT NULL,
    classification TEXT NOT NULL,
    notes TEXT NOT NULL
);

INSERT INTO emergency_routing_wave03_checkpoint (
    checkpoint_id,
    created_at,
    classification,
    notes
)
VALUES (
    'ep06-wave03',
    '2026-03-30T00:00:00Z',
    'NON_AUTONOMOUS_DECISION',
    'Emergency routing service checkpoint for deterministic explainable assistive routing'
)
ON CONFLICT (checkpoint_id) DO NOTHING;

COMMIT;

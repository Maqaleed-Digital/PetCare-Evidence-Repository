BEGIN;

CREATE TABLE IF NOT EXISTS partner_contracts_wave02 (
    contract_id TEXT PRIMARY KEY,
    partner_id TEXT NOT NULL,
    tenant_id TEXT NOT NULL,
    contract_state TEXT NOT NULL,
    effective_from TEXT NOT NULL,
    effective_to TEXT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS partner_slas_wave02 (
    sla_id TEXT PRIMARY KEY,
    contract_id TEXT NOT NULL,
    metric_type TEXT NOT NULL,
    target_value INTEGER NOT NULL,
    threshold_operator TEXT NOT NULL,
    monitoring_enabled INTEGER NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS partner_sla_breach_signals_wave02 (
    signal_id TEXT PRIMARY KEY,
    contract_id TEXT NOT NULL,
    sla_id TEXT NOT NULL,
    signal_state TEXT NOT NULL,
    observed_value INTEGER NOT NULL,
    target_value INTEGER NOT NULL,
    created_at TEXT NOT NULL,
    notes TEXT NOT NULL
);

COMMIT;

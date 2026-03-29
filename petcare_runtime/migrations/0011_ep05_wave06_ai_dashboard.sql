BEGIN;

CREATE TABLE IF NOT EXISTS ai_governance_dashboard_overview (
  tenant_id TEXT PRIMARY KEY,
  total_prompt_logs INTEGER NOT NULL,
  total_output_logs INTEGER NOT NULL,
  total_pending_gates INTEGER NOT NULL,
  total_approved_gates INTEGER NOT NULL,
  total_rejected_gates INTEGER NOT NULL,
  total_eval_runs INTEGER NOT NULL,
  total_drift_alerts INTEGER NOT NULL,
  total_ai_intake_records INTEGER NOT NULL,
  total_vet_copilot_records INTEGER NOT NULL,
  total_resolutions INTEGER NOT NULL,
  total_signoffs INTEGER NOT NULL,
  generated_at TEXT NOT NULL,
  ai_execution_authority INTEGER NOT NULL DEFAULT 0 CHECK (ai_execution_authority IN (0, 1))
);

CREATE TABLE IF NOT EXISTS ai_governance_operational_alerts (
  tenant_id TEXT NOT NULL,
  category TEXT NOT NULL,
  severity TEXT NOT NULL,
  reference_id TEXT NOT NULL,
  case_id TEXT NOT NULL,
  message TEXT NOT NULL,
  generated_at TEXT NOT NULL,
  ai_execution_authority INTEGER NOT NULL DEFAULT 0 CHECK (ai_execution_authority IN (0, 1))
);

CREATE INDEX IF NOT EXISTS idx_ai_governance_operational_alerts_tenant_id
  ON ai_governance_operational_alerts(tenant_id);
CREATE INDEX IF NOT EXISTS idx_ai_governance_operational_alerts_case_id
  ON ai_governance_operational_alerts(case_id);

CREATE TABLE IF NOT EXISTS ai_case_governance_views (
  tenant_id TEXT NOT NULL,
  case_id TEXT NOT NULL,
  prompt_log_ids TEXT NOT NULL DEFAULT '[]',
  output_log_ids TEXT NOT NULL DEFAULT '[]',
  gate_statuses TEXT NOT NULL DEFAULT '[]',
  runtime_artifact_ids TEXT NOT NULL DEFAULT '[]',
  resolution_ids TEXT NOT NULL DEFAULT '[]',
  signoff_ids TEXT NOT NULL DEFAULT '[]',
  latest_drift_alert_status TEXT NOT NULL,
  governance_state TEXT NOT NULL,
  generated_at TEXT NOT NULL,
  ai_execution_authority INTEGER NOT NULL DEFAULT 0 CHECK (ai_execution_authority IN (0, 1)),
  PRIMARY KEY (tenant_id, case_id)
);

COMMIT;

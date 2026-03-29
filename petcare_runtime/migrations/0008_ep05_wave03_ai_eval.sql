BEGIN;

CREATE TABLE IF NOT EXISTS ai_eval_cases (
  id TEXT PRIMARY KEY,
  species TEXT NOT NULL,
  symptom_cluster TEXT NOT NULL,
  context_type TEXT NOT NULL,
  expected_risk_flags TEXT NOT NULL DEFAULT '[]',
  expected_requires_approval INTEGER NOT NULL DEFAULT 0 CHECK (expected_requires_approval IN (0, 1)),
  expected_decision_class TEXT NOT NULL,
  status TEXT NOT NULL,
  created_at TEXT NOT NULL,
  ai_execution_authority INTEGER NOT NULL DEFAULT 0 CHECK (ai_execution_authority IN (0, 1))
);

CREATE INDEX IF NOT EXISTS idx_ai_eval_cases_species ON ai_eval_cases(species);
CREATE INDEX IF NOT EXISTS idx_ai_eval_cases_context_type ON ai_eval_cases(context_type);

CREATE TABLE IF NOT EXISTS ai_eval_runs (
  id TEXT PRIMARY KEY,
  suite_name TEXT NOT NULL,
  suite_version TEXT NOT NULL,
  model_name TEXT NOT NULL,
  model_version TEXT NOT NULL,
  provider TEXT NOT NULL,
  total_cases INTEGER NOT NULL,
  passed_cases INTEGER NOT NULL,
  pass_rate REAL NOT NULL,
  approval_alignment_rate REAL NOT NULL,
  risk_flag_alignment_rate REAL NOT NULL,
  regression_threshold_pass_rate REAL NOT NULL,
  status TEXT NOT NULL,
  created_at TEXT NOT NULL,
  ai_execution_authority INTEGER NOT NULL DEFAULT 0 CHECK (ai_execution_authority IN (0, 1))
);

CREATE INDEX IF NOT EXISTS idx_ai_eval_runs_model ON ai_eval_runs(provider, model_name, model_version);
CREATE INDEX IF NOT EXISTS idx_ai_eval_runs_created_at ON ai_eval_runs(created_at);

CREATE TABLE IF NOT EXISTS ai_drift_snapshots (
  id TEXT PRIMARY KEY,
  model_name TEXT NOT NULL,
  model_version TEXT NOT NULL,
  provider TEXT NOT NULL,
  baseline_pass_rate REAL NOT NULL,
  current_pass_rate REAL NOT NULL,
  baseline_approval_alignment_rate REAL NOT NULL,
  current_approval_alignment_rate REAL NOT NULL,
  baseline_risk_flag_alignment_rate REAL NOT NULL,
  current_risk_flag_alignment_rate REAL NOT NULL,
  pass_rate_delta REAL NOT NULL,
  approval_alignment_delta REAL NOT NULL,
  risk_flag_alignment_delta REAL NOT NULL,
  alert_status TEXT NOT NULL,
  thresholds TEXT NOT NULL,
  created_at TEXT NOT NULL,
  ai_execution_authority INTEGER NOT NULL DEFAULT 0 CHECK (ai_execution_authority IN (0, 1))
);

CREATE INDEX IF NOT EXISTS idx_ai_drift_snapshots_model ON ai_drift_snapshots(provider, model_name, model_version);
CREATE INDEX IF NOT EXISTS idx_ai_drift_snapshots_alert_status ON ai_drift_snapshots(alert_status);

COMMIT;

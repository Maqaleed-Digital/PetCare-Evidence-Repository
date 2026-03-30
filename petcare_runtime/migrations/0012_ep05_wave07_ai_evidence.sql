BEGIN;

CREATE TABLE IF NOT EXISTS ai_evidence_exports (
  id TEXT PRIMARY KEY,
  tenant_id TEXT NOT NULL,
  case_id TEXT NOT NULL,
  export_type TEXT NOT NULL,
  prompt_log_ids TEXT NOT NULL DEFAULT '[]',
  output_log_ids TEXT NOT NULL DEFAULT '[]',
  gate_ids TEXT NOT NULL DEFAULT '[]',
  runtime_artifact_ids TEXT NOT NULL DEFAULT '[]',
  resolution_ids TEXT NOT NULL DEFAULT '[]',
  signoff_ids TEXT NOT NULL DEFAULT '[]',
  report_id TEXT NOT NULL,
  manifest_hash TEXT NOT NULL,
  created_at TEXT NOT NULL,
  ai_execution_authority INTEGER NOT NULL DEFAULT 0 CHECK (ai_execution_authority IN (0, 1))
);

CREATE INDEX IF NOT EXISTS idx_ai_evidence_exports_case_id
  ON ai_evidence_exports(case_id);
CREATE INDEX IF NOT EXISTS idx_ai_evidence_exports_tenant_id
  ON ai_evidence_exports(tenant_id);

CREATE TABLE IF NOT EXISTS ai_governance_reports (
  id TEXT PRIMARY KEY,
  tenant_id TEXT NOT NULL,
  scope_type TEXT NOT NULL,
  scope_id TEXT NOT NULL,
  summary_counts TEXT NOT NULL,
  risk_summary TEXT NOT NULL,
  governance_state TEXT NOT NULL,
  report_hash TEXT NOT NULL,
  created_at TEXT NOT NULL,
  ai_execution_authority INTEGER NOT NULL DEFAULT 0 CHECK (ai_execution_authority IN (0, 1))
);

CREATE INDEX IF NOT EXISTS idx_ai_governance_reports_tenant_scope
  ON ai_governance_reports(tenant_id, scope_type, scope_id);

COMMIT;

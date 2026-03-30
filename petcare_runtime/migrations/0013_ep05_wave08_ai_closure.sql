BEGIN;

CREATE TABLE IF NOT EXISTS ai_ep_closure_checklists (
  tenant_id TEXT NOT NULL,
  epic_id TEXT NOT NULL,
  has_logging_foundation INTEGER NOT NULL DEFAULT 0 CHECK (has_logging_foundation IN (0, 1)),
  has_hitl_foundation INTEGER NOT NULL DEFAULT 0 CHECK (has_hitl_foundation IN (0, 1)),
  has_eval_foundation INTEGER NOT NULL DEFAULT 0 CHECK (has_eval_foundation IN (0, 1)),
  has_runtime_activation INTEGER NOT NULL DEFAULT 0 CHECK (has_runtime_activation IN (0, 1)),
  has_resolution_binding INTEGER NOT NULL DEFAULT 0 CHECK (has_resolution_binding IN (0, 1)),
  has_dashboard_read_models INTEGER NOT NULL DEFAULT 0 CHECK (has_dashboard_read_models IN (0, 1)),
  has_evidence_exports INTEGER NOT NULL DEFAULT 0 CHECK (has_evidence_exports IN (0, 1)),
  has_governance_reports INTEGER NOT NULL DEFAULT 0 CHECK (has_governance_reports IN (0, 1)),
  has_no_pending_gates INTEGER NOT NULL DEFAULT 0 CHECK (has_no_pending_gates IN (0, 1)),
  has_no_drift_alerts INTEGER NOT NULL DEFAULT 0 CHECK (has_no_drift_alerts IN (0, 1)),
  seal_ready INTEGER NOT NULL DEFAULT 0 CHECK (seal_ready IN (0, 1)),
  generated_at TEXT NOT NULL,
  ai_execution_authority INTEGER NOT NULL DEFAULT 0 CHECK (ai_execution_authority IN (0, 1)),
  PRIMARY KEY (tenant_id, epic_id)
);

CREATE TABLE IF NOT EXISTS ai_ep_governance_seals (
  id TEXT PRIMARY KEY,
  tenant_id TEXT NOT NULL,
  epic_id TEXT NOT NULL,
  seal_status TEXT NOT NULL,
  checklist_hash TEXT NOT NULL,
  source_commit TEXT NOT NULL,
  sealed_by TEXT NOT NULL,
  sealed_at TEXT NOT NULL,
  ai_execution_authority INTEGER NOT NULL DEFAULT 0 CHECK (ai_execution_authority IN (0, 1))
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_ai_ep_governance_seals_tenant_epic
  ON ai_ep_governance_seals(tenant_id, epic_id);

COMMIT;

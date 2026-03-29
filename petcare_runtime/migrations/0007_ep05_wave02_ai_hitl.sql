BEGIN;

CREATE TABLE IF NOT EXISTS ai_output_approval_gates (
  output_id TEXT PRIMARY KEY,
  prompt_id TEXT NOT NULL,
  case_id TEXT NOT NULL,
  tenant_id TEXT NOT NULL,
  context_type TEXT NOT NULL,
  decision_class TEXT NOT NULL,
  requires_approval INTEGER NOT NULL DEFAULT 0 CHECK (requires_approval IN (0, 1)),
  allowed_roles TEXT NOT NULL,
  status TEXT NOT NULL,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  ai_execution_authority INTEGER NOT NULL DEFAULT 0 CHECK (ai_execution_authority IN (0, 1)),
  FOREIGN KEY(output_id) REFERENCES output_logs(id),
  FOREIGN KEY(prompt_id) REFERENCES prompt_logs(id)
);

CREATE INDEX IF NOT EXISTS idx_ai_output_approval_gates_case_id ON ai_output_approval_gates(case_id);
CREATE INDEX IF NOT EXISTS idx_ai_output_approval_gates_tenant_id ON ai_output_approval_gates(tenant_id);

CREATE TABLE IF NOT EXISTS ai_output_approval_decisions (
  id TEXT PRIMARY KEY,
  output_id TEXT NOT NULL,
  decision TEXT NOT NULL,
  approver_id TEXT NOT NULL,
  approver_role TEXT NOT NULL,
  reason_code TEXT NOT NULL,
  notes TEXT NULL,
  decided_at TEXT NOT NULL,
  ai_execution_authority INTEGER NOT NULL DEFAULT 0 CHECK (ai_execution_authority IN (0, 1)),
  FOREIGN KEY(output_id) REFERENCES ai_output_approval_gates(output_id)
);

CREATE INDEX IF NOT EXISTS idx_ai_output_approval_decisions_output_id ON ai_output_approval_decisions(output_id);
CREATE INDEX IF NOT EXISTS idx_ai_output_approval_decisions_decided_at ON ai_output_approval_decisions(decided_at);

COMMIT;

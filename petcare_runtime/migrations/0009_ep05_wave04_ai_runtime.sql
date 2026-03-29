BEGIN;

CREATE TABLE IF NOT EXISTS ai_intake_records (
  id TEXT PRIMARY KEY,
  tenant_id TEXT NOT NULL,
  case_id TEXT NOT NULL,
  pet_id TEXT NULL,
  actor_id TEXT NOT NULL,
  actor_role TEXT NOT NULL,
  species TEXT NOT NULL,
  symptom_summary TEXT NOT NULL,
  urgency_level TEXT NOT NULL,
  red_flags TEXT NOT NULL DEFAULT '[]',
  structured_questions TEXT NOT NULL DEFAULT '[]',
  disclaimer TEXT NOT NULL,
  prompt_log_id TEXT NOT NULL,
  output_log_id TEXT NOT NULL,
  approval_gate_id TEXT NULL,
  hitl_required INTEGER NOT NULL DEFAULT 0 CHECK (hitl_required IN (0, 1)),
  status TEXT NOT NULL,
  created_at TEXT NOT NULL,
  ai_execution_authority INTEGER NOT NULL DEFAULT 0 CHECK (ai_execution_authority IN (0, 1)),
  FOREIGN KEY(prompt_log_id) REFERENCES prompt_logs(id),
  FOREIGN KEY(output_log_id) REFERENCES output_logs(id)
);

CREATE INDEX IF NOT EXISTS idx_ai_intake_records_case_id ON ai_intake_records(case_id);
CREATE INDEX IF NOT EXISTS idx_ai_intake_records_tenant_id ON ai_intake_records(tenant_id);

CREATE TABLE IF NOT EXISTS vet_copilot_draft_records (
  id TEXT PRIMARY KEY,
  tenant_id TEXT NOT NULL,
  case_id TEXT NOT NULL,
  pet_id TEXT NULL,
  actor_id TEXT NOT NULL,
  actor_role TEXT NOT NULL,
  soap_subjective TEXT NOT NULL,
  soap_objective TEXT NOT NULL,
  soap_assessment TEXT NOT NULL,
  soap_plan TEXT NOT NULL,
  protocol_citations TEXT NOT NULL DEFAULT '[]',
  uncertainty_note TEXT NOT NULL,
  disclaimer TEXT NOT NULL,
  prompt_log_id TEXT NOT NULL,
  output_log_id TEXT NOT NULL,
  approval_gate_id TEXT NULL,
  hitl_required INTEGER NOT NULL DEFAULT 0 CHECK (hitl_required IN (0, 1)),
  status TEXT NOT NULL,
  created_at TEXT NOT NULL,
  ai_execution_authority INTEGER NOT NULL DEFAULT 0 CHECK (ai_execution_authority IN (0, 1)),
  FOREIGN KEY(prompt_log_id) REFERENCES prompt_logs(id),
  FOREIGN KEY(output_log_id) REFERENCES output_logs(id)
);

CREATE INDEX IF NOT EXISTS idx_vet_copilot_draft_records_case_id ON vet_copilot_draft_records(case_id);
CREATE INDEX IF NOT EXISTS idx_vet_copilot_draft_records_tenant_id ON vet_copilot_draft_records(tenant_id);

COMMIT;

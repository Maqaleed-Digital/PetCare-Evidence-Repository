BEGIN;

CREATE TABLE IF NOT EXISTS ai_approval_resolutions (
  id TEXT PRIMARY KEY,
  tenant_id TEXT NOT NULL,
  case_id TEXT NOT NULL,
  artifact_type TEXT NOT NULL,
  artifact_id TEXT NOT NULL,
  output_id TEXT NOT NULL,
  gate_status TEXT NOT NULL,
  resolved_by TEXT NOT NULL,
  resolved_role TEXT NOT NULL,
  resolution_action TEXT NOT NULL,
  resolution_notes TEXT NULL,
  created_at TEXT NOT NULL,
  ai_execution_authority INTEGER NOT NULL DEFAULT 0 CHECK (ai_execution_authority IN (0, 1))
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_ai_approval_resolutions_artifact_unique
  ON ai_approval_resolutions(artifact_type, artifact_id);
CREATE INDEX IF NOT EXISTS idx_ai_approval_resolutions_case_id
  ON ai_approval_resolutions(case_id);
CREATE INDEX IF NOT EXISTS idx_ai_approval_resolutions_tenant_id
  ON ai_approval_resolutions(tenant_id);

CREATE TABLE IF NOT EXISTS ai_clinical_signoff_bindings (
  id TEXT PRIMARY KEY,
  tenant_id TEXT NOT NULL,
  case_id TEXT NOT NULL,
  artifact_type TEXT NOT NULL,
  artifact_id TEXT NOT NULL,
  veterinarian_id TEXT NOT NULL,
  veterinarian_role TEXT NOT NULL,
  final_note_hash TEXT NOT NULL,
  signoff_status TEXT NOT NULL,
  signed_at TEXT NOT NULL,
  immutable_after_signoff INTEGER NOT NULL DEFAULT 1 CHECK (immutable_after_signoff IN (0, 1)),
  ai_execution_authority INTEGER NOT NULL DEFAULT 0 CHECK (ai_execution_authority IN (0, 1))
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_ai_clinical_signoff_bindings_artifact_unique
  ON ai_clinical_signoff_bindings(artifact_type, artifact_id);
CREATE INDEX IF NOT EXISTS idx_ai_clinical_signoff_bindings_case_id
  ON ai_clinical_signoff_bindings(case_id);
CREATE INDEX IF NOT EXISTS idx_ai_clinical_signoff_bindings_tenant_id
  ON ai_clinical_signoff_bindings(tenant_id);

COMMIT;

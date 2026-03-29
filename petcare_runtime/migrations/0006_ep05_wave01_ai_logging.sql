BEGIN;

CREATE TABLE IF NOT EXISTS prompt_logs (
  id TEXT PRIMARY KEY,
  timestamp TEXT NOT NULL,
  actor_id TEXT NOT NULL,
  actor_role TEXT NOT NULL,
  tenant_id TEXT NOT NULL,
  case_id TEXT NOT NULL,
  pet_id TEXT NULL,
  prompt_text TEXT NOT NULL,
  prompt_hash TEXT NOT NULL,
  model_name TEXT NOT NULL,
  model_version TEXT NOT NULL,
  provider TEXT NOT NULL,
  context_type TEXT NOT NULL,
  created_by_service TEXT NOT NULL DEFAULT 'petcare.ai_logging',
  ai_execution_authority INTEGER NOT NULL DEFAULT 0 CHECK (ai_execution_authority IN (0, 1))
);

CREATE INDEX IF NOT EXISTS idx_prompt_logs_case_id ON prompt_logs(case_id);
CREATE INDEX IF NOT EXISTS idx_prompt_logs_tenant_id ON prompt_logs(tenant_id);
CREATE INDEX IF NOT EXISTS idx_prompt_logs_timestamp ON prompt_logs(timestamp);

CREATE TABLE IF NOT EXISTS output_logs (
  id TEXT PRIMARY KEY,
  prompt_id TEXT NOT NULL,
  timestamp TEXT NOT NULL,
  output_text TEXT NOT NULL,
  output_hash TEXT NOT NULL,
  confidence REAL NULL,
  risk_flags TEXT NOT NULL DEFAULT '[]',
  requires_approval INTEGER NOT NULL DEFAULT 0 CHECK (requires_approval IN (0, 1)),
  approved_by TEXT NULL,
  approved_at TEXT NULL,
  created_by_service TEXT NOT NULL DEFAULT 'petcare.ai_logging',
  ai_execution_authority INTEGER NOT NULL DEFAULT 0 CHECK (ai_execution_authority IN (0, 1)),
  FOREIGN KEY(prompt_id) REFERENCES prompt_logs(id)
);

CREATE INDEX IF NOT EXISTS idx_output_logs_prompt_id ON output_logs(prompt_id);
CREATE INDEX IF NOT EXISTS idx_output_logs_timestamp ON output_logs(timestamp);

CREATE TABLE IF NOT EXISTS model_registry (
  model_name TEXT NOT NULL,
  model_version TEXT NOT NULL,
  provider TEXT NOT NULL,
  status TEXT NOT NULL,
  safety_level TEXT NOT NULL,
  registered_at TEXT NOT NULL,
  PRIMARY KEY (provider, model_name, model_version)
);

COMMIT;

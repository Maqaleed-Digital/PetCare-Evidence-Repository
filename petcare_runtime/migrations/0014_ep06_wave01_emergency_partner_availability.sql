BEGIN;

CREATE TABLE IF NOT EXISTS emergency_partner_availability (
  id TEXT PRIMARY KEY,
  tenant_id TEXT NOT NULL,
  partner_clinic_id TEXT NOT NULL,
  clinic_name TEXT NOT NULL,
  city TEXT NOT NULL,
  open_status TEXT NOT NULL,
  capacity_status TEXT NOT NULL,
  emergency_ready INTEGER NOT NULL DEFAULT 0 CHECK (emergency_ready IN (0, 1)),
  estimated_eta_minutes INTEGER NOT NULL CHECK (estimated_eta_minutes >= 0),
  failover_eligible INTEGER NOT NULL DEFAULT 0 CHECK (failover_eligible IN (0, 1)),
  on_call_vet_available INTEGER NOT NULL DEFAULT 0 CHECK (on_call_vet_available IN (0, 1)),
  accepts_walk_in_emergency INTEGER NOT NULL DEFAULT 0 CHECK (accepts_walk_in_emergency IN (0, 1)),
  operational_notes TEXT NULL,
  last_updated_at TEXT NOT NULL,
  ai_execution_authority INTEGER NOT NULL DEFAULT 0 CHECK (ai_execution_authority IN (0, 1))
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_emergency_partner_availability_tenant_partner
  ON emergency_partner_availability(tenant_id, partner_clinic_id);

CREATE INDEX IF NOT EXISTS idx_emergency_partner_availability_tenant
  ON emergency_partner_availability(tenant_id);

CREATE INDEX IF NOT EXISTS idx_emergency_partner_availability_ready
  ON emergency_partner_availability(tenant_id, emergency_ready, open_status, capacity_status);

COMMIT;

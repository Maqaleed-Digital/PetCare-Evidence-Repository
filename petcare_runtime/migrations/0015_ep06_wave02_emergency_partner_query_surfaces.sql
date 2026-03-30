BEGIN;

CREATE TABLE IF NOT EXISTS emergency_partner_availability_query_surface (
  tenant_id TEXT NOT NULL,
  partner_clinic_id TEXT NOT NULL,
  city TEXT NOT NULL,
  open_status TEXT NOT NULL,
  capacity_status TEXT NOT NULL,
  emergency_ready INTEGER NOT NULL DEFAULT 0 CHECK (emergency_ready IN (0, 1)),
  failover_eligible INTEGER NOT NULL DEFAULT 0 CHECK (failover_eligible IN (0, 1)),
  on_call_vet_available INTEGER NOT NULL DEFAULT 0 CHECK (on_call_vet_available IN (0, 1)),
  accepts_walk_in_emergency INTEGER NOT NULL DEFAULT 0 CHECK (accepts_walk_in_emergency IN (0, 1)),
  estimated_eta_minutes INTEGER NOT NULL CHECK (estimated_eta_minutes >= 0),
  ai_execution_authority INTEGER NOT NULL DEFAULT 0 CHECK (ai_execution_authority IN (0, 1)),
  PRIMARY KEY (tenant_id, partner_clinic_id)
);

CREATE INDEX IF NOT EXISTS idx_emergency_partner_query_surface_city
  ON emergency_partner_availability_query_surface(tenant_id, city);

CREATE INDEX IF NOT EXISTS idx_emergency_partner_query_surface_failover
  ON emergency_partner_availability_query_surface(
    tenant_id,
    emergency_ready,
    failover_eligible,
    on_call_vet_available,
    accepts_walk_in_emergency,
    estimated_eta_minutes
  );

COMMIT;

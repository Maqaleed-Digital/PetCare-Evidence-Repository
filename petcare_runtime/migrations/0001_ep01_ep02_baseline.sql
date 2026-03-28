CREATE TABLE pet (
  pet_id TEXT PRIMARY KEY,
  tenant_id TEXT NOT NULL,
  owner_id TEXT NOT NULL,
  clinic_id_nullable TEXT,
  name TEXT NOT NULL,
  species TEXT NOT NULL,
  breed_nullable TEXT,
  sex_nullable TEXT,
  birth_date_nullable TEXT,
  weight_latest_nullable REAL,
  status TEXT NOT NULL,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);

CREATE TABLE consent_record (
  consent_record_id TEXT PRIMARY KEY,
  pet_id TEXT NOT NULL,
  owner_id TEXT NOT NULL,
  consent_scope TEXT NOT NULL,
  purpose_of_use TEXT NOT NULL,
  granted_to_role TEXT NOT NULL,
  status TEXT NOT NULL,
  granted_at TEXT NOT NULL,
  revoked_at_nullable TEXT,
  captured_by_actor_id TEXT NOT NULL,
  audit_reference_id TEXT NOT NULL
);

CREATE TABLE audit_event (
  audit_event_id TEXT PRIMARY KEY,
  event_name TEXT NOT NULL,
  actor_id TEXT NOT NULL,
  actor_role TEXT NOT NULL,
  tenant_id TEXT NOT NULL,
  clinic_id_nullable TEXT,
  resource_type TEXT NOT NULL,
  resource_id TEXT NOT NULL,
  action_result TEXT NOT NULL,
  reason_code_nullable TEXT,
  correlation_id TEXT NOT NULL,
  occurred_at TEXT NOT NULL
);

CREATE TABLE allergy_record (
  allergy_record_id TEXT PRIMARY KEY,
  pet_id TEXT NOT NULL,
  allergen TEXT NOT NULL,
  severity TEXT NOT NULL,
  reaction_nullable TEXT,
  status TEXT NOT NULL,
  recorded_by_actor_id TEXT NOT NULL,
  recorded_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  version_no INTEGER NOT NULL
);

CREATE TABLE medication_record (
  medication_record_id TEXT PRIMARY KEY,
  pet_id TEXT NOT NULL,
  medication_name TEXT NOT NULL,
  medication_type_nullable TEXT,
  dose_nullable TEXT,
  dose_unit_nullable TEXT,
  route_nullable TEXT,
  frequency_nullable TEXT,
  start_date_nullable TEXT,
  end_date_nullable TEXT,
  status TEXT NOT NULL,
  prescribed_by_actor_id_nullable TEXT,
  recorded_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  version_no INTEGER NOT NULL
);

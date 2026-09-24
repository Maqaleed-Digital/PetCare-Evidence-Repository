-- 0037 · FR-02 pet profile persistence (MVC-BUILD-RUNNER-001 U2)
--
-- Ratified criteria AC-FR-02-01/02/03 (MVC-ACCEPT-PACK-P1). The pet profile
-- moves off the node-local UPHR JSON file onto the governed store. Additive only:
-- three new tables, no change to any existing table, no destructive statement.
--
-- Every row carries tenant_id and references `tenant`, so a profile cannot exist
-- in an unregistered scope (TENANT-05) and every read can be tenant-predicated.

CREATE TABLE IF NOT EXISTS pet_profile (
    pet_id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL REFERENCES tenant(tenant_id),
    owner_id TEXT NOT NULL CHECK (length(TRIM(owner_id)) > 0),
    name TEXT NOT NULL CHECK (length(TRIM(name)) > 0),
    species TEXT NOT NULL CHECK (length(TRIM(species)) > 0),
    breed TEXT NULL,
    birth_date DATE NULL,
    weight_kg NUMERIC(7, 3) NULL CHECK (weight_kg IS NULL OR weight_kg > 0),
    medical_conditions TEXT NULL,
    allergies TEXT NULL,
    preferences TEXT NULL,
    created_by_actor_id TEXT NOT NULL CHECK (length(TRIM(created_by_actor_id)) > 0),
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL,
    CHECK (updated_at >= created_at)
);

CREATE INDEX IF NOT EXISTS idx_pet_profile_tenant_owner
    ON pet_profile (tenant_id, owner_id);

-- Structured animal identification (AC-FR-02-03, REQ-MVC-6.10). Optional: a pet
-- may have none — no unsourced obligation makes it mandatory. Never free text on
-- the profile.
CREATE TABLE IF NOT EXISTS pet_identification (
    identification_id TEXT PRIMARY KEY,
    pet_id TEXT NOT NULL REFERENCES pet_profile(pet_id),
    tenant_id TEXT NOT NULL REFERENCES tenant(tenant_id),
    id_type TEXT NOT NULL CHECK (id_type IN ('MICROCHIP', 'TATTOO', 'OTHER')),
    id_value TEXT NOT NULL CHECK (length(TRIM(id_value)) > 0),
    issuing_scheme TEXT NULL,
    captured_at DATE NOT NULL,
    capture_method TEXT NOT NULL CHECK (length(TRIM(capture_method)) > 0),
    recorded_by_actor_id TEXT NOT NULL CHECK (length(TRIM(recorded_by_actor_id)) > 0),
    recorded_at TIMESTAMP NOT NULL,
    CHECK (id_type <> 'OTHER' OR length(TRIM(COALESCE(issuing_scheme, ''))) > 0)
);

CREATE INDEX IF NOT EXISTS idx_pet_identification_tenant_pet
    ON pet_identification (tenant_id, pet_id);

-- Medical history held on the profile: lab results and clinical records
-- (AC-FR-02-02). Prescriptions are NOT duplicated here; they are read from
-- `prescription`, their single source of truth.
CREATE TABLE IF NOT EXISTS pet_medical_record (
    record_id TEXT PRIMARY KEY,
    pet_id TEXT NOT NULL REFERENCES pet_profile(pet_id),
    tenant_id TEXT NOT NULL REFERENCES tenant(tenant_id),
    record_type TEXT NOT NULL CHECK (record_type IN ('LAB_RESULT', 'CLINICAL_RECORD')),
    title TEXT NOT NULL CHECK (length(TRIM(title)) > 0),
    detail TEXT NULL,
    recorded_by_actor_id TEXT NOT NULL CHECK (length(TRIM(recorded_by_actor_id)) > 0),
    recorded_at TIMESTAMP NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_pet_medical_record_tenant_pet
    ON pet_medical_record (tenant_id, pet_id);

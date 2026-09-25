-- 0044 · FR-06 durable consultation record and the telemedicine counsel gate (MVC-BUILD-RUNNER-001 U11)
--
-- Ratified AC-FR-06-04: the consultation, its participants and its outcome are persisted and
-- audited within the owner's tenant. Both records are insert-only; status is derived.
-- Ratified AC-FR-06-05 (COUNSEL:REG-02_TELEMEDICINE): remote consultation is fail-closed until a
-- counsel determination is RECORDED in regulatory_determination. No served route writes that
-- table; recording it is a governed counsel/Sponsor act. Additive only.

CREATE TABLE IF NOT EXISTS consultation (
    session_id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL REFERENCES tenant(tenant_id),
    pet_id TEXT NOT NULL CHECK (length(TRIM(pet_id)) > 0),
    owner_id TEXT NOT NULL REFERENCES user_identity(user_id),
    veterinarian_id TEXT NOT NULL REFERENCES user_identity(user_id),
    requested_by_actor_id TEXT NOT NULL CHECK (length(TRIM(requested_by_actor_id)) > 0),
    mode TEXT NOT NULL CHECK (mode IN ('IN_PERSON', 'REMOTE_VIDEO')),
    clinic_id TEXT NULL,
    created_at TIMESTAMP NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_consultation_tenant ON consultation (tenant_id, created_at);

CREATE TABLE IF NOT EXISTS consultation_outcome (
    session_id TEXT PRIMARY KEY REFERENCES consultation(session_id),
    tenant_id TEXT NOT NULL REFERENCES tenant(tenant_id),
    outcome TEXT NOT NULL CHECK (length(TRIM(outcome)) > 0),
    recorded_by_actor_id TEXT NOT NULL CHECK (length(TRIM(recorded_by_actor_id)) > 0),
    recorded_at TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS regulatory_determination (
    determination_id TEXT PRIMARY KEY,
    subject TEXT NOT NULL CHECK (subject IN ('REG-02_TELEMEDICINE')),
    decision TEXT NOT NULL CHECK (decision IN ('LAWFUL', 'NOT_LAWFUL')),
    form TEXT NOT NULL,
    reference TEXT NOT NULL CHECK (length(TRIM(reference)) > 0),
    recorded_by TEXT NOT NULL CHECK (length(TRIM(recorded_by)) > 0),
    recorded_at TIMESTAMP NOT NULL
);

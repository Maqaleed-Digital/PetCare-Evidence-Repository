-- 0043 · FR-05 veterinarian licence registration and verification (MVC-BUILD-RUNNER-001 U10)
--
-- Ratified AC-FR-05-01/02. A licence is submitted with the registration and is immutable; its
-- verification is a separate immutable record that NAMES the verifier, the time, the method and
-- what it was checked against. The database refuses a verification without them. Verification
-- mints the time-bounded practitioner_authority_grant (migration 0039) that expires with the
-- licence and is evaluated at every clinical act. Additive only.

CREATE TABLE IF NOT EXISTS vet_licence (
    licence_id TEXT PRIMARY KEY,
    actor_id TEXT NOT NULL REFERENCES user_identity(user_id),
    licence_number TEXT NOT NULL CHECK (length(TRIM(licence_number)) > 0),
    issuing_authority TEXT NOT NULL CHECK (length(TRIM(issuing_authority)) > 0),
    expires_on DATE NOT NULL,
    submitted_at TIMESTAMP NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_vet_licence_actor ON vet_licence (actor_id);

CREATE TABLE IF NOT EXISTS vet_licence_verification (
    verification_id TEXT PRIMARY KEY,
    licence_id TEXT NOT NULL UNIQUE REFERENCES vet_licence(licence_id),
    tenant_id TEXT NOT NULL REFERENCES tenant(tenant_id),
    verified_by_actor_id TEXT NOT NULL CHECK (length(TRIM(verified_by_actor_id)) > 0),
    verified_at TIMESTAMP NOT NULL,
    method TEXT NOT NULL CHECK (method IN ('MANUAL_STAFF', 'AUTHORITY_LOOKUP')),
    basis TEXT NOT NULL CHECK (length(TRIM(basis)) > 0),
    grant_id TEXT NOT NULL REFERENCES practitioner_authority_grant(grant_id)
);

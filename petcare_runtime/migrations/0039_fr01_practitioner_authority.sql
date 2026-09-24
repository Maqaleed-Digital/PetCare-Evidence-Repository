-- 0039 · FR-01 live practitioner authority attribute (MVC-BUILD-RUNNER-001 U5)
--
-- Ratified criterion AC-FR-01-02 (REQ-MVC-8.32): every regulated act (prescribing,
-- dispensing) is authorised by a live practitioner authority attribute evaluated at
-- the moment of the act, in addition to role and tenant membership. Authority is
-- time-bounded, never a boolean: a revoked or expired grant must not retroactively
-- look as if it never existed, nor a new one as if it always had. Additive only.

CREATE TABLE IF NOT EXISTS practitioner_authority_grant (
    grant_id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL REFERENCES tenant(tenant_id),
    actor_id TEXT NOT NULL REFERENCES user_identity(user_id),
    professional_class TEXT NOT NULL CHECK (professional_class IN ('VETERINARIAN')),
    licence_ref TEXT NOT NULL CHECK (length(TRIM(licence_ref)) > 0),
    effective_from TIMESTAMP NOT NULL,
    expires_at TIMESTAMP NULL,
    revoked_at TIMESTAMP NULL,
    granted_by_actor_id TEXT NOT NULL CHECK (length(TRIM(granted_by_actor_id)) > 0),
    granted_at TIMESTAMP NOT NULL,
    revoked_by_actor_id TEXT NULL,
    CHECK (expires_at IS NULL OR expires_at > effective_from),
    CHECK ((revoked_at IS NULL) = (revoked_by_actor_id IS NULL))
);

CREATE INDEX IF NOT EXISTS idx_practitioner_authority_actor
    ON practitioner_authority_grant (tenant_id, actor_id);

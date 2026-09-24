-- 0038 · FR-09 language preference that survives a new session (MVC-BUILD-RUNNER-001 U3)
--
-- Ratified criterion AC-FR-09-02: "the persistent language choice survives a new
-- session". The choice is held server-side against the identity, so a sign-in on
-- a fresh device restores it. Additive only: one new table, no existing table
-- touched. Arabic is the default when no row exists (FR-09: Arabic primary).

CREATE TABLE IF NOT EXISTS user_preference (
    user_id TEXT PRIMARY KEY REFERENCES user_identity(user_id),
    tenant_id TEXT NOT NULL REFERENCES tenant(tenant_id),
    language TEXT NOT NULL CHECK (language IN ('ar', 'en')),
    updated_at TIMESTAMP NOT NULL
);

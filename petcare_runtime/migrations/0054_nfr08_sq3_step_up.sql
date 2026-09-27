-- 0054 · NFR-08 under Sponsor act SQ-3 (MVC-SQ3-NFR08-STEP-UP-001; MVC-BUILD-RUNNER-001 v1.3 U28)
--
-- Additive only. A step-up now records whether it has authorized an operation (an always-fresh operation needs one
-- that has not) and whether it came from a recovery code (authorizes exactly one operation). Recovery codes are stored
-- ONLY as a salted SHA-256 digest; a code is used at most once (used_at set by an atomic UPDATE). An assisted reset
-- is a request by one tenant admin approved once by a second.

ALTER TABLE mfa_step_up ADD COLUMN IF NOT EXISTS single_use BOOLEAN NOT NULL DEFAULT FALSE;
ALTER TABLE mfa_step_up ADD COLUMN IF NOT EXISTS used BOOLEAN NOT NULL DEFAULT FALSE;

CREATE TABLE IF NOT EXISTS mfa_recovery_code (
    code_id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL REFERENCES user_identity(user_id),
    salt BYTEA NOT NULL CHECK (length(salt) = 16),
    digest BYTEA NOT NULL CHECK (length(digest) = 32),
    used_at TIMESTAMP NULL
);
CREATE INDEX IF NOT EXISTS mfa_recovery_code_user ON mfa_recovery_code (user_id);

CREATE TABLE IF NOT EXISTS mfa_reset_request (
    reset_id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL REFERENCES tenant(tenant_id),
    subject_user_id TEXT NOT NULL REFERENCES user_identity(user_id),
    requested_by TEXT NOT NULL REFERENCES user_identity(user_id),
    requested_at TIMESTAMP NOT NULL,
    approved_by TEXT NULL REFERENCES user_identity(user_id),
    approved_at TIMESTAMP NULL,
    CHECK (requested_by <> subject_user_id),
    CHECK (approved_by IS NULL OR (approved_by <> subject_user_id AND approved_by <> requested_by))
);

-- 0056 · Owner self-registration, email verification, password reset (MVC-EPC-D-001 Lane D, D2; Sponsor ruling 1:
-- built fully behind PETCARE_OWNER_SELF_REGISTRATION, production default OFF). Additive only.
--
-- email_verification: an identity with a row here must verify its address before it may sign in (self-registered
-- owners). Seeded and invited identities have no row and are unaffected.
-- account_token: one-time tokens, stored ONLY as sha256; single use (used_at set once), time-limited.

CREATE TABLE IF NOT EXISTS email_verification (
    user_id TEXT PRIMARY KEY REFERENCES user_identity(user_id),
    required_since TIMESTAMP NOT NULL,
    verified_at TIMESTAMP NULL
);

CREATE TABLE IF NOT EXISTS account_token (
    token_sha256 TEXT PRIMARY KEY CHECK (token_sha256 ~ '^[0-9a-f]{64}$'),
    user_id TEXT NOT NULL REFERENCES user_identity(user_id),
    purpose TEXT NOT NULL CHECK (purpose IN ('EMAIL_VERIFICATION', 'PASSWORD_RESET')),
    created_at TIMESTAMP NOT NULL,
    expires_at TIMESTAMP NOT NULL CHECK (expires_at > created_at),
    used_at TIMESTAMP NULL
);
CREATE INDEX IF NOT EXISTS account_token_user ON account_token (user_id, purpose);

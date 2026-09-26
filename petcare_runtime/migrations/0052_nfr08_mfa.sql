-- 0052 · NFR-08 MFA step-up mechanism (MVC-BUILD-RUNNER-001 v1.2 U25)
--
-- The TOTP secret is stored ONLY as AES-256-GCM ciphertext (key from the governed secret provider). last_used_step
-- makes every code single-use. A step-up is bound to one server-side session. Additive only.

CREATE TABLE IF NOT EXISTS mfa_factor (
    user_id TEXT PRIMARY KEY REFERENCES user_identity(user_id),
    nonce BYTEA NOT NULL CHECK (length(nonce) = 12),
    ciphertext BYTEA NOT NULL CHECK (length(ciphertext) > 16),
    created_at TIMESTAMP NOT NULL,
    confirmed_at TIMESTAMP NULL,
    last_used_step BIGINT NULL
);

CREATE TABLE IF NOT EXISTS mfa_step_up (
    session_id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL REFERENCES user_identity(user_id),
    verified_at TIMESTAMP NOT NULL
);

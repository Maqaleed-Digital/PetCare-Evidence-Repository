-- 0053 · SQ-1 platform identity audit chain (Sponsor act MVC-SQ1-PLATFORM-IDENTITY-AUDIT-001; v1.2 U26)
--
-- Pre-tenant identity/security events (registration, failed sign-in) are chained HERE — a separate chain with its
-- own head, the same hashing as audit_event, and NO tenant column. audit_event and its NOT NULL tenant_id are not
-- touched. Additive only.

CREATE TABLE IF NOT EXISTS platform_identity_chain_head (
    chain_id TEXT PRIMARY KEY,
    head_hash TEXT NOT NULL CHECK (length(TRIM(head_hash)) > 0),
    next_seq BIGINT NOT NULL CHECK (next_seq > 0),
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
INSERT INTO platform_identity_chain_head (chain_id, head_hash, next_seq)
    VALUES ('platform-identity', 'GENESIS', 1) ON CONFLICT (chain_id) DO NOTHING;

CREATE TABLE IF NOT EXISTS platform_identity_event (
    event_id TEXT PRIMARY KEY,
    event_name TEXT NOT NULL CHECK (length(TRIM(event_name)) > 0),
    subject_kind TEXT NOT NULL CHECK (subject_kind IN ('IDENTITY', 'UNKNOWN_IDENTITY')),
    subject_ref TEXT NOT NULL CHECK (length(TRIM(subject_ref)) > 0),
    outcome TEXT NOT NULL CHECK (outcome IN ('success', 'denied')),
    reason_code TEXT NULL,
    correlation_id TEXT NOT NULL,
    occurred_at TEXT NOT NULL,
    prev_hash TEXT NOT NULL,
    event_hash TEXT NOT NULL,
    chain_seq BIGINT NOT NULL UNIQUE
);

-- 0040 · FR-07 consultation messaging and file sharing (MVC-BUILD-RUNNER-001 U7)
--
-- Ratified AC-FR-07-01 (messages + files within a consultation, invisible outside it)
-- and AC-FR-07-02 (every attempt to deliver a notification writes a delivery record
-- carrying the RENDERED body, never a reference to a mutable template — REQ-MVC-8.67,
-- authoritative only for delivery evidence). Additive only; delivery records are
-- append-only (no UPDATE path exists in the application).

CREATE TABLE IF NOT EXISTS consultation_message (
    message_id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL REFERENCES tenant(tenant_id),
    consultation_id TEXT NOT NULL CHECK (length(TRIM(consultation_id)) > 0),
    sender_id TEXT NOT NULL CHECK (length(TRIM(sender_id)) > 0),
    sender_role TEXT NOT NULL,
    body TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_consultation_message_tenant_consultation
    ON consultation_message (tenant_id, consultation_id, created_at);

CREATE TABLE IF NOT EXISTS consultation_message_attachment (
    attachment_id TEXT PRIMARY KEY,
    message_id TEXT NOT NULL REFERENCES consultation_message(message_id),
    tenant_id TEXT NOT NULL REFERENCES tenant(tenant_id),
    filename TEXT NOT NULL,
    content_type TEXT NOT NULL,
    byte_size INTEGER NOT NULL CHECK (byte_size > 0),
    sha256 TEXT NOT NULL CHECK (length(sha256) = 64),
    storage_key TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS notification_delivery_record (
    record_id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL REFERENCES tenant(tenant_id),
    message_id TEXT NOT NULL REFERENCES consultation_message(message_id),
    recipient_id TEXT NOT NULL CHECK (length(TRIM(recipient_id)) > 0),
    channel TEXT NOT NULL CHECK (channel IN ('IN_APP')),
    attempt_no INTEGER NOT NULL CHECK (attempt_no >= 1),
    status TEXT NOT NULL CHECK (status IN ('DELIVERED', 'FAILED')),
    rendered_body TEXT NOT NULL,
    occurred_at TIMESTAMP NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_delivery_record_message ON notification_delivery_record (tenant_id, message_id);

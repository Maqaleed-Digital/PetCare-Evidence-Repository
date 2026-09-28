-- 0057 · Server-side owner consent ledger (MVC-EPC-D-001 Lane D, D2 — journey J-O2). Additive only.
--
-- Append-only: a grant or a revocation is a NEW row; the current state of a purpose is its latest row. A row can be
-- neither updated nor deleted (trigger), so the history shown to the owner is the history that happened. The purposes
-- and actions match petcare_api/owner_consent.py.

CREATE TABLE IF NOT EXISTS owner_consent_event (
    event_id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL REFERENCES tenant(tenant_id),
    user_id TEXT NOT NULL REFERENCES user_identity(user_id),
    purpose TEXT NOT NULL CHECK (purpose IN ('privacy_notice', 'care_reminders', 'marketing_messages')),
    action TEXT NOT NULL CHECK (action IN ('GRANT', 'REVOKE')),
    origin TEXT NOT NULL CHECK (origin IN ('self_registration', 'pilot_invite', 'account_settings')),
    policy_version TEXT NOT NULL,
    at TIMESTAMP NOT NULL,
    -- privacy_notice is withdrawn by closing the account (erasure request), never by a revocation row.
    CHECK (NOT (purpose = 'privacy_notice' AND action = 'REVOKE'))
);
CREATE INDEX IF NOT EXISTS owner_consent_event_subject ON owner_consent_event (tenant_id, user_id, at);

CREATE OR REPLACE FUNCTION owner_consent_event_is_append_only() RETURNS trigger AS $$
BEGIN
    RAISE EXCEPTION 'owner_consent_event is an append-only ledger: % refused', TG_OP;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS owner_consent_event_no_update_delete ON owner_consent_event;
CREATE TRIGGER owner_consent_event_no_update_delete
    BEFORE UPDATE OR DELETE ON owner_consent_event
    FOR EACH ROW EXECUTE FUNCTION owner_consent_event_is_append_only();

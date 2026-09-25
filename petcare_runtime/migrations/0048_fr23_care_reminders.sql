-- 0048 · FR-23 vaccination and treatment reminders (MVC-BUILD-RUNNER-001 U15)
--
-- Ratified AC-FR-23-01 (REMINDER_DEFAULT=7_DAYS_BEFORE_DUE; SECOND_REMINDER=24_HOURS_BEFORE_DUE_IF_OUTSTANDING;
-- defaults may not be suppressed) and AC-FR-23-02 (owner's language; every send audited). One reminder per
-- (due item, kind) — the UNIQUE constraint makes a repeated scheduler run idempotent. Insert-only. Additive.

CREATE TABLE IF NOT EXISTS pet_care_due (
    due_id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL REFERENCES tenant(tenant_id),
    pet_id TEXT NOT NULL REFERENCES pet_profile(pet_id),
    kind TEXT NOT NULL CHECK (kind IN ('VACCINATION', 'TREATMENT')),
    title TEXT NOT NULL CHECK (length(TRIM(title)) > 0),
    due_at TIMESTAMP NOT NULL,
    recorded_by TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_pet_care_due_tenant ON pet_care_due (tenant_id, due_at);

CREATE TABLE IF NOT EXISTS pet_care_completion (
    due_id TEXT PRIMARY KEY REFERENCES pet_care_due(due_id),
    tenant_id TEXT NOT NULL REFERENCES tenant(tenant_id),
    completed_by TEXT NOT NULL,
    completed_at TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS care_reminder (
    reminder_id TEXT PRIMARY KEY,
    due_id TEXT NOT NULL REFERENCES pet_care_due(due_id),
    tenant_id TEXT NOT NULL REFERENCES tenant(tenant_id),
    owner_id TEXT NOT NULL REFERENCES user_identity(user_id),
    kind TEXT NOT NULL CHECK (kind IN ('REMIND_7D', 'REMIND_24H')),
    language TEXT NOT NULL CHECK (language IN ('ar', 'en')),
    rendered TEXT NOT NULL CHECK (length(TRIM(rendered)) > 0),
    channel TEXT NOT NULL CHECK (channel IN ('IN_APP')),
    sent_at TIMESTAMP NOT NULL,
    UNIQUE (due_id, kind)
);
CREATE INDEX IF NOT EXISTS idx_care_reminder_owner ON care_reminder (tenant_id, owner_id, sent_at);

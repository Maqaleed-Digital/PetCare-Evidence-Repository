-- 0066 · Consultation SOAP note drafts (MVC-EPC-D-001 Lane D, D3c — journey J-V3, screen CV-05 consultation workspace; Sponsor
-- ruling R21.4). Additive only.
--
-- Insert-only and versioned by saved_at: the latest version for a consultation is the draft in force; earlier versions stay.
-- Written only by the consultation's own veterinarian with a practitioner authority in force (petcare_api/main.py enforces both).
-- A draft is UNSIGNED — signing a note (journey J-V4) is not part of this migration.

CREATE TABLE IF NOT EXISTS consultation_soap_draft (
    draft_id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL REFERENCES consultation(session_id),
    tenant_id TEXT NOT NULL REFERENCES tenant(tenant_id),
    veterinarian_id TEXT NOT NULL REFERENCES user_identity(user_id),
    template_id TEXT,
    subjective TEXT NOT NULL CHECK (char_length(subjective) <= 4000),
    objective TEXT NOT NULL CHECK (char_length(objective) <= 4000),
    assessment TEXT NOT NULL CHECK (char_length(assessment) <= 4000),
    plan TEXT NOT NULL CHECK (char_length(plan) <= 4000),
    saved_at TIMESTAMP NOT NULL,
    CHECK (char_length(btrim(subjective || objective || assessment || plan)) > 0)
);
CREATE INDEX IF NOT EXISTS consultation_soap_draft_latest ON consultation_soap_draft (tenant_id, session_id, saved_at);

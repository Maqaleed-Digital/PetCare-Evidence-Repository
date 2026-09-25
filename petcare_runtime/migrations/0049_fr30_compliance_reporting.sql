-- 0049 · FR-30 SFDA compliance reporting automation (MVC-BUILD-RUNNER-001 U16)
--
-- Ratified AC-FR-30-01/02/03. Antimicrobial agent and class are REGISTRATION facts (product_registration);
-- a prescription names its product in prescription_product (insert-only). Notifiable diseases and their
-- statutory windows are a governed register with no served write path; a case cannot exist without its
-- reporting clock (NOT NULL + CHECK). Generated compliance reports store their period and content hash so a
-- report re-derives from recorded events. Additive only.

ALTER TABLE product_registration ADD COLUMN IF NOT EXISTS antimicrobial_agent TEXT NULL;
ALTER TABLE product_registration ADD COLUMN IF NOT EXISTS antimicrobial_class TEXT NULL;
ALTER TABLE product_registration DROP CONSTRAINT IF EXISTS product_registration_antimicrobial;
ALTER TABLE product_registration ADD CONSTRAINT product_registration_antimicrobial
    CHECK ((antimicrobial_agent IS NULL) = (antimicrobial_class IS NULL));

CREATE TABLE IF NOT EXISTS prescription_product (
    prescription_id TEXT PRIMARY KEY REFERENCES prescription(prescription_id),
    tenant_id TEXT NOT NULL REFERENCES tenant(tenant_id),
    product_id TEXT NOT NULL CHECK (length(TRIM(product_id)) > 0),
    recorded_at TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS notifiable_disease (
    disease_code TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    report_within_hours INTEGER NOT NULL CHECK (report_within_hours > 0),
    source TEXT NOT NULL CHECK (length(TRIM(source)) > 0)
);

CREATE TABLE IF NOT EXISTS notifiable_case (
    case_id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL REFERENCES tenant(tenant_id),
    pet_id TEXT NOT NULL REFERENCES pet_profile(pet_id),
    disease_code TEXT NOT NULL REFERENCES notifiable_disease(disease_code),
    detected_at TIMESTAMP NOT NULL,
    report_due_at TIMESTAMP NOT NULL CHECK (report_due_at > detected_at),
    recorded_by TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS notifiable_case_report (
    case_id TEXT PRIMARY KEY REFERENCES notifiable_case(case_id),
    tenant_id TEXT NOT NULL REFERENCES tenant(tenant_id),
    reported_by TEXT NOT NULL,
    reported_at TIMESTAMP NOT NULL,
    reference TEXT NOT NULL CHECK (length(TRIM(reference)) > 0)
);

CREATE TABLE IF NOT EXISTS compliance_report (
    report_id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL REFERENCES tenant(tenant_id),
    kind TEXT NOT NULL CHECK (kind IN ('CONTROLLED_SUBSTANCE_AUDIT')),
    period_from TIMESTAMP NOT NULL,
    period_to TIMESTAMP NOT NULL CHECK (period_to > period_from),
    generated_by TEXT NOT NULL,
    generated_at TIMESTAMP NOT NULL,
    row_count INTEGER NOT NULL CHECK (row_count >= 0),
    content_sha256 TEXT NOT NULL CHECK (length(content_sha256) = 64)
);

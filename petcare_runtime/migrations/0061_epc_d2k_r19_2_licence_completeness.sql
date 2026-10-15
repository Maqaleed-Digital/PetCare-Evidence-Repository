-- 0061 · Establishment-licence record completeness (MVC-EPC-D-001 Lane D, D2k — Sponsor ruling R19.2; rows X-31, X-32). Additive only.
--
-- A licence names its type and scope (X-31) and the evidence document the recording administrator checked (X-32). The columns
-- are nullable only so that rows recorded before this migration remain readable: such a row is INCOMPLETE and never validates
-- a delivery (petcare_api/establishment_licences.py, fail closed). Every new row carries all three (application validation).
-- More than one licence per location is supported (no uniqueness on location). R19.3: no column claims registry verification.

ALTER TABLE establishment_licence ADD COLUMN IF NOT EXISTS licence_type TEXT
    CHECK (licence_type IS NULL OR (char_length(btrim(licence_type)) > 0 AND char_length(licence_type) <= 200));
ALTER TABLE establishment_licence ADD COLUMN IF NOT EXISTS scope TEXT
    CHECK (scope IS NULL OR (char_length(btrim(scope)) > 0 AND char_length(scope) <= 200));
ALTER TABLE establishment_licence ADD COLUMN IF NOT EXISTS evidence_document_ref TEXT
    CHECK (evidence_document_ref IS NULL OR (char_length(btrim(evidence_document_ref)) > 0 AND char_length(evidence_document_ref) <= 200));

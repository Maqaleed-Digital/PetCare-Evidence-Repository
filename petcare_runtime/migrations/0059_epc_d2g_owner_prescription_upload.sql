-- 0059 · Owner-uploaded external prescriptions (MVC-EPC-D-001 Lane D, D2g — journey J-O7; FR-14 owner part). Additive only.
--
-- One row per upload, AWAITING_VERIFICATION until a veterinarian decides it (J-V6). owner_id, tenant_id and the pet's
-- ownership are written from the session by petcare_api/main.py, never from the request. The bytes live in the document
-- store under a server-generated storage_key; the row is written after the object, so it never names a missing object.

CREATE TABLE IF NOT EXISTS owner_prescription_upload (
    upload_id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL REFERENCES tenant(tenant_id),
    owner_id TEXT NOT NULL REFERENCES user_identity(user_id),
    pet_id TEXT NOT NULL REFERENCES pet_profile(pet_id),
    filename TEXT NOT NULL,
    content_type TEXT NOT NULL,
    byte_size INTEGER NOT NULL CHECK (byte_size > 0),
    content_sha256 TEXT NOT NULL,
    storage_key TEXT NOT NULL UNIQUE,
    note TEXT NOT NULL DEFAULT '' CHECK (char_length(note) <= 500),
    status TEXT NOT NULL CHECK (status IN ('AWAITING_VERIFICATION')),
    uploaded_at TIMESTAMP NOT NULL
);
CREATE INDEX IF NOT EXISTS owner_prescription_upload_owner ON owner_prescription_upload (tenant_id, owner_id, uploaded_at);
CREATE INDEX IF NOT EXISTS owner_prescription_upload_status ON owner_prescription_upload (tenant_id, status, uploaded_at);

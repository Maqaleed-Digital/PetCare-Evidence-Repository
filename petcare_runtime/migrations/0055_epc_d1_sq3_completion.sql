-- 0055 · SQ-3 completion (MVC-EPC-D-001 Lane D, D1). Additive only.
--
-- #4  a medical record can be SIGNED once; a signed record is immutable (trigger), content bound by sha256.
-- #12 tenant payout details; #13 tenant bank details — the IBAN is stored ONLY as AES-GCM ciphertext (+ last four).
-- #15 API keys — stored ONLY as sha256 of the key; the key itself is shown once at issuance.
-- #14 staff invitation credentials reuse invite_code with the code column holding "sha256:<hex>" of the credential.

ALTER TABLE pet_medical_record ADD COLUMN IF NOT EXISTS signed_by_actor_id TEXT NULL;
ALTER TABLE pet_medical_record ADD COLUMN IF NOT EXISTS signed_at TIMESTAMP NULL;
ALTER TABLE pet_medical_record ADD COLUMN IF NOT EXISTS content_sha256 TEXT NULL;

CREATE OR REPLACE FUNCTION pet_medical_record_signed_is_immutable() RETURNS trigger AS $$
BEGIN
    IF TG_OP = 'DELETE' AND OLD.signed_at IS NOT NULL THEN
        RAISE EXCEPTION 'a signed medical record is immutable' USING ERRCODE = 'restrict_violation';
    END IF;
    IF TG_OP = 'UPDATE' AND OLD.signed_at IS NOT NULL THEN
        RAISE EXCEPTION 'a signed medical record is immutable' USING ERRCODE = 'restrict_violation';
    END IF;
    RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;
DROP TRIGGER IF EXISTS pet_medical_record_signed_immutable ON pet_medical_record;
CREATE TRIGGER pet_medical_record_signed_immutable
    BEFORE UPDATE OR DELETE ON pet_medical_record
    FOR EACH ROW EXECUTE FUNCTION pet_medical_record_signed_is_immutable();

CREATE TABLE IF NOT EXISTS tenant_payout_details (
    tenant_id TEXT PRIMARY KEY REFERENCES tenant(tenant_id),
    payout_method TEXT NOT NULL CHECK (payout_method IN ('BANK_TRANSFER')),
    payout_schedule TEXT NOT NULL CHECK (payout_schedule IN ('WEEKLY', 'BIWEEKLY', 'MONTHLY')),
    minimum_payout_halalas BIGINT NOT NULL CHECK (minimum_payout_halalas >= 0),
    updated_by TEXT NOT NULL REFERENCES user_identity(user_id),
    updated_at TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS tenant_bank_details (
    tenant_id TEXT PRIMARY KEY REFERENCES tenant(tenant_id),
    bank_name TEXT NOT NULL CHECK (length(TRIM(bank_name)) > 0),
    account_holder TEXT NOT NULL CHECK (length(TRIM(account_holder)) > 0),
    iban_nonce BYTEA NOT NULL CHECK (length(iban_nonce) = 12),
    iban_ciphertext BYTEA NOT NULL CHECK (length(iban_ciphertext) > 16),
    iban_last4 TEXT NOT NULL CHECK (iban_last4 ~ '^[0-9A-Z]{4}$'),
    updated_by TEXT NOT NULL REFERENCES user_identity(user_id),
    updated_at TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS api_key (
    key_id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL REFERENCES tenant(tenant_id),
    name TEXT NOT NULL CHECK (length(TRIM(name)) > 0),
    prefix TEXT NOT NULL CHECK (length(prefix) = 12),
    key_sha256 TEXT NOT NULL UNIQUE CHECK (key_sha256 ~ '^[0-9a-f]{64}$'),
    created_by TEXT NOT NULL REFERENCES user_identity(user_id),
    created_at TIMESTAMP NOT NULL,
    revoked_at TIMESTAMP NULL
);
CREATE INDEX IF NOT EXISTS api_key_tenant ON api_key (tenant_id);

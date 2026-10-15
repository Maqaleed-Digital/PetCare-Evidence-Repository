-- 0062 · Pre-visit intake with photos (MVC-EPC-D-001 Lane D, D2p — screen CO-06; Sponsor ruling R21.4). Additive only.
--
-- One intake per consultation booking (UNIQUE booking_id), insert-only: what the veterinarian reads is what the owner submitted.
-- owner_id, tenant_id, booking_id and pet_id are written from the session and the booking by petcare_api/main.py, never from
-- the request. Photos are images held in the document store under server-generated keys; the objects are written before these
-- rows, and the intake and its photo rows are written in one transaction, so a row never names a missing object. Photos keep
-- the order the owner attached them (position 0..n-1): they share one upload instant, so time cannot order them.

CREATE TABLE IF NOT EXISTS pre_visit_intake (
    intake_id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL REFERENCES tenant(tenant_id),
    booking_id TEXT NOT NULL UNIQUE REFERENCES consultation_booking(booking_id),
    owner_id TEXT NOT NULL REFERENCES user_identity(user_id),
    pet_id TEXT NOT NULL REFERENCES pet_profile(pet_id),
    reason TEXT NOT NULL CHECK (char_length(btrim(reason)) > 0 AND char_length(reason) <= 500),
    symptoms_since DATE,
    eating_normally TEXT NOT NULL CHECK (eating_normally IN ('YES', 'NO', 'UNSURE')),
    current_medications TEXT NOT NULL DEFAULT '' CHECK (char_length(current_medications) <= 500),
    submitted_at TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS pre_visit_intake_photo (
    photo_id TEXT PRIMARY KEY,
    intake_id TEXT NOT NULL REFERENCES pre_visit_intake(intake_id),
    tenant_id TEXT NOT NULL REFERENCES tenant(tenant_id),
    position INTEGER NOT NULL CHECK (position >= 0 AND position < 5),
    filename TEXT NOT NULL,
    content_type TEXT NOT NULL CHECK (content_type IN ('image/jpeg', 'image/png', 'image/heic')),
    byte_size INTEGER NOT NULL CHECK (byte_size > 0),
    content_sha256 TEXT NOT NULL,
    storage_key TEXT NOT NULL UNIQUE,
    uploaded_at TIMESTAMP NOT NULL,
    UNIQUE (intake_id, position)
);
CREATE INDEX IF NOT EXISTS pre_visit_intake_photo_intake ON pre_visit_intake_photo (tenant_id, intake_id, position);

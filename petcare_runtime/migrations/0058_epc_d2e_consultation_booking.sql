-- 0058 · Consultation booking (MVC-EPC-D-001 Lane D, D2e — journey J-O5; ledger row X-26). Additive only.
--
-- One row per booking; a reschedule moves starts_at, a cancellation sets status CANCELLED (the row is kept). Every
-- identity column is written from the session by petcare_api/main.py, never from the request. A veterinarian holds at
-- most one live booking per instant: the partial unique index below is the database's own refusal of a double booking.

CREATE TABLE IF NOT EXISTS consultation_booking (
    booking_id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL REFERENCES tenant(tenant_id),
    owner_id TEXT NOT NULL REFERENCES user_identity(user_id),
    pet_id TEXT NOT NULL REFERENCES pet_profile(pet_id),
    veterinarian_id TEXT NOT NULL REFERENCES user_identity(user_id),
    mode TEXT NOT NULL CHECK (mode IN ('IN_CLINIC', 'VIDEO')),
    starts_at TIMESTAMP NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('BOOKED', 'CANCELLED')),
    reason TEXT NOT NULL DEFAULT '' CHECK (char_length(reason) <= 500),
    created_by_actor_id TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL
);
CREATE INDEX IF NOT EXISTS consultation_booking_owner ON consultation_booking (tenant_id, owner_id, starts_at);
CREATE UNIQUE INDEX IF NOT EXISTS consultation_booking_one_live_per_slot
    ON consultation_booking (tenant_id, veterinarian_id, starts_at) WHERE status = 'BOOKED';

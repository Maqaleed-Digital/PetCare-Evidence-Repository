-- 0064 · Consultation rating (MVC-EPC-D-001 Lane D, D2r — screen CO-13 rate visit; Sponsor ruling R21.4). Additive only.
--
-- One rating per consultation (PRIMARY KEY session_id), insert-only, by the consultation's owner after it is completed
-- (petcare_api/main.py enforces both). owner_id and veterinarian_id are copied from the consultation, never from the request.

CREATE TABLE IF NOT EXISTS consultation_rating (
    session_id TEXT PRIMARY KEY REFERENCES consultation(session_id),
    tenant_id TEXT NOT NULL REFERENCES tenant(tenant_id),
    owner_id TEXT NOT NULL REFERENCES user_identity(user_id),
    veterinarian_id TEXT NOT NULL REFERENCES user_identity(user_id),
    score INTEGER NOT NULL CHECK (score BETWEEN 1 AND 5),
    comment TEXT NOT NULL DEFAULT '' CHECK (char_length(comment) <= 500),
    rated_at TIMESTAMP NOT NULL
);

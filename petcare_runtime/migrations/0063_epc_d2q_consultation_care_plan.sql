-- 0063 · Consultation care plan (MVC-EPC-D-001 Lane D, D2q — screen CO-10 visit summary and care plan; Sponsor ruling R21.4).
-- Additive only.
--
-- One care plan per consultation (PRIMARY KEY session_id), insert-only, written by that consultation's veterinarian after the
-- outcome (petcare_api/main.py enforces both). The owner's visit summary reads it beside the FR-06 outcome and the prescriptions
-- issued under the same session; nothing else is attached to a visit.

CREATE TABLE IF NOT EXISTS consultation_care_plan (
    session_id TEXT PRIMARY KEY REFERENCES consultation(session_id),
    tenant_id TEXT NOT NULL REFERENCES tenant(tenant_id),
    instructions TEXT NOT NULL CHECK (char_length(btrim(instructions)) > 0 AND char_length(instructions) <= 2000),
    follow_up_on DATE,
    recorded_by_actor_id TEXT NOT NULL REFERENCES user_identity(user_id),
    recorded_at TIMESTAMP NOT NULL
);

-- 0065 · Veterinarian availability (MVC-EPC-D-001 Lane D, D3b — journey J-V2, screens CV-02/CV-03; Sponsor ruling R21.4).
-- Additive only.
--
-- A published weekly schedule: a plan (insert-only, versioned by published_at; the latest is in force) and its windows on the
-- Asia/Riyadh clock (weekday 0 = Monday … 6 = Sunday). The veterinarian and tenant are written from the session by
-- petcare_api/main.py. Existing bookings are never changed by a new plan.

CREATE TABLE IF NOT EXISTS vet_availability_plan (
    plan_id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL REFERENCES tenant(tenant_id),
    veterinarian_id TEXT NOT NULL REFERENCES user_identity(user_id),
    published_at TIMESTAMP NOT NULL
);
CREATE INDEX IF NOT EXISTS vet_availability_plan_latest ON vet_availability_plan (tenant_id, veterinarian_id, published_at);

CREATE TABLE IF NOT EXISTS vet_availability_window (
    plan_id TEXT NOT NULL REFERENCES vet_availability_plan(plan_id),
    weekday INTEGER NOT NULL CHECK (weekday BETWEEN 0 AND 6),
    opens TIME NOT NULL,
    closes TIME NOT NULL CHECK (closes > opens),
    PRIMARY KEY (plan_id, weekday, opens)
);

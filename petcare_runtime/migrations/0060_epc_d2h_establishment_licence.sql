-- 0060 · Establishment licences of supplying locations (MVC-EPC-D-001 Lane D, D2h — X-30, Sponsor ruling R18.3). Additive only.
--
-- A delivery (the regulated dispensing act) is accepted only when its supplying location holds a licence of the SAME tenant
-- valid on the Asia/Riyadh date of the act; petcare_api/main.py enforces it. Rows are recorded by a platform administrator
-- with what the licence was checked against; they are never updated (a renewal is a new row).

CREATE TABLE IF NOT EXISTS establishment_licence (
    licence_id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL REFERENCES tenant(tenant_id),
    location_id TEXT NOT NULL REFERENCES inventory_location(location_id),
    licence_number TEXT NOT NULL CHECK (char_length(btrim(licence_number)) > 0 AND char_length(licence_number) <= 200),
    issuing_authority TEXT NOT NULL CHECK (char_length(btrim(issuing_authority)) > 0 AND char_length(issuing_authority) <= 200),
    expires_on DATE NOT NULL,
    basis TEXT NOT NULL CHECK (char_length(btrim(basis)) > 0 AND char_length(basis) <= 200),
    recorded_by_actor_id TEXT NOT NULL,
    recorded_at TIMESTAMP NOT NULL
);
CREATE INDEX IF NOT EXISTS establishment_licence_location ON establishment_licence (tenant_id, location_id, expires_on);

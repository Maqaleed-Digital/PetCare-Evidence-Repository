-- W0-G · additive audit-chain columns
--
-- AUTHORED, NOT APPLIED. CP-2 §4 authorizes migration design and authoring, and
-- schema changes against NON-PRODUCTION only. Applying this against any live
-- database is GATE_LIVE_APPLY and is Sponsor-gated.
--
-- Additive by construction: both columns are NULLable and no existing column,
-- constraint or index is altered or dropped. A deploy that runs this and then
-- rolls back leaves every pre-existing row exactly as it was.
--
-- PRE-EXISTING ROWS — an explicit RECORDED decision, never a guess.
--
--   Rows written before the chain existed have no predecessor digest and no
--   digest of their own. They are left NULL. They are NOT back-filled, and they
--   are NOT assigned a synthetic genesis.
--
--   Back-filling would manufacture a chain over events whose integrity was never
--   protected, producing a log that VERIFIES while proving nothing about the
--   period before the chain was wired. That is worse than an honest gap: it
--   converts an absence of evidence into false evidence.
--
--   Verification therefore starts at the first row where event_hash IS NOT NULL.
--   The boundary is a recorded fact about when the control began, not a defect.

ALTER TABLE audit_event ADD COLUMN prev_hash TEXT NULL;
ALTER TABLE audit_event ADD COLUMN event_hash TEXT NULL;

-- Verification walks the chain in write order; this keeps that walk indexed.
CREATE INDEX IF NOT EXISTS idx_audit_event_chain
    ON audit_event (occurred_at, audit_event_id);

-- NOT ENFORCED YET, and deliberately so.
--
-- A NOT NULL constraint on event_hash is correct only once every writer
-- populates it and the pre-chain rows have been dispositioned by the Sponsor.
-- Enforcing it here would fail closed against exactly the historical rows this
-- migration has just decided to leave NULL.
--
--   ALTER TABLE audit_event ALTER COLUMN event_hash SET NOT NULL;
--
-- Sequence: additive (this migration) -> every writer populates -> validate ->
-- only then enforce, and only if the pre-chain disposition permits it.

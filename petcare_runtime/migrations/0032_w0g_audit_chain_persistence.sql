-- W0-G · persist the audit chain
--
-- AUTHORED AND REHEARSED, NOT APPLIED TO ANY PRODUCTION STORE.
-- Applying this to a production database is GATE_LIVE_APPLY and Sponsor-gated.
--
-- Authority: CP-2 Wave-0 W0-G (chain persisted — the one target its receipt
-- records as NOT delivered, blocked on W0-F, which is now complete),
-- MVC-W0F-DATA-STORE-DECISION-001, migration 0028 (which added prev_hash and
-- event_hash to audit_event).
--
-- Purely additive: one new table, one new NULLable column, two indexes. No
-- existing table, column or row is altered or removed. Reversal is by removing
-- what this file creates.
--
-- PORTABILITY (D.21). Plain SQL only — no provider-proprietary type, extension
-- or function — so the mandatory KSA move replays this file unchanged.

-- ---------------------------------------------------------------------------
-- Chain ordering
-- ---------------------------------------------------------------------------
--
-- The chain is a SEQUENCE, and `audit_event` had no column that establishes one.
-- `occurred_at` is an ISO-8601 TEXT timestamp, so two events written in the same
-- instant tie — and a tie reorders the chain into a verification failure that
-- looks exactly like tampering. Ordering must be explicit, total, and assigned
-- by the writer.
--
-- PRE-EXISTING ROWS ARE LEFT NULL — a recorded decision, matching 0028's
-- decision for prev_hash/event_hash, and for the same reason. Numbering rows
-- that were written before the chain existed would manufacture an ordering
-- nothing witnessed, producing a log that verifies while proving nothing about
-- that period. Verification starts at the first row carrying a sequence.
-- NOT BACK-FILLED.
ALTER TABLE audit_event ADD COLUMN chain_seq BIGINT NULL;

-- Two events cannot occupy one position. Partial, so the historical NULLs above
-- remain representable rather than colliding with each other.
CREATE UNIQUE INDEX IF NOT EXISTS uq_audit_event_chain_seq
    ON audit_event (chain_seq) WHERE chain_seq IS NOT NULL;

-- Serves the tenant-scoped read, in chain order.
CREATE INDEX IF NOT EXISTS idx_audit_event_tenant_seq
    ON audit_event (tenant_id, chain_seq);

-- ---------------------------------------------------------------------------
-- Chain head
-- ---------------------------------------------------------------------------
--
-- One row. Its purpose is CONCURRENCY CONTROL, not caching.
--
-- `prev_hash` is "the previous event's digest", which is a read-then-write. Two
-- concurrent appends that both read the same head produce a fork — two events
-- claiming the same predecessor — and verify_hash_chain reports that as
-- prev_hash_mismatch. A correct log would then be indistinguishable from an
-- attacked one, which is the single property the chain exists to provide.
--
-- Appenders take `SELECT ... FOR UPDATE` on this row, so they serialise on it.
-- Deriving the head from `SELECT ... ORDER BY chain_seq DESC LIMIT 1` instead
-- would not: under READ COMMITTED the second transaction re-reads its own
-- snapshot and still links to the stale head.
CREATE TABLE IF NOT EXISTS audit_chain_head (
    -- A single chain. A second chain id would mean two orderings of one log,
    -- and nothing could then say which of two events came first.
    chain_id TEXT PRIMARY KEY,

    -- The digest of the most recent event, or the genesis marker when empty.
    head_hash TEXT NOT NULL CHECK (length(TRIM(head_hash)) > 0),

    -- The position the next event will take. Allocated under the same row lock
    -- that serialises linkage, so a sequence and a digest can never disagree
    -- about order.
    next_seq BIGINT NOT NULL CHECK (next_seq > 0),

    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- The chain starts at the genesis marker the application names.
--
-- Seeded HERE rather than lazily on first write, deliberately: a repository that
-- created its own head row would create one per empty database it happened to
-- meet, and a head created by a writer is a head no reviewer chose. ON CONFLICT
-- DO NOTHING so the migration ledger's idempotency holds.
INSERT INTO audit_chain_head (chain_id, head_hash, next_seq)
VALUES ('default', 'GENESIS', 1)
ON CONFLICT (chain_id) DO NOTHING;

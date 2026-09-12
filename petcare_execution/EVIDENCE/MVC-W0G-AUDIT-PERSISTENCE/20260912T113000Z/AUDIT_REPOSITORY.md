# A3 / A4 — the audit repository and its schema

```
AUDIT_REPOSITORY_IMPLEMENTED=YES   petcare_api/audit_repository.py
AUDIT_POSTGRES_IMPLEMENTED=YES     0032_w0g_audit_chain_persistence.sql
HASHING_REWRITTEN=NO               the governed algorithm is REUSED unmodified
```

## The boundary

`AuditRepository` is a protocol with two implementations — in-memory and
PostgreSQL — behind the same boundary identity, sessions and invite codes already
use. No SQL appears in `main.py`.

```
append_event(record)                     link and store, atomically
get_event(audit_event_id, *, tenant_id)  one event, within the caller's tenant
query_events_for_tenant(tenant_id, ...)  a tenant's events and no other's
all_events()                             the whole chain, PRIVILEGED
verify_chain()                           reports a break, never repairs one
count()
```

## Why the repository owns chain linkage

`prev_hash` is "the previous event's digest", which is a read-then-write. Two
concurrent appends that both read the same head produce a fork — two events
claiming the same predecessor — and `verify_hash_chain` reports that as
`prev_hash_mismatch`, i.e. as tampering. **A correct log would be
indistinguishable from an attacked one.**

So linkage happens inside one transaction, serialised on a single row of
`audit_chain_head` taken `FOR UPDATE`. A caller cannot get it wrong because a
caller no longer does it. Deriving the head from
`SELECT ... ORDER BY chain_seq DESC LIMIT 1` would not be equivalent: under READ
COMMITTED the second transaction re-reads its own snapshot and still links to the
stale head.

## The hashed record is exactly the governed fields

`GOVERNED_EVENT_FIELDS` is the single definition the write path and the verify
path both use. `chain_seq` is deliberately **not** among them — it is storage
ordering, not content.

This is not theoretical care: W0-G's own receipt records the first implementation
hashing the record *after* attaching `prev_hash`, producing a chain that linked
correctly and verified as BROKEN every time. `test_only_the_governed_fields_are_hashed`
asserts a smuggled field is dropped rather than hashed.

The `audit_event` table names two columns `clinic_id_nullable` and
`reason_code_nullable` where the governed record says `clinic_id` and
`reason_code`. Mapped explicitly in `_COLUMN_BY_FIELD`: a mismatch would store
the event under a key the hash never covered, and verification would fail against
a row written correctly.

## Schema — `0032`, additive

```sql
ALTER TABLE audit_event ADD COLUMN chain_seq BIGINT NULL;
CREATE UNIQUE INDEX uq_audit_event_chain_seq ON audit_event (chain_seq) WHERE chain_seq IS NOT NULL;
CREATE INDEX idx_audit_event_tenant_seq ON audit_event (tenant_id, chain_seq);
CREATE TABLE audit_chain_head (chain_id PK, head_hash, next_seq, updated_at);
INSERT INTO audit_chain_head VALUES ('default','GENESIS',1) ON CONFLICT DO NOTHING;
```

**Ordering had to be explicit.** `audit_event` had no column establishing a
sequence: `occurred_at` is an ISO-8601 `TEXT` timestamp, so two events in the
same instant tie — and a tie reorders the chain into a verification failure that
looks exactly like tampering.

**Pre-existing rows are left NULL** — the same recorded decision `0028` made for
`prev_hash`/`event_hash`, for the same reason. Numbering rows written before the
chain existed would manufacture an ordering nothing witnessed, producing a log
that verifies while proving nothing about that period. Verification starts at the
first row carrying a sequence.

**The head row is seeded by the migration, not lazily by a writer.** A repository
that created its own head would create one per empty database it happened to
meet, and a head created by a writer is a head no reviewer chose.

## What persistence does NOT close

```
ARCH_01_SIGNATURES_OR_ANCHORING=OPEN   carried forward from W0-G, untouched
```

A hash chain detects tampering by anyone without write access to the whole log.
It does not defend against an actor who can rewrite every row and recompute every
digest. `test_aud_09` asserts that limit explicitly rather than letting the
chain's verification imply more than it proves.

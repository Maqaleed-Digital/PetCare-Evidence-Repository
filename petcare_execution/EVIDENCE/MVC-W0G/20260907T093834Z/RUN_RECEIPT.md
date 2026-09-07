# MVC-W0G — wire the existing audit chain

**Authority:** CP-2 `MVC-CP2-PACK-001 V1.0` (SHA-256 verified `8c11c8b9…c473a1`)
**Base:** `200b169558ae0fa30990420e8d4590a9729ed2e8`
**Scope:** NON_PRODUCTION_ONLY · `LIVE_GATE=NO`

## What W0-G asked for, and what was delivered

CP-2 defines W0-G as **integration work, not new cryptography**:

> `DISPOSITION  REUSE the algorithm — do NOT reinvent hashing.`

The algorithm at `petcare_execution/FND/security/audit_chain.py` was correct and
complete — canonical-JSON SHA-256, `compute_event_hash` + `verify_hash_chain` —
and imported by **nothing**. It is now imported and used unmodified. Not one line
of hashing was rewritten.

| CP-2 target | Delivered |
|---|---|
| chain computed on every audit write | **YES** — `_audit()` links every event |
| verification surfaced | **YES** — `GET /audit/chain/verify`, and in governance status |
| fork/gap detectable and reportable | **YES** — T-CHAIN-01/02/03 |
| never silently healed | **YES** — T-CHAIN-04 |
| `prev_hash`, `event_hash` columns | **AUTHORED** — `0028_w0g_audit_chain_columns.sql`, not applied |
| chain **persisted** | **NO** — requires W0-F, Sponsor-gated |

## The one defect this work caught in itself

The first implementation hashed the record *after* attaching `prev_hash`, while
`verify_hash_chain` strips `prev_hash` before recomputing. The chain linked
correctly and verified as **BROKEN** every time — a chain that looks wired and
can never be verified.

`test_t_gov_01` caught it immediately. The fix is to hash the record before the
chain fields are attached, which is what the verifier's core reconstruction
expects. This is exactly why W0-G is integration work with armed controls rather
than a wiring exercise: the failure mode was silent and looked like success.

## Honesty about what this does NOT establish

W0-G makes tampering **detectable**. It does not make the audit log **durable**.
The store is still `_audit_log`, an in-memory list that dies with the process and
is not shared between instances.

Those are reported as two separate fields, deliberately:

```json
"audit_chain_active":    true,
"audit_chain_persisted": false,
"audit_chain_durability": "IN_PROCESS_ONLY — … persistence is W0-F"
```

Collapsing them into one boolean would repeat the MVC-INC-ATTEST-001 defect in a
new place: a service reporting a control it only partly has. A chain over a
volatile store is a real control against tampering and a real non-control against
loss, and W0-E's discipline is that the service must not blur the two.

## Migration — authored, not applied

`petcare_runtime/migrations/0028_w0g_audit_chain_columns.sql`

Additive by construction: two NULLable columns on `audit_event`, one index.
Nothing altered or dropped.

**Pre-existing rows are left NULL — a RECORDED decision, not a guess.**
Back-filling would manufacture a chain over events whose integrity was never
protected, producing a log that verifies while proving nothing about the period
before the chain existed. That converts an absence of evidence into false
evidence, which is worse than an honest gap. Verification starts at the first row
carrying a digest.

`NOT NULL` is written into the file as a commented future step with its
precondition, not enforced now: enforcing it would fail closed against exactly
the historical rows this migration just decided to leave NULL.

The migration was proven to apply by running all 28 migrations against a
throwaway SQLite database in scratch space. `audit_event` gains `prev_hash` and
`event_hash`; no migration errors. No live database was touched.

## Open question carried forward

CP-2 records one, and it is **not** resolved here:

> whether ARCH-01 requires signatures/anchoring BEYOND the hash chain — to be
> determined against V3.2 §25/§26 before claiming the chain complete

This run therefore claims the chain is **wired**, not that it is **complete**.
A hash chain detects tampering by anyone without write access to the whole log;
it does not defend against an actor who can rewrite every row and recompute every
digest. Signatures or external anchoring would, and whether they are required is
a specification question that stays open.

## Boundary

```
PRODUCTION_MUTATED=NO   LIVE_DB_MUTATED=NO
GCP_MUTATED=NO          EXTERNAL_DASHBOARD_MUTATED=NO
MIGRATION_APPLIED=NO (authored only, per CP-2 §4)
```

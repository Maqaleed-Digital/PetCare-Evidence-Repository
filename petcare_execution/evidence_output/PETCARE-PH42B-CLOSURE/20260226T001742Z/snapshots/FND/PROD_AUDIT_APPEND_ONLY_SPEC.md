PetCare PH42-B
Production Audit Ledger Append-Only Specification
Status: Canonical for PH42-B

1. Objective

Define a production-grade append-only audit ledger model that is:
- Tamper-evident (any modification detectable)
- Append-only (no in-place edits)
- Exportable (regulator evidence bundle)
- Deterministic (stable canonical serialization)

2. Core Concept

An audit ledger is an ordered sequence of audit events.
Each record includes a cryptographic hash that commits to:
- its own canonical content
- the previous record hash (prev_hash)

This produces a hash chain.

3. Record Schema (Minimum)

Fields:
- seq: integer, strictly increasing starting at 1
- timestamp_utc: string (YYYYMMDDTHHMMSSZ)
- tenant_id: string
- actor_id: string
- actor_role: string
- event_type: string
- payload: object (must be JSON-serializable)
- prev_hash: hex sha256 string (for seq=1 use "0"*64)
- record_hash: hex sha256 string over canonical record content excluding record_hash

4. Canonical Serialization Rules

Canonical JSON encoding:
- UTF-8
- No trailing spaces
- Object keys sorted
- No float NaN/Inf
- Arrays preserved in order
- Newlines normalized to \n

Hash input:
- canonical JSON of the record with record_hash omitted

5. Append Rules

- New record is appended with seq = last.seq + 1
- prev_hash = last.record_hash
- record_hash computed from canonical content

6. Tamper Detection

If any field of any record changes, its record_hash changes, and the chain breaks at that record and beyond.

Verifier must:
- recompute hashes
- ensure prev_hash linkage
- ensure seq monotonic ordering

7. Export Bundle

Export must include:
- ledger.jsonl (one canonical record per line, includes record_hash)
- bundle_metadata.json:
  - tenant_id
  - environment
  - record_count
  - root_hash (last record_hash)
  - generated_utc
- bundle_checksum (sha256 of concatenated files) (signing in PH42-C/PH27 already exists elsewhere; PH42-B only defines)

8. Out of Scope

- External signing keys
- Cloud KMS integration
- Runtime enforcement hooks in API layer

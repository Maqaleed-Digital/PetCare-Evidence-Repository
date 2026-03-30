PetCare PH42-B
Audit Hash Chain Model
Status: Canonical for PH42-B

1. Purpose

Provide an implementation-neutral model for a tamper-evident audit chain.

2. Definitions

- record: a single audit entry
- record_hash: sha256 hash over the canonical record without record_hash
- prev_hash: record_hash of prior record (or all-zero for first)
- root_hash: record_hash of the final record in the chain

3. Integrity Conditions

Given records r[1..n]:

- r[i].seq == i
- r[1].prev_hash == "0"*64
- r[i].prev_hash == r[i-1].record_hash for i>1
- recompute_hash(r[i]) == r[i].record_hash

4. Failure Modes

- Broken prev link: prev_hash mismatch
- Modified record: hash mismatch
- Reordered records: seq mismatch or prev mismatch
- Deleted record: seq mismatch / prev mismatch
- Inserted record: seq mismatch / prev mismatch

5. Deterministic Canonicalization

Verifier must canonicalize JSON:
- stable key order
- stable formatting
- exact bytes used for hashing

6. Minimal Tooling Delivered in PH42-B

- append-only ledger writer (scaffold)
- hash chain verifier (scaffold)
- negative tests for tampering

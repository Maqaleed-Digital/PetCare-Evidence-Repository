# Clinical Signoff — Immutability Policy

## Principle

An APPROVED clinical record is a legal medical document. Once a record reaches the `APPROVED`
state, its content is sealed and no field may be modified. This mirrors the requirements for
paper-based clinical records under Saudi MoH guidance.

## Sealing Mechanism

On `approve` transition:

1. The record's canonical JSON is serialised (sorted keys, no insignificant whitespace).
2. `record_seal_hash = SHA-256(canonical_json)` is computed and stored.
3. The `approved_at` and `approved_by` (vet `principal_id`) are recorded.
4. The database row's `mutable` flag is set to `false`.
5. A `signoff_approved` audit event (including `record_seal_hash`) is emitted to `audit_ledger`.

## Seal Verification

Any service holding an approved record may verify it has not been tampered with:

```
GET /v1/signoff/{record_id}/verify
→ { "valid": true|false, "expected_hash": "...", "actual_hash": "..." }
```

## Supersession vs. Amendment

| Scenario                              | Correct action                                    |
|---------------------------------------|---------------------------------------------------|
| Minor transcription error             | Supersede: approve corrected record, mark old as SUPERSEDED |
| Clinical update (new findings)        | New DRAFT → PENDING → APPROVED linked via `parent_record_id` |
| Fraudulent modification attempt       | Blocked at storage layer; access-denial audit event raised |

Amendment-in-place of an approved record is **not permitted** under any circumstance.

## Retention

Approved clinical records (and their seals) are retained for **5 years** from the date of
approval per Saudi MoH guidance, after which they move to cold-archive storage. The
`audit_ledger` entry for the approval is retained for 5 years independently.

## Correction Audit Trail

Every SUPERSEDED record remains readable (read-only) with a pointer to its replacement.
The full chain of versions is queryable via:

```
GET /v1/signoff/{record_id}/history
→ [ { "record_id": "...", "state": "SUPERSEDED", "superseded_by": "..." }, ... ]
```

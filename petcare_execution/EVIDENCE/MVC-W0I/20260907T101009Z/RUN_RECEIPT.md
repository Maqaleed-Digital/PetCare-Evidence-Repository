# MVC-W0I — professional authority, separated from device authority

**Authority:** CP-2 `MVC-CP2-PACK-001 V1.0` · BRD V3.2 §28 · PRD-14
**Base:** `4ed4469cde59b6fbd7b07d0811a978d68b1f648f`
**Scope:** NON_PRODUCTION_ONLY · `LIVE_GATE=NO` · `DEPENDENCIES  W0-B` (delivered)

## Why this one could be delivered in full

W0-I is the only remaining Wave-0 package that does not depend on W0-F. CP-2
lists `DEPENDENCIES  W0-B`, and W0-B is delivered — authorization already derives
from the validated session rather than a client header. Nothing here needed the
persistent serving boundary, so nothing here is blocked.

| CP-2 / §28 target | Status |
|---|---|
| human professional authority modelled separately from device sealing authority | **DELIVERED** |
| sole-practitioner bootstrap, RECORDED, never silent | **DELIVERED** |
| T-PROF-01 / 02 / 04 armed | **DELIVERED** |
| T-PROF-03 allowed and recorded | **DELIVERED** |
| schema | **AUTHORED**, not applied |

## Two decisions that shaped the design

**Authority is time-bounded, not a boolean.** `T-PROF-01` denies attesting a
clinical record as an identity that did not hold authority *at that time*. A
`bool` cannot answer that question — it knows only the present. Under a boolean,
a revoked veterinarian would retroactively appear never to have been authorised,
and a newly granted one would appear to have always been. Grants therefore carry
`effective_from` / `revoked_at`, and every check takes the instant it asks about.

The subtle half is the second one, and it has its own test: a vet granted
authority today must not be able to attest a record from before the grant. A
naive `is_authorised(actor)` check passes that case while being wrong.

**Device sealing authority is a different type, not a different flag.**
`T-PROF-02` denies deriving professional authority from a device's sealing
authority. Rather than writing a rule against the derivation, the derivation was
made unrepresentable: `DeviceSealingAuthority` has no `actor_id`, no
`professional_class`, and no method returning a grant. There is no conversion to
write, so there is none to review — and the test asserts the type stays that way,
failing the moment someone adds an actor to it.

Sealing answers *"was this record altered after it was written"*. Professional
authority answers *"was the person who wrote it entitled to"*. A device can
guarantee the first and can say nothing about the second. That is the whole of
§28's separation requirement.

## The sole-practitioner bootstrap

PRD-14 requires a one-vet practice to bootstrap without a second PRINCIPAL, and
`T-PROF-03` requires the act to be ALLOWED and RECORDED, never silent.

Both halves are load-bearing. Refusing the bootstrap would make single-vet
practices unusable. Allowing it silently would make a self-granted authority
indistinguishable from one a second principal conferred — which is exactly what
an auditor needs to be able to tell apart. Recording it is the only option that
does neither.

`granted_by IS NULL` is therefore a **meaningful recorded fact**, not missing
data, and the schema makes the two shapes mutually exclusive:

```sql
CHECK (
    (sole_practitioner_bootstrap = FALSE AND granted_by IS NOT NULL)
    OR
    (sole_practitioner_bootstrap = TRUE  AND granted_by IS NULL)
)
```

A grant with no principal that is *not* marked as a bootstrap — the silent
exception §28 forbids — cannot be stored at all. Verified against SQLite: the
insert is rejected by the CHECK, while both legitimate shapes are accepted.

## Migration — authored, not applied

`petcare_runtime/migrations/0030_w0i_professional_authority.sql`

Two new tables, `professional_authority_grant` and
`clinical_record_attestation`. Nothing existing is altered or dropped.

Device sealing authority is **deliberately not modelled** in either table. A
`device_id` column on a grant would make professional authority derivable from a
device, which is the thing `T-PROF-02` denies.

Proven to apply by running all 30 migrations against a throwaway SQLite database
in scratch space, and the CHECK semantics were exercised directly. No live
database was touched.

## Boundary

```
PRODUCTION_MUTATED=NO   LIVE_DB_MUTATED=NO   MIGRATION_APPLIED=NO
```

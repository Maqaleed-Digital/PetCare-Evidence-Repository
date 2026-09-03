# Canonical Repository Authority — MyVetiCare

**Decision ID:** `MVC-GOV-CANON-001`
**Effective date:** 2026-09-03
**Status:** ACTIVE
**Authority:** Sponsor determination, issued in the execution instruction of 2026-09-03
**Resolves:** `MARKETPLACE_CANONICAL_CODEBASE_AUTHORITY`

## Decision

`petcare-evidence-repository` is the **canonical MyVetiCare implementation
repository**.

`petcare-platform` is designated **`LEGACY_TO_PORT_FROM`** and remains an
authorised source of validated serving-layer functionality until controlled port
completion.

Existing EP-07 marketplace governance seals **remain valid** and are not
reopened by this determination. **No duplicate marketplace implementation is to
be created in `petcare-platform`.**

| Field | Value |
|---|---|
| `CANONICAL_REPOSITORY` | `petcare-evidence-repository` |
| `CANONICAL_LOCAL_PATH` | `$HOME/dev/petcare-evidence-repository` |
| `CANONICAL_REMOTE` | `git@github.com:Maqaleed-Digital/PetCare-Evidence-Repository.git` |
| `SECONDARY_REPOSITORY` | `petcare-platform` |
| `SECONDARY_LOCAL_PATH` | `$HOME/dev/petcare-platform` |
| `SECONDARY_DISPOSITION` | `LEGACY_TO_PORT_FROM` |
| `SECONDARY_REMOTE` | `git@github.com:Waheebow/PetCare-Platform.git` (private) |
| `NEW_FEATURE_DEVELOPMENT_IN_SECONDARY` | PROHIBITED, except changes strictly necessary to produce or verify controlled-port evidence |
| `MARKETPLACE_CANONICAL_LOCATION` | `petcare_runtime/src/petcare/partner_network/` |
| `MARKETPLACE_REBUILD_IN_SECONDARY` | PROHIBITED |
| `MARKETPLACE_ACTIVATION` | NOT_AUTHORIZED |
| `EP07_SEAL_STATUS` | PRESERVED |

## Rationale

1. EP-07 *B2B Marketplace Integration* is already implemented and
   governance-sealed in this repository — `petcare_execution/ep07_closure/`,
   seal commit `11f2a3714e57c23ef9f93ac18b3b64e0c2e51834`, nine waves closed,
   implementation at `petcare_runtime/src/petcare/partner_network/` (37 modules
   across catalog, contracts, orders, pricing, execution visibility and
   settlement preparation / review / export).
2. Rebuilding EP-07 in `petcare-platform` would create a divergent
   implementation of a sealed epic. `petcare-platform` contains **zero**
   occurrences of the string "marketplace"; the absence is a repository
   boundary, not a gap in the product.
3. The convergence work in `petcare-platform` remains valuable as a **validated
   serving-layer port source**: 106 requirements closed against code, tests and
   evidence; 363 passing tests; Arabic-first remediation; an error boundary; and
   an 84-assertion viewport harness.
4. Canonicalisation must **preserve evidence rather than discard validated
   implementation**.
5. Marketplace governance seals must not be invalidated merely because
   constitutional repository authority was previously unlodged.

## What this decision does not authorise

Production deployment · live database changes · Odoo access · ZATCA access ·
external credential entry · marketplace activation · remote push of previously
local-only `petcare-platform` history · closure of human acceptance · closure of
regulatory or DPO gates.

## Standing conditions

- Marketplace **domain ownership** stays in this repository. Serving layers may
  consume it through governed seams; they may not re-own it.
- `petcare-platform` may continue to run and prove its existing tests. It may
  not acquire new product domains.
- Historical evidence in either repository remains interpretable and is not
  rewritten for cosmetic consistency.

## Related findings recorded at lodgement

Two conditions were observed while lodging this decision and are recorded here
because they bear on custody and interpretation. Neither is resolved by this
instrument.

**`evidence/` is untracked in both repositories.** The gate-evidence tree
(`evidence/G-C1`, `G-R1`, `G-O1`, `G-S1`, `G-A1`, `G-C1-pharmacy`,
`FR-ACQUIRE`, `design`) is 40 files on local disk and **0 files tracked in
git**, here or in `petcare-platform`. The 104 requirements that
`petcare-platform` records as `CLOSED_EVIDENCED` cite these paths. Their
content is currently protected by nothing but this working copy. Recorded as
`GOVERNANCE_EXCEPTION_OPEN — GATE_EVIDENCE_UNVERSIONED`.

**Epic identifier collision.** `EP-06` denotes *Emergency Network* under this
repository's planning authority (`petcare_execution/PLANNING/`) and *Security,
Audit, Evidence, Ops Baseline* under the `petcare-platform` requirement
register. Both usages are historical and sealed evidence depends on each.
Recorded as `EPIC_IDENTIFIER_COLLISION_OPEN`; remediation must be an
alias/namespace mechanism, never a rewrite of sealed evidence.

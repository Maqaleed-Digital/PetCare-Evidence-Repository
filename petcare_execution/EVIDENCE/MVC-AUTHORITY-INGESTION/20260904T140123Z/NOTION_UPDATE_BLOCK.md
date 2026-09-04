# Notion update block — PREPARED, NOT APPLIED

Append to the 4 September MyVetiCare handoff. Nothing backdated; nothing
historical rewritten.

```
GATE3_STATUS                     = CLOSED  (verified read-only)
REQUIRED_CHECK                   = verify
STRICT                           = true
ADMIN_ENFORCEMENT                = true
ALLOW_FORCE_PUSHES               = false
ALLOW_DELETIONS                  = false
REQUIRED_PULL_REQUEST_REVIEWS    = null — the gate is the status check, not a review

CI_ACTIVE_PR_CHECK               = YES
CI_VACUITY_FIXED                 = YES
FINAL_ACCEPTANCE_SUBSTRATE       = CLEAN_CLONE

AUTH01_REPOSITORY_RESIDENT       = NO
AUTH02_REPOSITORY_RESIDENT       = NO
AUTH03_REPOSITORY_RESIDENT       = NO
AUTHORITY_PRECEDENCE             = UNRESOLVED_PRECEDENCE
AUTHORITY_INGESTION_PERFORMED    = NO

DENOMINATOR_499_STATUS           = RELAYED_NOT_REMEASURED
DENOMINATOR_499_MEASURED_VALUE   = NOT_MEASURABLE
COMPETING_FIGURE_495             = RECORDED, NOT RECONCILED

MANIFEST_DECLARED_FILES          = 315
MANIFEST_TRACKED_FILES           = 169
MANIFEST_UNVERSIONED_ENTRIES     = 146  (pin holds)
SECRET_SCANNER_ALLOWLIST         = 0

RESPONSIVE                       = 90/90
PORT_REGRESSION                  = 397 python · 120 vitest · tsc clean

GCP_IS_CURRENT_TARGET            = NO
PATHFINDER_002_BOUNDARY          = PRESERVED
HISTORY_PURGE                    = GATE-5_NOT_AUTHORIZED
```

## Correction to the 4 September record

The handoff and this repository's own PORT-10 artefacts state that `499` derives
from **AUTH-01/02/03**. **That is wrong.**

`499` is computed in **`MVC-ACCEPTANCE-ANNEX-001 V1.0` §6** over
**`MVC-BRD-001` V3.1 + V3.2 + `MVC-SPEC-001` V3.1 Annex K** — the MyVetiCare
lineage. AUTH-01/02/03 are the PetCare lineage and the authority table does not
list the MyVetiCare documents at all.

The residency status of AUTH-01/02/03 is unchanged and still correct. Only the
attribution was wrong, and it mattered: it made `499` look unreachable **in
principle**, when the source is on this machine and the blockers are three named,
closable conditions.

## What now blocks 499

1. **Nothing in the family is ratified.** *"All outputs are DRAFT pending Sponsor
   verdict. Nothing is ratified."* · `CP2_STATE = NOT_TAKEN`.
2. **V3.2 does not supersede V3.1.** It incorporates V3.1's requirement text by
   reference; V3.1 is a normative annex carrying the bodies. Neither is complete
   alone, so a single-document ingestion is wrong whichever is picked.
3. **V3.2's bytes have drifted from their own hash register.** REV 8 records
   `d480cb71…`; the file produces `32f53669…`. 2 of 6 REV-8 hashes reproduce
   exactly, which validates the method and makes the other four drift.

## A second figure, and why neither is reproducible

`MVC-BRD-001 V3.2` Appendix T computes **495** — distinct identifiers traced into
a V3.2 section, excluding the metavariable `REQ-MVC-n` and *including*
`REQ-MVC-1`. `499` excludes `REQ-MVC-1` from 500 authored. They exclude different
things over different corpora and **do not reconcile**: the annex's residue set
is four identifiers, but `REQ-MVC-1` is already out of 499, so the arithmetic
gives 496, not 495.

Neither is reproducible from the located documents. Appendix T **elides its own
members** — 33 rows read `REQ-MVC-4.1, REQ-MVC-4.10, … (+114) | 120` — and the
set was *generated* from a part structure, not written out. A literal scan of the
three documents yields 291 distinct identifier strings, which is a lower bound on
mentions and **not a denominator**. The generator is not among the artefacts.

## Sponsor decision available

Ratifying `MVC-BRD-001` V3.1 + V3.2 + Annex K as the requirement authority, and
re-issuing REV 8's hash register against current bytes, would unblock ingestion.
Until then `499` stays relayed — adopting a denominator from an unratified draft
whose bytes have drifted would be worse than the admitted gap, because it would
look measured.

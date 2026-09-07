# MVC-W0F-FINDINGS-DISPOSITION — run receipt

**Run:** `20260907T091710Z` · **Authority:** MVC-GOV-CANON-001 / CP-2
**Base:** `e3d488547d04624f2b1ba5de1ae3a1a7b30da1eb`
**Scope:** NON_PRODUCTION_ONLY · **Cloud authority:** AWS

Disposes the four findings recorded by `MVC-W0F-READINESS/20260907T082004Z`.
No W0-F implementation. No production, live-DB, credential or dashboard action.

## Disposition summary

| Finding | Disposition | Guard |
|---|---|---|
| **F1** GCP cloudbuild under AWS authority | 6 files retained as `LEGACY_RETAINED_NOT_ACTIVE`, registered, not deleted | `test_gcp_legacy_custody.py` — 5 assertions, armed ×2 |
| **F2** absence guard narrower than AC3 | widened from 3 directories to tree-wide, two-sided | `test_retired_role_absence.py` — 5 assertions, armed ×3 |
| **F3** `policy_enforcer.ts` retired-role grant | classified stale, in-file marker, registered | marker guard, armed ×1 |
| **F4** stale pack counts | append-only correction | n/a (documentary) |

## The governing idea, common to F1 and F2

Both findings had the same shape: a rule stated more broadly than it was
enforced, where literal enforcement would have destroyed evidence. Deleting the
GCP configs would erase how the estate was built; scrubbing `pharmacy_operator`
tree-wide would falsify the record of its retirement.

Both are resolved the same way — separate **existence** from **use**, forbid use
absolutely in the surfaces that matter, and require everything else to be
explicitly registered with a reason. Retention stays permitted. Silent retention
does not.

## What changed in live code

Exactly two lines: dead `assigned_pharmacy_operator_id` fields removed from
`AccessContext` and `ResourceContext`. Never read, never passed. This was the
only live-source occurrence of the retired role in the repository.

`LIVE_PHARMACY_OPERATOR_GRANTS=0` — and it was 0 before this change too. The
fields were vestigial, not an authorization path. No grant was closed here
because none was open.

## New governance artefacts

```
GOVERNANCE/CANONICAL_REPOSITORY_AUTHORITY/GCP_LEGACY_CUSTODY_REGISTER.json
GOVERNANCE/CANONICAL_REPOSITORY_AUTHORITY/RETIRED_ROLE_CUSTODY_REGISTER.json
tests/governance/test_gcp_legacy_custody.py
tests/governance/test_retired_role_absence.py
```

Both registers carry the inverse guard — a registered file that disappears, or an
unregistered file that appears, fails a test. A register that can silently drift
out of true is not a control.

## Measured

```
GCP_LEGACY_FILES=6            GCP_ACTIVE_REFERENCES=0     GCP_GUARD_ARMED=YES
ABSENCE_GUARD_SCOPE=TREE_WIDE ABSENCE_GUARD_EXCLUSIONS=6  LIVE_SOURCE_OCCURRENCES=0
POLICY_ENFORCER_CLASSIFICATION=STALE_DESIGN_ARTEFACT      LIVE_PHARMACY_OPERATOR_GRANTS=0
W0F_COUNT_CORRECTION_APPENDED=YES
PERTURBATION_GUARDS_PROVEN=6
REGRESSION=648 green, 0 failed · RESPONSIVE=90/90 · ASSERTIONS_WEAKENED=0
```

## Boundary

```
PRODUCTION_MUTATED=NO   LIVE_DB_MUTATED=NO
GCP_MUTATED=NO          EXTERNAL_DASHBOARD_MUTATED=NO
```

Not crossed: production datastore choice · residency `D.21` · identity migration ·
Gate-5 · GCP as a current target · W0-F implementation.

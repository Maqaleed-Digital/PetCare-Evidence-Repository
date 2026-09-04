# V3.3 Appendix-T authoring plan — INPUT TO A SPONSOR ACT, NOT AN AUTHORITY

**Date:** 2026-09-05 · **Under:** `MVC-GOV-CANON-001`
**Status:** PLAN. Authoring is not performed here. Ratification is a separate act.

## The defect being addressed

`MVC-BRD-001 V3.2` Appendix T prints:

```
CURRENT_REQUIREMENT_TRACE_COVERAGE = 100%   (495/495 identifiers, computed)
DISTINCT_REQUIREMENT_IDENTIFIERS   = 495
```

`495` was withdrawn as **defective** by `MVC-CONTENT-COMPLETENESS-001 V1.0` §1.
Appendix T also **elides its own members**: 33 rows read
`REQ-MVC-4.1, REQ-MVC-4.10, … (+114) | 120`, so the identifier set cannot be
enumerated from the document, and the "100% coverage" claim cannot be checked
against anything.

Classification: `STALE_DENOMINATOR_IN_CANDIDATE_BASELINE`.

## Input

- `petcare_execution/AUTHORITY/MVC-LINEAGE/inventory.json` — deterministic,
  regenerable by `petcare_execution/tools/mvc_inventory.py`, with 20
  known-answer controls.
- `petcare_execution/AUTHORITY/MVC-LINEAGE/sources/` — the six declared source
  documents, byte-identical to their originals and hash-bound.
- `DENOMINATOR_RECONCILIATION.md` — the 495 → 500 → 499 chain and the measured
  511.

## Permitted change scope — narrow

1. Replace the stale Appendix-T denominator representation.
2. Enumerate the identifiers, **or** cite the committed inventory such that the
   denominator is derivable from identifiers alone.
3. Correct the denominator to whatever that enumeration yields.

## Prohibited

- any requirement wording change;
- any scope change;
- any requirement addition or deletion, absent a distinct Sponsor authoring
  decision that permits it;
- any claim of ratification;
- silently adopting `500`, `499` or `511` without the identifiers behind it.

## Precondition that is not yet met

`MVC-SPEC-001 V3.1` — a named namespace source of Appendix T's own derivation —
**does not exist in custody**; only its Annex K does. Until it is recovered, an
enumeration authored from the available sources will not reproduce 500, and
V3.3 should say so in the document rather than presenting a figure that looks
settled.

**Recommended sequence:** recover SPEC V3.1 → re-run the reconstruction →
compare against 500 → author V3.3 with the enumeration → ratify the lineage.
Authoring V3.3 before the recovery attempt would bind a denominator that the
next artefact recovery could immediately move.

```
RATIFICATION_REQUIRED_AFTER_AUTHORING = YES
LINEAGE_RATIFIED                      = NO
```

# Run receipt — lineage repair and denominator reconstruction

**Date:** 2026-09-05 · **Branch:** `govern/denominator-inventory` from `45344eb2`
**Rulings applied:** R1 repair-not-ratify · R2 Gate-5 authorized but deferred · CP-2 TAKEN_NOT_LODGED

## What this run built

A generator that did not exist. `mvc_content_completeness.py` in the portfolio
repo *consumes* `inventory['union']`; nothing in custody ever *built* that file,
and neither it nor the six `.txt` documents it scanned were ever committed. The
corrected `500` universe — and therefore `499` — had never been reproducible.

`petcare_execution/tools/mvc_inventory.py` closes that, with the six source
documents copied byte-identically into custody and 20 known-answer controls.

## The correction I owe

**"495 vs 499 NOT RECONCILED" was false.** I wrote it into artefacts merged to
`main` on 2026-09-04. They reconcile completely, and the adjudication predates
my claim: `MVC-CONTENT-COMPLETENESS-001 V1.0` §1 withdraws 495 as **defective**,
names the three defects that produced it, and records `CORRECTED_UNIVERSE = 500`;
`MVC-ACCEPTANCE-ANNEX-001` §6 then subtracts `REQ-MVC-1` to reach 499.

I compared two figures without finding the document that settles them — the
exact failure the port source's own tracer warns against: *"read the register,
not a document citing it."* Recorded as **C-20**.

## What reconstruction measured

```
MEASURED_UNIVERSE = 511      (declared six-document source set)
                    292      (same set without SPEC V3.0)
HISTORIC          = 500
```

**Nothing was tuned toward 500.** The parser was corrected twice, both times
because inspection found a defect: `REQ-A.5`/`REQ-D.22`/`REQ-E.1`/`REQ-F.12`/
`REQ-C.35` were truncating to `REQ-A`…`REQ-F` — the historic D-A defect in a new
place — and `REQ-FIN-*` namespace mentions were counting as requirements. Both
fixes moved the number away from 500 as often as toward it.

## Why 500 is unreachable, named precisely

**`MVC-SPEC-001 V3.1` does not exist as a document** — only its Annex K, verified
across the filesystem and the portfolio repo's complete git history. V3.2
Appendix T derives its set from *"the SPEC V3.1 / GAP V1.7 namespaces"*. One of
the two named sources is missing, and the SET-A/SET-B spread (511 vs 292) shows
what SPEC-scale absence costs.

`DENOMINATOR_STATUS = NOT_REPRODUCIBLE_MISSING_SOURCE` — a stronger result than
"not reproducible", because the cause is a single recoverable artefact.

## REQ-MVC-1 left in the union, deliberately

The 500 → 499 step needs it to be prose. `MVC-ACCEPTANCE-ANNEX-001` finds it
occurs only as *"the REQ-MVC-1 precedent"*, and V3.1 confirms that phrasing —
but `V3.2` Appendix T lists it as a traced identifier of §1. Two governed
documents disagree. Excluding it would bake one side of an unresolved question
into a measurement **and** move the figure toward the historic one. It stays;
the subtraction is reported separately.

## Also in this run

- **C-21** Appendix T carries the withdrawn 495 and elides 33 rows →
  `STALE_DENOMINATOR_IN_CANDIDATE_BASELINE`. V3.2 is **not edited**; a narrow
  V3.3 authoring plan is prepared instead.
- **C-22** CP-2 is `TAKEN_NOT_LODGED`, Sponsor-explicit 2026-08-31, pack
  `8c11c8b9…c473a1`. The pack's own `NOT_TAKEN` is its pre-decision self-state.
  Not re-dated, not rewritten.
- **C-23** the missing SPEC V3.1, inventory JSON and `.txt` corpus.
- **REV-12 draft** — re-registers current bytes and binds the REV8→current diff
  chain. REV 8's row is untouched. `HASH_CHAIN_INTACT=YES`; there was no custody
  break, only a missing re-registration.

## Measured

| Check | Result |
|---|---|
| python combined | **418 passed** |
| governance | **104 passed** (20 new inventory controls) |
| vitest | 120 passed · tsc clean |
| playwright | **90 / 90** |
| secret scan | CLEAN, 0 allowlisted |
| evidence bundles | 8 bundles, 55 artefacts, 0 mismatches |

```
LINEAGE_RATIFIED = NO      REV12_STATUS = DRAFT_NOT_RATIFIED
GATE5_EXECUTION  = DEFERRED_UNTIL_THIS_PR_MERGED
PRODUCTION_MUTATED = NO · IRREVERSIBLE_ACTION_PERFORMED = NO
```

# Run receipt — post Gate-3 authority continuation

**Date:** 2026-09-04 · **Branch:** `govern/canonical-repository-authority`

## What this run did

Gate 3 was verified read-only and not touched. The lane then went after the
question Gate 3 does not answer: **where does `499` actually come from?**

It found that the answer this repository had been carrying was wrong, and that
the real source is locatable — which converts an unreachable gap into three
named conditions.

## The correction

`499` was recorded as deriving from **AUTH-01/02/03**. It does not.

- **AUTH-01/02/03** are the *PetCare* lineage — `PetCare BRD v1.1`, the AI-Native
  Technical Architecture, the Agentic AI Feature Layer BRD.
- **`499`** is computed in **`MVC-ACCEPTANCE-ANNEX-001 V1.0` §6** over the
  *MyVetiCare* lineage: `MVC-BRD-001` V3.1 CANDIDATE + V3.2 and `MVC-SPEC-001`
  V3.1 Annex K. The port source's authority table lists none of them.

The attribution was inherited from that table's framing rather than measured. The
residency status of AUTH-01/02/03 is unchanged and still `NO`; two new tests
guard the correction so it cannot drift back.

## Why nothing was ingested

Not absence — the sources were found. Three independently sufficient blockers:

1. **Nothing in the family is ratified.** `MVC-RESUMPTION_RECORD.md`: *"All
   outputs are DRAFT pending Sponsor verdict. Nothing is ratified."*
   `CP2_STATE = NOT_TAKEN`.
2. **V3.2 does not supersede V3.1.** It incorporates V3.1's requirement text by
   reference and governs only on conflict; V3.1 is a normative annex carrying the
   requirement bodies. Neither is complete alone.
3. **V3.2's bytes have drifted from their own hash register.** REV 8 binds
   `d480cb71…`; the file produces `32f53669…`. **2 of 6 REV-8 hashes reproduce
   exactly**, which validates the method and makes the other four drift rather
   than a methodology difference. Ingesting would bind a new hash to bytes whose
   link to the recorded governance act is broken.

## Why neither denominator is reproducible

A second computed figure exists — **495**, from V3.2 Appendix T — and it does not
reconcile with 499. They exclude different things: 499 drops `REQ-MVC-1` from 500
authored; 495 drops the metavariable `REQ-MVC-n` and keeps `REQ-MVC-1`.

Neither can be recomputed from the located documents, because **Appendix T elides
its own members**: 33 rows read `REQ-MVC-4.1, REQ-MVC-4.10, … (+114) | 120`. The
set was generated from a part structure, not written out. A literal scan of the
corpus gives **291** distinct identifier strings — a lower bound on mentions,
explicitly **not** a denominator. The generator is not among the artefacts.

## Measured this run

| Check | Result |
|---|---|
| Gate 3 protection | `verify` required, strict, admins enforced, no force-push, no deletions |
| `pytest tests petcare_runtime/tests petcare_api/tests` | **397 passed** |
| `tests/governance` | **83 passed** |
| `npx vitest run` | **120 passed** (18 files) |
| `npx tsc --noEmit` | clean |
| `npx playwright test` | **90 / 90** |
| `secret_scan.py` | 3663 files, **0 allowlisted**, 0 findings |
| `prohibited_literal_scan.py` | 355 files, 0 active defaults |
| `verify_evidence_bundles.py` | 7 bundles, 42 artefacts, 0 mismatches |
| manifest custody | 315 declared / 169 tracked / **146 unversioned — pin holds** |
| custody ∩ unversioned | **0** — no governed evidence claim depends on untracked material |

## Gates

```
GATE-3  CLOSED and verified — not touched by this run
GATE-5  published-history purge — still NOT AUTHORIZED
PRODUCTION_MUTATED = NO   LIVE_DB_MUTATED = NO   GCP_MUTATED = NO
EXTERNAL_DASHBOARD_MUTATED = NO   IRREVERSIBLE_ACTION_PERFORMED = NO
```

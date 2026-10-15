# MVC-EPC-D-001 v1.5 — Lane D unit D2r: CO-13 rate visit

```
UNIT=D2r   AUTHORITY=R21.4 (remaining owner screens, ledger order), R18.4   BASE=origin/main d729fc3
SCREEN=CO-13 "Rate visit" (no journey links CO-13 — tagged @S:CO-13 only)
```

## Ledger position
CO-12 (invoices and payments), which precedes CO-13, is BLOCKED and uncounted: X-05 HyperPay (R18.4) and X-09 ZATCA invoice
format (OPEN, CP2); clinic billing (J-C8) is not built. CO-13 does not depend on it.

## What is built
- `visit_rating.py`: the owner rates ONE of their own COMPLETED consultations once — a whole score 1..5 and an optional comment
  (<=500), insert-only. Owner and veterinarian are copied from the consultation. Nothing is published or aggregated (a public
  rating belongs to PUB-02/PUB-03).
- Migration **0064** (additive): `consultation_rating` (PRIMARY KEY session_id -> consultation; CHECK score 1..5). PG repository;
  harness deletes it before `consultation`.
- Served routes: `POST /api/owner/consultations/{id}/rating` (owner's own; incomplete 409 VISIT_NOT_COMPLETED; second 409
  VISIT_ALREADY_RATED; another owner/tenant 404; staff 403; the score is `StrictInt`, so a JSON `true` is not a score of 1);
  `GET /api/owner/consultations/{id}/rating` (the owner's own); `GET /api/consultations/{id}/rating` (the consultation's
  veterinarian or the clinic administrator; another veterinarian 403). Recording is audited. `served_routes.json` regenerated (+3).
- Web: `/owner/consultations/[sessionId]/rate` (ar/en; Arabic-Indic digits in Arabic), linked from each COMPLETED consultation.

## Defect found during the unit (before any commit)
The first served-test run accepted `{"score": true}` as a score of 1 (pydantic lax mode). Fixed with `StrictInt`; perturbation
P-D2R-CO13-BOOL-SCORE-ACCEPTED is ARMED.

## Full-stack acceptance (each project separately, one worker, no concurrent backend run) — first run, no retries
| PROJECT | CO-13 `@S:CO-13` | J-O6 chat regression (consultations list changed) |
|---|---|---|
| en-desktop | PASS | PASS |
| ar-desktop | PASS | PASS |
| en-mobile | PASS | PASS |
| ar-mobile | PASS | PASS |

The spec: the seeded veterinarian starts two consultations and completes one; rating the open one is 409; owner home -> my
consultations -> only the completed one offers "rate" -> score 4 + comment -> recorded; reload shows it read-only; a second rating
is 409; the veterinarian reads the same score and comment; Arabic: `dir=rtl`, no untranslated copy.

## Evidence
| Check | Result |
|---|---|
| backend, CI command | **1317 passed, 0 failed** |
| D2r served API tests · PostgreSQL control | 10 passed · 1 passed, 0 skipped (added to the CI PostgreSQL list) |
| tsc · web vitest | clean · **48 files / 249 passed** |
| perturbations (`perturb_epc_d_d2r_co13.py`) | **10 ARMED / 0 VACUOUS** |
| migration invariants · register status | 14 passed |
| prohibited-literal / secret / evidence bundles | 0 / CLEAN / 32 bundles FAILED=0 |

## Counting
CO-13 counts when `report.mjs` reports it PASS in all four projects from the CI full-stack run of this PR's head; matrices are taken
from that run, not edited. No journey is tagged. No ledger X-row closes.

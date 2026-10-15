# MVC-EPC-D-001 v1.5 — Lane D unit D2n: J-O9 internal order tracking — partial evidence, J-O9 UNCOUNTED

```
UNIT=D2n   AUTHORITY=R19.5(4), R18.4, R20 (Phase 4)   STACKED_ON=D2m (485fb97, merged by #97 -> 6c41005)
CODE_COMMIT=39dc3ab9841cd9965cd9fbc6a65cdab73c58cacd
```

## What is built
- `orders.tracking_view(order, decision, collection, receipt)`: lifecycle **PLACED -> ROUTED -> DELIVERED -> RECEIPT_ISSUED**, each
  step done exactly when its record exists, at that record's own time. A routing refusal (no chosen location) is not a route.
  `carrier` is always `null`: no carrier reading, courier status or ETA is shown or invented (EXTERNAL:LOGISTICS_PARTNER).
- Every order view (`GET /api/orders`, place/deliver responses) carries `tracking` (additive; no route added).
- `/owner/orders`: the four steps with KSA times (ar/en) and the notice that no courier tracking exists.

## Dependencies stated, not claimed
- **ROUTED** requires FR-15 routing, which in the served stack cannot assign a pharmacy: the routing-licence register has no
  served route (fixture only, MVC-PHARM-001 §6c) and the served app has no maps adapter (EXTERNAL:MAPS_API). The full-stack
  journey therefore proves the REFUSAL path (409 NO_QUALIFYING_PHARMACY recorded; ROUTED stays not done). The assigned path is
  proven at API level with the FR-15 maps CONTRACT DOUBLE (as FR-15's own tests) — not counted as maps availability.
- **Carrier readings**: BLOCKED on the logistics partner (R18.4). Not built, not mocked.

## Counting
The journey spec is tagged **[J-O9-INTERNAL]**, which report.mjs does not count: J-O9 also covers carrier readings, blocked under
R18.4. Same treatment as [J-O8-COD] (R20.1). J-O9 stays **PARTIAL, uncounted**. Whether the internal portion counts J-O9 is a
Sponsor ruling (R18 said to "count only functionality that can be proven against real currently available dependencies").

## Full-stack acceptance (each project separately, one worker, no concurrent backend run)
| PROJECT | J-O9 [J-O9-INTERNAL] | J-O8 [J-O8-COD] regression (orders page changed) |
|---|---|---|
| en-desktop | PASS (after runs 1–2 below) | PASS |
| ar-desktop | PASS | PASS |
| en-mobile | PASS | PASS |
| ar-mobile | PASS | PASS |

JSON results: `evidence/replay/2026-10-15-epc-d-d2n/jo9-tracking-*.json`, `jo8-cod-regression-*.json`.
en-desktop attempts before the passing series, both defects in the NEW spec, not the product:
1. expected 503 ROUTING_UNAVAILABLE, received 409 — the location had no coordinates (NO_PHARMACY_LOCATED) and no routing licence
   is recordable through a served route; the spec now gives the location coordinates and asserts the actual fail-closed refusal
   (409 NO_QUALIFYING_PHARMACY, recorded decision with no chosen location) — equally specific.
2. read the steps before the reloaded page rendered (`{}`); replaced with web-first auto-retrying assertions of all four steps.

## Evidence
| Check | Result |
|---|---|
| backend, CI command (D2n head) | **1299 passed, 0 failed** |
| J-O9 served API tests · PostgreSQL control | 5 passed · 1 passed, 0 skipped |
| tsc · web vitest | clean · **46 files / 241 passed** (pinned FR-20/FR-04/FR-15 page tests passing) |
| perturbations (`perturb_epc_d_d2n_jo9.py`) | **8 ARMED / 0 VACUOUS** (run 1: 7/1 — RECEIPT-NOT-FROM-RECORD vacuous against the served test, where collection and receipt share one instant; retargeted to the PostgreSQL test with distinct stored times; `run1.out.txt` kept) |
| prohibited-literal / secret / evidence bundles | 0 / CLEAN / 32 bundles FAILED=0 |

## Counts
No ledger row closes. CP1 11/19, CP2 0/40; screens 11/107; journeys 9/53 (J-O8, J-O9 PARTIAL, uncounted).

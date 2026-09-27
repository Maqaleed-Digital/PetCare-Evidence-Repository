# MVC-BUILD-RUNNER-001 v1.3 — ledger segment s4

Chained to `evidence/receipts/2026-09-27-mvc-build-runner-001-v1.3-s3.md` (not modified) — sha256 e9c8adb4095a86910609cf2f3575b1be3a3d50c27ed0e7f7025bda63f8e6ee3d.

| Unit | PR | PR head | Merge SHA | CI attempts | Result | P1-High ACCEPTED | Criteria evidenced | NFR evidenced |
|---|---|---|---|---|---|---|---|---|
| U30 historical correction (merge record) | #78 | 71dcc3e80823d4a6b7a07570a6661d48879194d2 | 41bca574fcccffa801d2bb1368854ab37929d706 | 1 (PG 203 passed 0 skipped) | correction receipt; M1–M5 PASS (M2 n/a: no perturbation) | 2/16 | 42/68 | 3/13 |
| R2 fix: U25 retarget + session-binding guard | (this PR) | see PR | pending | see PR | 6/6 ARMED, 1 SUPERSEDED | 2/16 | 42/68 | 3/13 |

Phase R1 on 41bca57: PASS (pytest 1141 passed 0 skipped; checker/routes byte-stable; web 193; scanners 0).
Phase R2 on 41bca57: evidence 51 keys / 164 items — 107 tests pass, 40 served_app collected, 16 artefacts match;
perturbations — 22 of 23 committed scripts ARMED as recorded; perturb_u25.py stopped on anchor drift -> this fix.

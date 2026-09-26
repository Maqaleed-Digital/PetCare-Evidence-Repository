# MVC-BUILD-RUNNER-001 v1.2 — ledger segment s5

Chained to `evidence/receipts/2026-09-26-mvc-build-runner-001-v1.2-s4.md` (not modified) — sha256 41e394e51a22d4392c805304f77b63ed08498c812bf45ac06982aaa54ee2de49.

| Unit | PR | PR head | Merge SHA | CI attempts | Closed | P1-High ACCEPTED | Criteria evidenced | NFR evidenced |
|---|---|---|---|---|---|---|---|---|
| U27 SQ-2 → AC-FR-06-01/02 (merge record) | #73 | 34bd344e35fd90d129c8a210a5047b47c3e62cd7 | 9d526742301dcc34180118bbb624bcb9ac52a4b7 | 1 (PG 202 passed 0 skipped) | AC-FR-06-01, AC-FR-06-02 | 2/16 | 42/68 | 2/13 |
| R3 replay receipt + harness | (this PR) | see PR | pending | see PR | — | 2/16 | 42/68 | 2/13 |

Phase B complete: no remaining gap is internally closable. Replay: `evidence/receipts/2026-09-26-replay-68-13.md`.
FINDINGS: R2-U22-ANCHOR-DRIFT (fixed, one attempt), R2-UNSCRIPTED-PERTURBATIONS (19 reconstructed, ARMED).
SPONSOR_QUEUE: SQ-3 NFR-08 (open).

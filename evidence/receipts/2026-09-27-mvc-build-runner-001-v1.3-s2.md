# MVC-BUILD-RUNNER-001 v1.3 — ledger segment s2

Chained to `evidence/receipts/2026-09-27-mvc-build-runner-001-v1.3.md` (not modified) — sha256 32b1c6c9f58052654ab28641a8eae49e19818760097b786b2163f6d028c98e8c.

| Unit | PR | PR head | Merge SHA | CI attempts | Result | P1-High ACCEPTED | Criteria evidenced | NFR evidenced |
|---|---|---|---|---|---|---|---|---|
| U28 NFR-08 SQ-3 (merge record) | #76 | be8bcd0936d64ab01a664f4fdd583f90a6a6ed5f | 630cbad295f920ccda42cf5556c16490f0383cee | 1 per head, 0 re-runs (see finding); final head: PG 203 passed 0 skipped | NFR-08 EVIDENCED; M1–M5 PASS | 2/16 | 42/68 | 3/13 |
| U29 video default-off hardening | (this PR) | see PR | pending | see PR | control hardened; 3/3 ARMED | 2/16 | 42/68 | 3/13 |

FINDING U28-STALE-BASE-BRANCH: the U28 branch was cut from a stale local origin/main (6a540fc, before the GA-2 merge).
CI passed on that head (633fcea), but GitHub refused the merge (branch BEHIND). The branch was rebased onto 6911573
(GA-2 only touched two governance files — no overlap) and CI passed again on the final head be8bcd0; merged there.
Not a failure re-run; M1 holds on the final head. The U28 receipt's BASE_MAIN=6911573 is true of the merged history.

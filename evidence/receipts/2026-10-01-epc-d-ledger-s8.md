# MVC-EPC-D-001 — Lane D ledger segment s8 (predecessor evidence/receipts/2026-09-30-epc-d-ledger-s7.md, sha256 1c1458ea7c0a07e57b0acb94f70233c6bce3ac7cb3399ad3c8d029d7be01e1eb, not modified)

| Unit | PR | Head | Merge SHA | CI attempts | D1–D6 | Journeys PASS | Screens PASS |
|---|---|---|---|---|---|---|---|
| D2e R14 record closure · J-O5 booking (CO-05, CO-07) · X-26 · R14.4 CI initdb (merge record — s7 left it "pending") | #88 | 1e55c26504d6bc9713a99a9478dc410bbcd3fb07 | 1df6f2417b1b8fc26092fd197f460c21950c0f85 | 1 (success; workflow verify run #235) | PASS (D3: 269 -> 285, 280 ARMED, 5 excluded) | 8/53 | 9/107 |
| D2f R16 reconciliation · X-22 Option B (registration/submission) · X-27 · J-O6 chat and files (CO-09; CO-08 fail-closed) | (this PR) | see receipt | pending | — | see receipt 2026-10-01-epc-d-d2f-x22-x27-jo6.md | 8/53 | 10/107 |

Ledger rows (canonical Notion ledger, 2026-10-01): X-26 CLOSED (merge 1df6f24, R16.1). X-27 closes on the D2f merge. X-22 OPEN
(Option B built; residual D2F-X22-LAPSE-INSTANT awaits a Sponsor ruling). X-28 ADDED (CP1: user-facing dates from UTC instants).
CP1 measured 15 (14 + X-28), CLOSED 4/15 (X-04, X-23, X-25, X-26). CP2 0/39, CP3 0/20.
R14_4_CI_INITDB=PROVEN (run #235 steps 6 and 8). Rulings custody: evidence/receipts/2026-10-01-epc-d-rulings-register.md (R16 verbatim).

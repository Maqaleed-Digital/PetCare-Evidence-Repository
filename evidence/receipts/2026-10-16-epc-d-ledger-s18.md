# MVC-EPC-D-001 — Lane D ledger segment s18 (predecessor evidence/receipts/2026-10-15-epc-d-ledger-s17.md, sha256 904ac3e22f6df4616f76d20df3eb0668ed34fb0d01c86b51dbc33b8e079d7ad8, not modified)

| Unit | PR | Head | Merge SHA | CI attempts | D1–D6 | Journeys PASS | Screens PASS |
|---|---|---|---|---|---|---|---|
| R21.1 annotation, ledger s17 (merge record — s17 left it "(this PR) / pending") | #102 | cffd1d1b3ff3b95a3222cb73f490e1be24259029 | c5d6d4f042c854e3551fe0a875781567d243d1d8 | 1 (verify: SUCCESS) | no code | 9/53 | 11/107 |
| D2o CO-04 vaccination card (PDF) — R21.4 owner screens | (this PR) #103 | see PR | pending | see PR (head 635380c verify: SUCCESS; matrices from that run) | see receipt 2026-10-15-epc-d-d2o-co04-vaccination-card.md (E2E 4/4; J-O4 regression 4/4) | 9/53 | 12/107 |

Matrices: `product/SCREENS.md` and `petcare_web/e2e/JOURNEYS.md` are the CI full-stack run of head 635380c (run 38806572221,
artifact `journey-results`), copied byte-for-byte; versus main they differ only in the CO-04 row (PASS) and the screen total.
Owner screens triaged (R21.4, R18.4): CO-08 BLOCKED (R17.3, counsel REG-02); CO-12 BLOCKED (X-05 HyperPay; X-09 ZATCA OPEN, CP2).
Ledger rows: none added or closed. Measured on main c5d6d4f before this PR: CP1 11/19, CP2 0/40 (X-33 OPEN), CP3 0/20; screens
11/107; journeys 9/53; BRD FR accepted 2/31. This PR, once merged: screens 12/107.

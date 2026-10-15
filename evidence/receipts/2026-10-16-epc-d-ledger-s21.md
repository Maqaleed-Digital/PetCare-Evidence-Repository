# MVC-EPC-D-001 — Lane D ledger segment s21 (predecessor evidence/receipts/2026-10-16-epc-d-ledger-s20.md, sha256 d520270bf537a087b196bb06cccd6426e043771010521af3f2a2d2d755525e08, not modified)

| Unit | PR | Head | Merge SHA | CI attempts | D1–D6 | Journeys PASS | Screens PASS |
|---|---|---|---|---|---|---|---|
| D2q CO-10 visit summary and care plan (merge record — s20 left it "pending") | #105 | a6458711026e00b7b670b67f5da1c76cc20d0840 | 8af13d515d7e152eb2864c66e1315d9201d0e82d | 2 (head b866003 SUCCESS -> matrices; head a645871 SUCCESS, its matrices byte-identical to the committed ones) | see D2q receipt | 9/53 | 14/107 |
| D2r CO-13 rate visit — R21.4 owner screens (CO-12 BLOCKED: X-05, X-09) | (this PR) #106 | see PR | pending | see PR (head e1a790d verify: SUCCESS; matrices from that run) | see receipt 2026-10-16-epc-d-d2r-co13-rate-visit.md (E2E 4/4; J-O6 regression 4/4) | 9/53 | 15/107 |

Matrices: `product/SCREENS.md` from the CI full-stack run of head e1a790d (run 38819224108, artifact `journey-results`), copied
byte-for-byte; versus main it differs only in the CO-13 row (PASS) and the screen total; CO-10 stays PASS beside the new link.
`JOURNEYS.md` unchanged.
Owner screens (R21.4) after this PR: CO-04, CO-06, CO-10, CO-13 PASS; CO-08 BLOCKED (R17.3, counsel REG-02); CO-12 BLOCKED (X-05,
X-09). Ledger rows: none added or closed. Measured on main 8af13d5 before this PR: CP1 11/19, CP2 0/40 (X-33 OPEN), CP3 0/20;
screens 14/107; journeys 9/53; BRD FR accepted 2/31. This PR, once merged: screens 15/107.

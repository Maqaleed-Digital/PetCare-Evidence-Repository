# MVC-EPC-D-001 — Lane D ledger segment s19 (predecessor evidence/receipts/2026-10-16-epc-d-ledger-s18.md, sha256 e375b0c82e04390d50c62c2b3813789b55e995b73a810c1ab37ab8a89dc765d7, not modified)

| Unit | PR | Head | Merge SHA | CI attempts | D1–D6 | Journeys PASS | Screens PASS |
|---|---|---|---|---|---|---|---|
| D2o CO-04 vaccination card (merge record — s18 left it "pending") | #103 | 0a1e2426f148d80b3138654ea66f32141bca4b8a | d729fc3d2e02ebf422ebd238765b623160400bcf | 2 (head 635380c SUCCESS -> matrices; head 0a1e242 SUCCESS, its matrices byte-identical to the committed ones) | see D2o receipt | 9/53 | 12/107 |
| D2p CO-06 pre-visit intake with photos — R21.4 owner screens | (this PR) #104 | see PR | pending | see PR (head ffea16b verify: SUCCESS; matrices from that run) | see receipt 2026-10-16-epc-d-d2p-co06-previsit-intake.md (E2E 4/4 after fix; J-O5 regression 4/4) | 9/53 | 13/107 |

Matrices: `product/SCREENS.md` from the CI full-stack run of head ffea16b (run 38811324918, artifact `journey-results`), copied
byte-for-byte; versus main it differs only in the CO-06 row (PASS) and the screen total. `JOURNEYS.md` unchanged.
Ledger rows: none added or closed. Measured on main d729fc3 before this PR: CP1 11/19, CP2 0/40 (X-33 OPEN), CP3 0/20; screens
12/107; journeys 9/53; BRD FR accepted 2/31. This PR, once merged: screens 13/107.

# MVC-EPC-D-001 — Lane D ledger segment s20 (predecessor evidence/receipts/2026-10-16-epc-d-ledger-s19.md, sha256 e4633284686524b564b31fbcf4955b3f0b7bf79138dfabae2b73f32d32dc5bb2, not modified)

| Unit | PR | Head | Merge SHA | CI attempts | D1–D6 | Journeys PASS | Screens PASS |
|---|---|---|---|---|---|---|---|
| D2p CO-06 pre-visit intake with photos (merge record — s19 left it "pending") | #104 | 299eb722fb4f202b5ec4818011ee649212d74a45 | 26b6edf4935ec32363dd62a39a7aa100fa332df5 | 2 (head ffea16b SUCCESS -> matrices; head 299eb72 SUCCESS, its matrices byte-identical to the committed ones) | see D2p receipt | 9/53 | 13/107 |
| D2q CO-10 visit summary and care plan — R21.4 owner screens | (this PR) #105 | see PR | pending | see PR (head b866003 verify: SUCCESS; matrices from that run) | see receipt 2026-10-16-epc-d-d2q-co10-visit-summary.md (E2E 4/4; J-O6 regression 4/4) | 9/53 | 14/107 |

Matrices: `product/SCREENS.md` from the CI full-stack run of head b866003 (run 38815352241, artifact `journey-results`), copied
byte-for-byte; versus main it differs only in the CO-10 row (PASS) and the screen total. `JOURNEYS.md` unchanged.
Finding recorded in the D2q receipt: CONSULT-READ-NOT-PARTICIPANT-SCOPED (FR-06 GET /api/consultations/{id}; not changed).
Ledger rows: none added or closed. Measured on main 26b6edf before this PR: CP1 11/19, CP2 0/40 (X-33 OPEN), CP3 0/20; screens
13/107; journeys 9/53; BRD FR accepted 2/31. This PR, once merged: screens 14/107.

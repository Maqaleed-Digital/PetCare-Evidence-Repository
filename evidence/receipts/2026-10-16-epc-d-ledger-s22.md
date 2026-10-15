# MVC-EPC-D-001 — Lane D ledger segment s22 (predecessor evidence/receipts/2026-10-16-epc-d-ledger-s21.md, sha256 c015348b5328c1d8920c6c7f1814c723835718ca23ce1a6c827f91e25cd6a36f, not modified)

| Unit | PR | Head | Merge SHA | CI attempts | D1–D6 | Journeys PASS | Screens PASS |
|---|---|---|---|---|---|---|---|
| D2r CO-13 rate visit (merge record — s21 left it "pending") | #106 | e7d709a65bea6cea1078233130b21f1f4f0a3dc6 | ae222e055a1a2d54977336018bd5c941a75da8e5 | 2 (head e1a790d SUCCESS -> matrices; head e7d709a SUCCESS, its matrices byte-identical to the committed ones) | see D2r receipt | 9/53 | 15/107 |
| D3a J-V1 internal — onboarding + licence status (CV-12) [J-V1-INTERNAL]; J-V1 and CV-12 UNCOUNTED (X-33, R19.3) | (this PR) | see PR | pending | see PR | see receipt 2026-10-16-epc-d-d3a-jv1-licence-status.md (E2E 4/4) | 9/53 | 15/107 |

D3 veterinarian journeys begin (R21.4). J-V1 stays uncounted while its licence verification can only be a staff attestation: the
registry check is X-33 (OPEN, CP2). No count changes in this PR; matrices are not edited.
Ledger rows: none added or closed. Measured on main ae222e0: CP1 11/19, CP2 0/40 (X-33 OPEN), CP3 0/20; screens 15/107;
journeys 9/53; BRD FR accepted 2/31.

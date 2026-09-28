# MVC-EPC-D-001 — Lane D ledger segment s5 (predecessor evidence/receipts/2026-09-28-epc-d-ledger-s4.md, sha256 ddea10e352c8d9682a958fd8fbb04600e4074bb1ba183bab3ffe2f0867aac121, not modified)

| Unit | PR | Head | Merge SHA | CI attempts | D1–D6 | Journeys PASS | Screens PASS |
|---|---|---|---|---|---|---|---|
| D2b J-00 landing + J-O1 self-registration (merge record) | #85 | cdfb1f4cc9aac3534c9ea5ef8e25b86c572d912d | c47bb0a | 2 (1st: stale X6 assertion — real fix, not a flake re-run) | PASS (D3: 221 -> 234, 229 ARMED, 5 excluded; u26 frozen-literal edit caught and fixed in-PR) | 2/53 | 2/107 |
| D2c J-O2 consent · J-O3 profile/export · J-O11 owner MFA | (this PR) | see PR | pending | see PR | see receipt | 5/53 | 3/107 |

Ledger rows: X-01 2/107 → 3/107 on merge. X-03 UI: #11 export now reachable from /account through step-up (J-O3).
X-22 Sponsor gate (A/B). X-24 guarded, OPEN until D9. New finding D2C-REFUSALS-WITHOUT-CORS fixed.

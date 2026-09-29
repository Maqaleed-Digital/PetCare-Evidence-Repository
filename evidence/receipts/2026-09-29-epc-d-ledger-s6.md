# MVC-EPC-D-001 — Lane D ledger segment s6 (predecessor evidence/receipts/2026-09-28-epc-d-ledger-s5.md, sha256 20da09e6918a49107a6d9cc71f1db723c472d084b931149c4644db0a77a79785, not modified)

| Unit | PR | Head | Merge SHA | CI attempts | D1–D6 | Journeys PASS | Screens PASS |
|---|---|---|---|---|---|---|---|
| D2c J-O2 consent · J-O3 profile/export · J-O11 owner MFA (merge record — s5 left it "(this PR) / pending") | #86 | dfce9329de485847fc7366089b2ab21a6fff7e3c | 4896e3316e29d12f13f9af0b53e6a6035446777e | 2 (1st on f031864 cancelled — superseded by the receipt commit; 2nd on dfce932 success) | PASS (D3: 234 -> 250, 245 ARMED, 5 excluded) | 5/53 | 3/107 |
| D2d CO-01 owner home · CO-14 notifications (J-O10) · J-O4 pets · R10 consent at dispatch · R12 scratch ownership · R13 | (this PR) | see PR | pending | see PR | see receipt 2026-09-29-epc-d-d2d-owner-home-notifications-pets.md | 7/53 | 7/107 |

Ledger rows: X-25 CLOSED (dispatch refuses without consent; tests + ARMED perturbations + J-O10). X-01 3/107 → 7/107.
X-26 OPEN (J-O5). X-22 OPEN — reproduced under a controlled clock, no TZ masking. X-27 NEW (consultation pet selector).
R13: AC-FR-23-01 interpretation recorded (governance/sponsor_acts/MVC-EPC-D-001-R13-FR23-CONSENT.md); four registered
tests amended precondition-only, assertions byte-identical; acceptance counts unchanged.

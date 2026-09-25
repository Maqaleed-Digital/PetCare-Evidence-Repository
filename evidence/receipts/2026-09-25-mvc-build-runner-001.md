# MVC-BUILD-RUNNER-001 — programme ledger, segment 2026-09-25 (append-only by SEGMENT)

Chained to the prior ledger (not modified — M3 forbids editing an existing receipt):
`evidence/receipts/2026-09-24-mvc-build-runner-001.md` @ origin/main b19ac23 — git blob
a68e4c5aabee0fb7fc1c9e3fc4a4c1a85361d60b, sha256 2fc46cf06457bcc64829e2023786f556a896e33b799f293ad07aa998abdb535e.
Each later unit adds a NEW segment (`…-s2.md`, `…-s3.md`) that records the previous unit's merge and chains to the
segment before it by sha256; no segment is edited after it lands.

Recovery 2026-09-25 (Mac restart): origin/main = b19ac23 (PR #52). U0-U7 MERGED (#45-#52); no open programme PR;
`build/u8-fr13-inventory` at b19ac23 with no commits and no uncommitted work. Control plane verified: PR #44 head is an
ancestor of main; evidence.json present; checker MVC-REQREG-003 v1.3; served_app marker registered; pack RATIFIED;
status.json reproduces byte-exact from main. Measured at recovery: PHASE1_HIGH_ACCEPTED=1/16, CRITERIA_EVIDENCED=13/68.

| Unit | PR | PR head | Merge SHA | CI attempts | Criteria closed | FR status | P1-High ACCEPTED | Criteria evidenced |
|---|---|---|---|---|---|---|---|---|
| U7 FR-07 (merge record, absent from prior ledger) | #52 | 016d6440f2734507d12f790e3a48918c3dfc3090 | b19ac23a84cdd23330522986dd0e951f8b4f3b6c | 1 (verify: SUCCESS) | AC-FR-07-01, -02 | FR-07 ABSENT->REACHABLE_TESTED | 1/16 | 13/68 |
| U8 FR-13 | (this PR) | see PR | pending | see PR | AC-FR-13-01, -02, -03 (AC-04 COUNSEL:L-2 only) | FR-13 ABSENT->REACHABLE_TESTED | 1/16 | 16/68 |

SPONSOR_QUEUE (carried): SQ-1 AC-FR-01-03 — do pre-session events (registration, failed sign-in) count as account
actions, and how is a tenantless security event recorded? Class SPONSOR_PRODUCT_DECISION. Safely buildable meanwhile:
chaining of session-bearing account actions.

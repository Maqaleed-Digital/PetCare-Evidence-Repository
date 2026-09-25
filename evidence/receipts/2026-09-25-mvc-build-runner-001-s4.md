# MVC-BUILD-RUNNER-001 — programme ledger, segment 2026-09-25 s4

Chained to segment s3 (not modified): `evidence/receipts/2026-09-25-mvc-build-runner-001-s3.md` @ origin/main 41236b6 —
git blob 53c0bd4419f91dbeaf74dc1fd3663da638492acb, sha256 ef8ab78149262191268c780d1f97ab1f80ff71efe1994e759035b586feac114e.

| Unit | PR | PR head | Merge SHA | CI attempts | Criteria closed | FR status | P1-High ACCEPTED | Criteria evidenced |
|---|---|---|---|---|---|---|---|---|
| U10 FR-05 (merge record) | #55 | 59682ab03b732345c3ff3a0cfbd6ccea40dadb86 | 41236b663bbc24b20880d1583fc4919a7ae65caf | 1 (verify: SUCCESS; PG 188 passed 0 skipped) | AC-FR-05-01, -02 | FR-05 ABSENT->REACHABLE_TESTED | 1/16 | 23/68 |
| U11 FR-06 | (this PR) | see PR | pending | see PR | AC-FR-06-04 (AC-05 COUNSEL only) | FR-06 ABSENT->REACHABLE_TESTED | 1/16 | 24/68 |

SPONSOR_QUEUE:
- SQ-1 AC-FR-01-03 (carried) — SPONSOR_PRODUCT_DECISION.
- SQ-2 AC-FR-06-01/-02 — NEW. Ratified with dependency NONE, yet AC-FR-06-05 keeps remote consultation fail-closed
  until COUNSEL:REG-02_TELEMEDICINE. Question: are AC-01/02 accepted on the capability proven with the gate opened in a
  test environment, or only once video is demonstrable in the served deployment (i.e. effectively COUNSEL:REG-02)?
  Why needed: decides whether FR-06 can reach ACCEPTED before counsel. Safely buildable meanwhile: the WebRTC video +
  screen-share capability behind the gate. Class: SPONSOR_PRODUCT_DECISION.

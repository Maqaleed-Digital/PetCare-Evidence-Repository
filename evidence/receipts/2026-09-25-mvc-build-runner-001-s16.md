# MVC-BUILD-RUNNER-001 — programme ledger, segment 2026-09-25 s16 (closing segment at stop)

Chained to segment s15 (not modified): `evidence/receipts/2026-09-25-mvc-build-runner-001-s15.md` @ origin/main c255263 —
git blob 695210b56f5ede331b4acbe1fe66daa2169b3d35, sha256 47ab56249d990efd8972134bfede86b6f97ef55cc3c015b396244064814f5c0b.

| Unit | PR | PR head | Merge SHA | CI attempts | Criteria closed | FR status | P1-High ACCEPTED | Criteria evidenced |
|---|---|---|---|---|---|---|---|---|
| U22 FR-06 video capability (merge record) | #67 | 386fe4a9fb2b455de24d56206609ecd5a5da3edf | c2552636fda5551a7d3068fa3e97974659be1c19 | 1 (verify: SUCCESS; PG 199 passed 0 skipped) | — (AC-01/02 held for SQ-2) | FR-06 REACHABLE_TESTED | 2/16 | 39/68 |
| U23 closing (NFR-04) | (this PR) | see PR | pending | see PR | — (NFR-04 EVIDENCED) | no FR change | 2/16 | 39/68 |

## State at stop (checker v1.3 on main after U22; NFR-04 per U23)
- PHASE1_HIGH_ACCEPTED = 2/16 (FR-02, FR-09). ABSENT = 0. REACHABLE_TESTED = 14.
- Exclusively named-dependency-gated: FR-04, FR-05, FR-07, FR-13, FR-14, FR-15, FR-16, FR-19, FR-20, FR-23, FR-27, FR-30 (12).
- Held by a Sponsor decision (plus named dependencies): FR-01 (SQ-1), FR-06 (SQ-2).
- CRITERIA_EVIDENCED = 39/68; criteria carrying a named dependency = 26.
- NFR: 1/13 EVIDENCED (NFR-04).

SPONSOR_QUEUE:
- SQ-1 AC-FR-01-03 — SPONSOR_PRODUCT_DECISION. Do pre-session events (registration, failed sign-in) count as account
  actions for the audit chain, and if so how is a tenantless security event chained (audit_event.tenant_id is NOT NULL;
  governed gap AUTH_EVENTS_OUTSIDE_AUDIT_CHAIN)? Everything else in AC-FR-01-03 is built (U20).
- SQ-2 AC-FR-06-01/-02 — SPONSOR_PRODUCT_DECISION. With remote consultation fail-closed until COUNSEL:REG-02, are
  AC-01/02 accepted on the capability proven with the gate opened in a test environment, or only once video runs in the
  served deployment? The capability is built behind the gate (U22).

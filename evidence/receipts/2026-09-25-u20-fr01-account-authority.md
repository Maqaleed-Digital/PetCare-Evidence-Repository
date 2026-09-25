# U20 · FR-01 server-held tenant authority, chained account actions, sign-out revocation; AC-FR-01-04 internal part, 2026-09-25

```
PROGRAMME=MVC-BUILD-RUNNER-001 v1.1   UNIT=U20   BASE_MAIN=ef51a479e28771aa4defc15026f44241c28d74c1 (U19 merged, PR #64)
BRANCH=build/u20-fr01-ac03
SELECTION (pass 2): FR-01 (1 dependency criterion, REACHABLE_TESTED) — before FR-06 (2) and FR-27 by the rule.
CRITERIA_CLOSED=[] (AC-FR-01-04 internal parts evidenced; its gap is now [DEPENDENCY] only — COUNSEL:L-2)
GAPS_REMAINING={AC-FR-01-03: [AUDIT, PERSISTENCE, TENANT_ISOLATION] — SPONSOR_QUEUE SQ-1 (pre-session account actions);
                AC-FR-01-04: [DEPENDENCY] — COUNSEL:L-2}
FR-01: REACHABLE_TESTED / EVIDENCE_INCOMPLETE (2/4) — unchanged count; AC-04 moved to dependency-only.
```

## Defects found and fixed (AC-FR-01-03 fails_if)
1. **Tenant authority was read from the token.** `read_session` returned the signed cookie's payload, whose `tenant_id`
   and `role` were then used at every authorisation decision ("tenant_id is read from a token … at an authorisation
   decision point"). It now returns the SERVER-HELD session record's tenant and role, and requires the identity's
   CURRENT membership to match — a moved or ended membership fails every older session closed (401
   SESSION_TENANT_STALE). Previously a session kept its old tenant's authority after the identity moved.
2. **Sign-out did not end the session.** It deleted the cookie but left the server record live, so a copied cookie
   stayed valid. Sign-out now revokes the server session.
3. **Session-bearing account actions were not in the audit chain.** Sign-in and sign-out are now chained
   (`account.signed_in` / `account.signed_out`, session actor, session id). Language and membership changes already
   were.

## Not registered — SQ-1
AC-FR-01-03 is NOT registered: "every account action is written to the audit chain" includes pre-session actions
(registration, failed sign-in) that have no tenant, and `audit_event.tenant_id` is NOT NULL. How a tenantless security
event is chained is SPONSOR_QUEUE SQ-1 (the repository's open governed gap AUTH_EVENTS_OUTSIDE_AUDIT_CHAIN). Everything
else in the criterion is now built and tested; SQ-1 is the only remaining question.

## Test changed because the requirement changed
`test_tenant_membership_postgres.py::test_the_target_route_authority_is_unchanged_after_a_move` reused the PRE-MOVE
cookie and expected it to keep working — the behaviour AC-FR-01-03 forbids. It now asserts the stale session fails
closed AND that a fresh session has the same role authority (the test's real claim: roles are not tenant-scoped).

## AC-FR-01-04 (COUNSEL:L-2) — internal part evidenced
No role in the catalogue is a pharmacy role; every non-veterinarian role is refused a POM dispense (with client headers
asserting "pharmacist"), each refusal audited; the class-scoped pharmacy authority itself awaits counsel.
Evidence {SERVED_APP_E2E, AUDIT}; DEPENDENCY not evidenced.

## Perturbations
```
P-AC03-TOKEN-TENANT             authority from the token again           -> authority test FAILS      ARMED
P-AC03-SIGNOUT-NO-REVOKE        sign-out leaves the session live         -> sign-out test FAILS       ARMED
P-AC03-SIGNIN-UNCHAINED         sign-in not chained                      -> chain test FAILS          ARMED
P-AC03-IDENTITY-DELETED-ON-END  (fixture-level) ending deletes identity  -> attributable test FAILS   ARMED
P-AC04-PHARMACY-ROLE            a 'pharmacist' role admitted             -> AC-04 test FAILS          ARMED
P-AC04-NONVET-DISPENSE          non-vet dispense allowed                 -> AC-04 test FAILS          ARMED
PERTURBATIONS=6 ARMED=6 VACUOUS=0
```
P-AC03-IDENTITY-DELETED-ON-END mutates the test's membership-end fixture (no product code deletes an identity); it
proves the attributability assertion would detect such a path.

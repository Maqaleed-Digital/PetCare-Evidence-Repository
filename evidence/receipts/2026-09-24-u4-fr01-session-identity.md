# U4 · FR-01 accounts — AC-FR-01-01: every served route authorised from the signed session, 2026-09-24

```
PROGRAMME=MVC-BUILD-RUNNER-001 v1.1   UNIT=U4   BASE_MAIN=301d1c7883aa83effbfa5c32bcc629a9924012a9 (U3 merged)
BRANCH=build/u4-fr01-accounts   SELECTION: FR-09 has no closable gap left (AC-03 needs FR-20/23 producers);
  FR-01 = 1 dependency criterion, REACHABLE_TESTED, lowest id
CRITERIA_CLOSED=[AC-FR-01-01]
GAPS_REMAINING (scope of the next FR-01 units):
  AC-FR-01-02 [AUDIT, SERVED_APP_E2E]   live practitioner-authority attribute at the moment of each regulated act
  AC-FR-01-03 [AUDIT, PERSISTENCE, TENANT_ISOLATION]   account actions into the audit chain — see SPONSOR_QUEUE
  AC-FR-01-04 [AUDIT, DEPENDENCY, SERVED_APP_E2E]   COUNSEL:L-2 (internal part buildable; DEPENDENCY never fabricated)
FR-01: REACHABLE_TESTED / EVIDENCE_INCOMPLETE (unchanged engineering status; one criterion closed)
```

## Defect measured and fixed
AC-FR-01-01 fails if "any served route accepts a role, actor or tenant asserted by the client". W1 finding F-3 held:
six handlers wrote the audit actor from a client `X-Actor-Id` header — book/get appointment, start/get consultation,
create note (also as `veterinarian_id`), sign note (also as `signed_by_actor_id`) — and the by-id reads had no tenant
predicate. Now (Rule 21, removed not validated): actor and role from `_actor(request)`; `get_appointment`,
`get_consultation`, note creation and note signing return 404 outside the session tenant (a note via its parent
session). Also: `/signin` ROLE_REDIRECT carried a dead non-canonical key `clinic_admin`; the canonical
`partner_clinic_admin` now routes to `/account`, its governed self-service surface (middleware
DOMAIN_CAPABILITY_PENDING_ROLE_BINDING). Checked and left as-is: `POST /audit/ui` prefixes client values
`client-asserted:` (never substituted for the session); `/api/auth/register` binds the requested role to the
server-held invite's `allowed_role` (mismatch → 400).

## Tests
```
petcare_api/tests/test_fr01_session_identity.py (served_app, 5)
  registered owner + vet (invite) and governed admin sign in and reach their surfaces
  registration role is bound to the invite
  spoofed X-Actor-Id ignored on appointment book, consultation start/view, note create/sign (records + audit)
  appointment / consultation / note records unreachable from another tenant (404)
  client X-Petcare-Role header grants nothing (403 on /audit/events)
petcare_web/__tests__/fr01-account.test.tsx (vitest, 5): sign-in routes owner→/owner, veterinarian→/vet,
  platform_admin→/admin, partner_clinic_admin→/account; register sends invite+role, never tenant/actor/user id
PERTURBATION: consultation start actor restored to the client header -> spoof test FAILS -> revert -> PASSES   ARMED
```
Note: tenant assignment in the served-app test is a fixture — the governed membership route refuses in memory
mode by design (503) and is proven against PostgreSQL in test_tenant_membership_postgres.py.

## Binding and evidence
- bindings FR-01: tests += test_fr01_session_identity.py; basis += 4 lines. Fitness unchanged (audit_actor_source
  stays NONE until AC-FR-01-03 chains account actions).
- evidence.json AC-FR-01-01: SERVED_APP_E2E, TENANT_ISOLATION (TEST) · UI (ARTEFACT fr01-account.test.tsx).

## Results
```
REGRESSION_LOCAL=1007 passed / 0 skipped · WEB_UNIT(local)=165 passed · TSC clean · served_routes current
M4: no FR lowered; ACCEPTED=[FR-02]
SCANNERS: SECRET_SCAN=CLEAN · ACTIVE_LITERAL_DEFAULT=0 · DIFF_CHECK=CLEAN
```

## SPONSOR_QUEUE
- **SQ-1 (AC-FR-01-03).** "every account action is written to the audit chain with the session actor". Account
  actions WITH a session (sign-in success, sign-out, membership change, language) can be chained. Pre-session events
  (registration, failed sign-in) have no tenant, and `audit_event.tenant_id` is NOT NULL — the repository records this
  as the open governed gap AUTH_EVENTS_OUTSIDE_AUDIT_CHAIN ("needs a governed answer on how a tenantless security event
  is recorded"). Decision needed: do pre-session events count as account actions for AC-FR-01-03, and if so, how is a
  tenantless security event recorded? The chaining of session-bearing account actions can be built meanwhile.

# MVC-EPC-D-001 v1.5 — Lane D unit D2c: J-O2 consent ledger, J-O3 profile + data export, J-O11 owner MFA

Authority: MVC-EPC-D-001 v1.5 [SPONSOR] + Sponsor rulings 2026-09-28 (resume at D2). Base: main `c47bb0a` (#85).
This lane registers no acceptance evidence; `requirements/acceptance/**` and `governance/**` are byte-identical.

## What was built
- **J-O2 consent (server-side, append-only).** `petcare_api/owner_consent.py` + migration `0057_epc_d2_owner_consent_ledger.sql`
  (`owner_consent_event`: INSERT only — UPDATE/DELETE refused by trigger; `privacy_notice` REVOKE refused by CHECK).
  Routes `GET /api/me/consents`, `POST /api/me/consents/{purpose}` {action GRANT|REVOKE}: caller's own ledger only,
  a no-op writes nothing, every change audited (`consent.granted` / `consent.revoked`). Purposes: privacy_notice (not
  revocable in-app — withdrawal is account closure via the erasure request), care_reminders, marketing_messages.
- **Self-registration records consent.** `POST /api/auth/self-register` requires `privacy_notice_accepted: true`
  (400 PRIVACY_NOTICE_REQUIRED before any identity exists) and appends a `privacy_notice` GRANT (origin
  self_registration). Invite registration is tenantless at that moment, so that owner acknowledges from /account.
- **J-O3 profile + export.** `GET/PUT /api/me/profile` — the write names only `full_name` (in-memory `set_full_name`;
  Postgres `UPDATE user_identity SET full_name … AND tenant_id`), so a profile edit cannot change role, tenant, email or
  credentials. `/api/me/export` (SQ-3 #11, step-up unchanged) now includes the consent history.
- **Web.** `components/account/AccountCenter.tsx` (ProfileCard, ConsentLedger, DataExportCard — server state only, the
  four data states via DataView, export through the Lane B step-up hook). `/account` mounts it; the browser-local
  ConsentStateView is superseded (component kept, no longer mounted). Role badge translated (X1). Design-system
  classes added: ds-stack, ds-muted, ds-list, ds-row--between, ds-badge.
- **J-O11 owner MFA** end-to-end on the existing /account/security (Lane B): enrol → confirm → ten recovery codes shown
  once → step-up with a recovery code → the same code refused (401).

## Defects found and fixed
- **D2C-REFUSALS-WITHOUT-CORS (real, product-wide).** `CORSMiddleware` was registered FIRST, so Starlette made it the
  innermost layer; the rate-limit (429) and step-up (403) middlewares answered OUTSIDE it with no CORS headers. A
  cross-origin browser saw a network error instead of `MFA_STEP_UP_REQUIRED` / `MFA_ENROLMENT_REQUIRED`, so the
  step-up dialog could never open. Lane B's web tests replay a mocked server contract and could not see it; the first
  full-stack journey (J-O3) did. Fix: CORS registered last (`_install_cors()`, outermost); `Content-Disposition`
  exposed for the export filename. Test `test_a_step_up_refusal_carries_cors_headers_so_the_web_origin_can_read_it`;
  P-D2C-REFUSAL-OUTSIDE-CORS ARMED.
- **X1 on /account and /account/security:** "(DPO)" removed from the Arabic string; the otpauth link read the literal
  "otpauth" (now translated); machine values (email addresses, the MFA key) marked `translate="no"`; the X1 scan skips
  `code` / `translate="no"` content and treats "Maqaleed Vet by VetiCare" as one brand token.
- **FR-09 guard held.** A `dir="ltr"` added to the DPO link failed the registered `language-fr09.test.tsx` (no LTR
  override) and was removed. That test file is unchanged; P-D2C-FR09-LTR-OVERRIDE records that it guards this.

## Tests changed (none registered as acceptance evidence)
- `test_epc_d2_self_registration.py` payloads carry `privacy_notice_accepted: True` (new server contract).
- `__tests__/account.test.tsx`, `__tests__/surface-states.test.tsx`: /account shows the server ledger (error state when
  unreadable) and the translated role — not the browser-local record and the raw role id.
- `e2e/pilot-path.spec.ts`: asserts the consent ledger and the ABSENCE of the legacy invite code (X6).

## Evidence
- Backend full suite: 1168 passed + the served-routes regeneration below (register test then passes).
- Postgres: `test_epc_d2_consent_postgres.py` (2) added to the CI PG list.
- Web: vitest 40 files / 212 tests; tsc clean.
- Full stack (Playwright → petcare_web → main:app → PostgreSQL), ar/en × 1280/390: 28/28. Journeys **5/53** (J-00,
  J-O1, J-O2, J-O3, J-O11); screens **3/107** (PUB-01, PUB-07, CO-15). Test-based PASS (D2-SCREEN-PASS-IS-TEST-BASED).

## Generated artefacts (Sponsor ruling 4)
| File | Before sha256 | After sha256 | Generator |
|---|---|---|---|
| requirements/served_routes.json | 74a08840fb3feb262ba033f162aeb88b1523f84563b59bc636dd39987f2a3b71 | d91c8bc6be0cc4b2de6c9a4020382ad9b14b8830c569393c1736050624d6a6da | `tools/list_served_routes.py main:app` (memory-mode env) |
| requirements/status.json | 2e0cad7635961480e7c790d34b4552c1687310c69e3d8878edcd72bad5300709 | 9e4c9d5e1a746f906e0b7e4f3fbdc0aeb6ccfeadfd88b3a85307076b11d4220b | `tools/check_register.py` |

Diff inspected: +4 routes (GET /api/me/consents, POST /api/me/consents/{purpose}, GET /api/me/profile, PUT
/api/me/profile); status.json changes only `served_route_count` 117 → 121. No FR/NFR status change (D4).

## D3
D3_PLACEHOLDER

## Findings
- D2C-CONSENT-ENFORCEMENT: `care_reminders` is recorded, not enforced on FR-23 dispatch — coupling a recorded choice
  to delivery is a product rule not ratified here. Recorded, not built.
- D2C-INVITE-CONSENT-DEFERRED: invite-registered identities are tenantless at registration; their privacy-notice
  acknowledgement is captured from /account after tenant assignment.
- D2C-CONSENTSTATEVIEW-SUPERSEDED: component and its unit test remain; retire with the pilot browser record.

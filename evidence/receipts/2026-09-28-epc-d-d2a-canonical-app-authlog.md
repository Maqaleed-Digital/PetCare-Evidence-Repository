# MVC-EPC-D-001 v1.5 · Lane D · D2a — canonical web app (X-24), auth-log PII (X-23), X-22 root cause, 2026-09-28

```
LANE=D   UNIT=D2 (slice a; D2 is delivered in slices, each merged under D1–D6)   BASE=e1a6e2db8a57ea33301041afba03a27ee458c2f0
RESUME: Phase V — origin/main == e1a6e2d; ledger: D0 DONE (#82 525e849), D1 DONE (#83 e1a6e2d); resume at D2.
        D0_REEXECUTED=NO  D1_REEXECUTED=NO. Instrument v1.5 unchanged (as pasted 2026-09-27) + Sponsor rulings 2026-09-28.
ACCEPTANCE_COUNTS=UNCHANGED (2/16, 42/68, 3/13)
```

## X-24 — one canonical, CI-tested web app (ruling ONE_CANONICAL_CI_TESTED_WEB_APP)
1. Web-app directories: `petcare_web` (Next.js product app) and `petcare-web` (create-next-app prototype: PH-UI admin /
   owner / vet / pharmacy / emergency dashboards, 79 tracked files, boilerplate README).
2. CI: every `working-directory` in `.github/workflows/verify.yml` is `petcare_web` (typecheck, unit tests, Playwright
   install, responsive regression, full-stack journey suite). No workflow references `petcare-web`.
3. D0 full-stack harness: `petcare_web/playwright.full.config.ts` runs `npx next dev` in `petcare_web` against
   `tools/e2e_stack.py` (FastAPI `main:app` on PostgreSQL).
4. Both therefore resolve to ONE canonical product app: `petcare_web`. All D2–D5 product screens are built there only.
5. `petcare-web` is not modified or deleted. It has no surviving product purpose found (no CI, no deploy wiring for it
   in the product pipeline, prototype dashboards superseded by petcare_web); RETIREMENT RECOMMENDED for a separately
   authorised cleanup (to be restated in the D9 receipt).
6. Guard: `tests/governance/test_canonical_web_app.py` — CI may build/test only `petcare_web`; the harness serves
   `petcare_web` and main:app; `petcare-web` is frozen by content digest
   42d89e2ed1b59ac23030488be92e525cd5f0d5cc37ba1f8ad20300910aa4424d, so product UI cannot land there unnoticed.

## X-23 — no raw email in authentication logs (ruling MUST_CLOSE_IN_D2)
- All authentication log paths: every AUTH_EVENT line is written by ONE sink, `routers/auth.py _log_auth_event`
  (called from sign-in ×4, register ×10, vet licence submission, /me, sign-out). A repository-wide search found no
  other log call carrying email, name or phone.
- Fix: the log line is `_log_safe(detail)`: `email` becomes `email_ref` = "email-sha256:" + sha256(lower(email)) — the
  SAME reference the SQ-1 platform identity chain uses as its subject, so a log line still correlates with the chain
  event. The chain still receives the full detail it needs. Invite codes were already reduced to `invite_ref` (D1).
- Test `petcare_api/tests/test_epc_d2_auth_log_pii.py` (served_app): register (refused + success), sign-in (wrong
  password, unknown identity, success), /me, sign-out → ≥6 AUTH_EVENT lines, no raw address and no "@" at all;
  authentication still works; the unknown identity's log reference equals its platform-chain `subject_ref`.

## X-22 — root cause (ruling TZ_UTC_IS_NOT_AN_ACCEPTED_FIX) — remains OPEN
- Failing frozen test: `test_fr05_licence.py::test_a_veterinarian_cannot_register_without_licence_details` (U10),
  between 00:00 and 03:00 Asia/Riyadh only.
- Product semantics (U10, deliberate and documented): a licence is valid THROUGH `expires_on`, lapsing at the start of
  the next UTC day (`licences.py:71`); registration refuses `expires_on < datetime.now(UTC).date()`
  (`routers/auth.py:484`).
- The SAME frozen file pins those UTC semantics: line 142 asserts a grant `expires_at` equal to (expiry+1 day) at UTC
  midnight; line 169 asserts the refusal reason "expired at <expiry+1>T00:00:00+00:00".
- Root cause: FIXTURE GENERATION in the frozen test — it derives "yesterday" from the test host's LOCAL calendar
  (`date.today()`), while the product's business date is the UTC calendar date. On a UTC+3 host, 00:00–03:00 local,
  local-yesterday equals UTC-today, so an unexpired (by the product's rule) licence is submitted as "expired".
- Not a product defect under the current rule, and not closable inside Lane D without authority:
  (a) correcting the fixture requires editing a frozen U10 test; (b) moving licence dates to Asia/Riyadh would
  invent a semantic absent from the BRD / ratified pack / register / Sponsor acts (searched; none states a business
  timezone) AND contradict U10's documented rule and the two frozen UTC assertions.
- SPONSOR_QUEUE X-22: choose (A) authorise a fixture-only correction of the frozen U10 test (derive dates in UTC,
  assertions unchanged), or (B) ratify Asia/Riyadh as the licence business calendar and authorise the dependent frozen
  assertions to follow. No TZ override is used as closure.

## Perturbations — evidence/replay/2026-09-28-epc-d/perturb_epc_d_d2a.py
P-D2A-AUTH-LOG-RAW-EMAIL · P-D2A-AUTH-LOG-NO-CORRELATION · P-D2A-PRODUCT-UI-IN-PROTOTYPE-APP (new tracked file) ·
P-D2A-CI-TESTS-PROTOTYPE-APP → ARMED=4 VACUOUS=0.

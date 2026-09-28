# MVC-EPC-D-001 v1.5 · Lane D · D2b — J-00 landing, J-O1 owner self-registration, 2026-09-28

```
LANE=D   UNIT=D2 (slice b)   BASE=f2a6e21ac0f303b612da1689be73459c97149cef (D2a merged, PR #84)
SPONSOR RULING 1: owner self-registration BUILT FULLY behind PETCARE_OWNER_SELF_REGISTRATION — production default OFF,
                  test/staging ON; both states tested. This does not authorise public production registration.
JOURNEYS PASS 2/53 (J-00, J-O1 — ar/en × 1280/390, full stack) · SCREENS PASS 2/107 (PUB-01, PUB-07)
ACCEPTANCE_COUNTS=UNCHANGED (2/16, 42/68, 3/13)   MIGRATIONS 60 -> 61 (0056)
```

## Server
- Switch `PETCARE_OWNER_SELF_REGISTRATION` (default OFF): `/api/auth/self-register` answers 404 SELF_REGISTRATION_DISABLED
  and creates nothing — no API bypass; the invite-only pilot (/api/auth/register) is unchanged and authoritative.
  `GET /api/auth/registration-options` tells the web which to offer.
- When ON: the owner's tenant comes from SERVER configuration `PETCARE_SELF_REGISTRATION_TENANT` (must exist and be
  assignable, else 503) — never from the request (W0-C preserved: no caller-supplied tenant authority). Password ≥ 10.
  A pending `email_verification` row blocks sign-in (403 EMAIL_NOT_VERIFIED) until `/api/auth/verify-email`.
- Governed email adapter `petcare_api/adapters/email.py`: interface + FAKE (labelled, delivers nothing; JSONL outbox for
  the journey suite; refused when PETCARE_DEPLOYMENT_ENV=production) + UNCONFIGURED default (every send raises → the
  feature fails closed with 503 BEFORE any identity is created). D6 completes its contract tests.
- Account tokens (migration 0056): 256-bit, stored as sha256 only, single use, verification 24 h / reset 30 min.
- Password reset: `/password-reset/request` answers 202 for any address (no enumeration); `/confirm` sets the password,
  revokes every session of the identity, consumes the token.
- Audit: owner_self_registered, email_verified, password_reset_completed are on the SQ-1 platform identity chain; the
  auth log carries only email references (X-23).

ROUTES ADDED (D4; ruling 4): GET /api/auth/registration-options · POST /api/auth/self-register · POST /api/auth/verify-email ·
POST /api/auth/password-reset/request · POST /api/auth/password-reset/confirm.
GENERATED ARTEFACTS (ruling 4; generator: `PYTHONPATH=petcare_api python3 tools/list_served_routes.py main:app` and
`python3 tools/check_register.py`; never hand-edited; diff inspected — only `served_route_count` 112 -> 117 in status):
- requirements/served_routes.json 06f2641483c6497828b2bb26d290fdf0d6432fe97a34f6c220b84f80bbe1b1ae -> 74a08840fb3feb262ba033f162aeb88b1523f84563b59bc636dd39987f2a3b71
- requirements/status.json 53323d1d2ba2682110f4d3bc82956ba5a473ac70fbfe6fa9d8a54c73c6ccc0a5 -> 2e0cad7635961480e7c790d34b4552c1687310c69e3d8878edcd72bad5300709
- requirements/acceptance/**, register.yaml, authority/**: byte-identical. No FR/NFR status change.

## Web (petcare_web only — X-24)
- Landing (PUB-01): owner and veterinarian entry points, "Create an account" -> /signup, PDPL notice with /privacy.
- /signup (self-registration form only when the server reports ON; otherwise the invite path), /verify-email,
  /forgot-password, /reset-password; sign-in shows EMAIL_NOT_VERIFIED and links "forgot password". /register (invite
  path) is unchanged in behaviour — its registered FR-05 UI evidence test is untouched.
- X1 defects fixed: "DPIA" inside Arabic strings (pilot badge, PDPL notice) and the nav's raw role id in Arabic mode.
- X6 defect fixed: the register page stored the invite code in localStorage (`vc_consent.origin_invite_code`); the
  consent record now keeps only `origin: 'pilot_invite'`, older records are read without it.

## Journeys (petcare_web/e2e-full, full stack, 4 projects)
- [J-00] @S:PUB-01 — Arabic default for a new visitor (no stored preference), entry points, PDPL notice, no untranslated
  word in Arabic (allow-list: brand/technical tokens only).
- [J-O1] @S:PUB-07 — self-register (UI) -> sign-in refused until verified -> verification link from the FAKE email
  outbox -> sign in -> dismiss first-run guide -> signed-in nav fully Arabic -> sign out (server session gone) -> forgot
  password -> reset link -> new password -> old password refused -> new password signs in.
- Report fix: the journey-id pattern did not match `J-00` (required a letter); corrected.

## Tests / perturbations
Backend: test_epc_d2_self_registration.py (5, both switch states, fail-closed, reset, expiry, fake-in-production) ·
test_epc_d2_account_tokens_postgres.py. Web: epc-d2-x1-x6.test.tsx (X6 storage, X1 nav).
evidence/replay/2026-09-28-epc-d/perturb_epc_d_d2b.py → ARMED=13 VACUOUS=0 (incl. full-stack P-D2B-LANDING-ENGLISH-IN-ARABIC).

## Findings
- D2B-GUARD-CAUGHT-PASSWORD-SHAPED-ASSIGNMENT (fixed before PR): `test_seed_retirement.py::test_seed_02c…` flagged the
  constant tuple `EMAIL_VERIFICATION, PASSWORD_RESET = "…", "…"` as a password-named literal assignment; renamed to
  PURPOSE_VERIFY / PURPOSE_RESET. The guard is unchanged.
- D2-DEAD-LINK: owner home "Book appointment" is `href="#"` (J-O5 builds booking).
- D2-SCREEN-PASS-IS-TEST-BASED: SCREENS.md PASS currently reflects journey tests; the G2–G8 gate checks per screen are
  added as those gates are built (G3 axe, G2 Lighthouse, …) before any screen can count toward X-01.
- D2B-D3-CAUGHT-FROZEN-LITERAL-EDIT (fixed in-PR, commit b5ed42a): the first D3 replay of this head reported
  `perturb_u26.py` rc=1 — P-REGISTRATION-UNCHAINED could no longer find its byte-exact target because D2b had rewritten
  the `_PLATFORM_CHAINED` literal, so four committed ARMED items read MISSING. The literal is restored byte-identical and
  the three D2 events are added as a separate union; u26 replays 6/6 ARMED. The corpus is unchanged (no script edited).
- D2B-STALE-X6-ASSERTION (fixed in-PR): legacy mocked `e2e/pilot-path.spec.ts` asserted the invite code IS shown on
  /account — the X6 defect this unit closes. Not registered evidence; now asserts the code is absent.

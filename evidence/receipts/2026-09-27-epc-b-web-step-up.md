# MVC-EPC-B-001 · Lane B — web step-up UX (MVC-EXTERNAL-PRODUCTION-CLOSURE-001), 2026-09-27

```
PROGRAMME=MVC-EXTERNAL-PRODUCTION-CLOSURE-001   LANE=B   INSTRUMENT=MVC-EPC-B-001 v1.0
INSTRUMENT_SOURCE=Notion "Lane B — Web Step-Up UX runner instrument (DRAFT)" (child of the Programme Charter, 27 Sep 2026);
  ISSUED by the Sponsor's [SPONSOR AUTHORITY] message of 2026-09-27 directing execution of that filed instrument
BASELINE=38bc79179ab78c181624252cfdeeed01beb136e7   BRANCH=lane-b/web-step-up-ux   CODE_COMMIT=3f2b4f4af13b8df5fe17a3d829357ecdb562495a
SQ3_ACT_SHA256=16efd2330f4b04e15aaf7cc04684897b7bd958feeb88c23a4133794e22f585cc (consumed, unchanged)
SCOPE=outside the 68 criteria / 13 NFRs; ACCEPTANCE_COUNTS=UNCHANGED (2/16, 42/68, 3/13). Closes finding U28-WEB-STEP-UP-PROMPT.
```

## Phase V
- V1 repo Maqaleed-Digital/PetCare-Evidence-Repository; common dir …/petcare-evidence-repository/.git; worktree petcare-wt-build.
- V2 origin/main == BASELINE (PASS). V3 tracked tree clean; branch from origin/main.
- V4 SERVER CONTRACT (from code, petcare_api/main.py at BASELINE):
  - step-up refusal — `_step_up_refusal` L3025–3032: HTTP 403, `{"detail": {"error": "MFA_STEP_UP_REQUIRED", "operation": "<METHOD /template>", "always_fresh": <bool>}}`;
    no active factor → `{"detail": {"error": "MFA_ENROLMENT_REQUIRED", "operation": …}}`. Middleware `enforce_mfa_step_up` L3046;
    in-route supply check via `_require_step_up` (same body). Machine-readable `detail.error` distinguishes it from every other 401/403 → no HALT.
  - step-up `POST /api/me/mfa/step-up` L3139 {code} → 200 `{"stepped_up": true}`; bad code 401 MFA_CODE_INVALID (L3120).
  - recovery `POST /api/me/mfa/recovery` L3152 {code} → 200 `{"stepped_up": true, "single_use": true}`; invalid 401 RECOVERY_CODE_INVALID (L3165).
  - enrolment `POST /api/me/mfa/enrol` L3082 {factor?, password?}: no active factor → 401 PRIMARY_REAUTHENTICATION_REQUIRED without a
    valid password (L3104); active factor → always-fresh step-up refusal (403, operation ENROL); SMS → 400 MFA_FACTOR_NOT_SUPPORTED (L3091);
    success → `{"otpauth_uri": …}` (L3110). Confirm `POST /api/me/mfa/confirm` L3123 → `{"confirmed": true, "recovery_codes": [10]}` (L3136);
    already confirmed → 409 (L3131).
  - protected operations: `petcare_api/mfa.py` SQ3_OPERATIONS; always-fresh items 5/8/9/12/13 (mfa.py L65); freshness 900 s (L29).
  - no endpoint reports step-up state to the client (none exists) — the client learns only from refusals, which is sufficient.
  - responses recorded from the real app at BASELINE into `petcare_web/__tests__/fixtures/epc-b-server-contract.json`; otpauth secret and
    recovery codes replaced by synthetic placeholders before writing (no real code/secret in any fixture).
- V5 BASELINE: web 193 passed, tsc clean; checker output == requirements/status.json (sha256 15ffcb4c04ba97801307be65810807290c5949e5303b0da0c56f11214ecec31a);
  served_routes.json sha256 92d43021baaec0ab10bcda1641a5166cac38b6a19f77f37b066bf2efd3861ec7; corpus 184 ARMED (non-ARMED set below).

## Build (web client only)
- `lib/stepUp.ts` — `withStepUp`: react only to the server's 403 refusal; prompt; retry the ORIGINAL request once; a second refusal →
  `step_up_failed` (shown, never re-prompted); `MFA_ENROLMENT_REQUIRED` → `enrolment_required`. No timer, cache or flag (B2).
- `components/StepUp.tsx` — `useStepUp()` + dialog: TOTP or recovery code; code only in component state, cleared on every submit, never
  stored/logged (B3); focus moved in and trapped, Escape cancels, labelled input, errors `role=alert` (B7); Arabic/RTL default (B6);
  `EnrolmentRequiredNotice` routes to /account/security (B5).
- `app/account/security/page.tsx` — enrolment: server chooses re-authentication (factorless) or existing-factor step-up (replace) (B4);
  ten codes shown once with copy/download, dropped from memory on dismissal; controlled inputs cleared on submit.
- Wired: `app/vet/prescriptions/page.tsx` (prescribe) and `app/pharmacy/page.tsx` (dispense); `app/globals.css` dialog styles.
- DEFECT FOUND AND FIXED IN SCOPE: the enrolment password/code inputs were uncontrolled and `form.reset()` did not clear them — a wrong
  password was concatenated with the next attempt ("nopepw"). Now controlled and emptied on submit.

## Coverage
SENSITIVE_SERVED_ACTIONS_COVERED (web surfaces that perform an SQ-3 operation): POST /api/prescriptions (item 2);
POST /api/prescriptions/{prescription_id}/dispense (item 1); POST /api/me/mfa/enrol (item 8, always-fresh) + /confirm.
Served SQ-3 operations with NO web surface today (nothing to wire; the served middleware still protects them): note signing (3),
practitioner authority grant/revoke/licence verify (6), tenant membership (7), MFA reset request/approve (9), bulk exports (10),
POM supply via /api/inventory/supplies (1, in-route). Any future web caller gets the behaviour by using `useStepUp().stepUpFetch`.
NOT_CURRENTLY_SERVED (server): SQ-3 items 4, 5, 11, 12, 13, 14, 15.

## Tests — `petcare_web/__tests__/epc-b-step-up.test.tsx` (10, all pass)
refusal → prompt → one retry of the identical request, result used · second refusal → error, no loop · always-fresh prompts on every attempt ·
recovery code works once, not retained (DOM, storage, cookie, console) · no TOTP code in storage/console/other requests; wrong code
announced and cleared · pending re-enrolment → enrolment link, no prompt · dispense via step-up + retry · Arabic/RTL, aria-modal, focus trap,
Escape cancels without retry · factorless enrolment → re-authentication; ten codes once, never again; secret gone after confirm ·
replace factor → existing-factor step-up. FINDING NO_E2E_HARNESS: the Playwright suite mocks the backend at the network layer; the web
tests therefore answer with responses recorded from main:app (fixture above).

## Perturbations — `evidence/replay/2026-09-27-epc-b/perturb_epc_b.py`
Lane-specific directory: the instrument's `<today>` (2026-09-27) directory already exists and existing replay dates may not change; the
corpus glob `evidence/replay/*/perturb_*.py` still includes it.
```
P-AUTO-RETRY-WITHOUT-STEP-UP  P-RETRY-LOOP  P-CLIENT-TIMER-SKIPS-PROMPT  P-CODE-PERSISTED-TO-STORAGE  P-CODE-LOGGED
P-RECOVERY-CODES-REDISPLAYED  P-FACTORLESS-ENROLMENT-WITHOUT-REAUTH  P-PENDING-REENROLMENT-BYPASS  P-ENGLISH-STRING-IN-ARABIC-MODE
ARMED=9 VACUOUS=0
```

## E-rules (measured on a fresh detached checkout of CODE_COMMIT 3f2b4f4)
- E2 PASS — 9/9 lane perturbations ARMED.
- E3 PASS — the COMPLETE committed corpus replayed: 26 scripts (every evidence/replay/*/perturb_*.py). 193 ARMED = baseline 184 + 9 new;
  no perturbation changed state between BASELINE and head. The non-ARMED set is IDENTICAL at BASELINE and head and predates this lane:
  three first attempts recorded VACUOUS by their own unit receipts (U12 P-AC02-NO-TIMESTAMP, U14 P-AC03-PAID-UNCONFIRMED,
  U21 P-AC02-NONVET-SUPPLY — each superseded in its receipt by an ARMED redesign that replays ARMED), and the historical
  `2026-09-26/perturb_u25.py`, which stops on anchor drift since U28 (superseded by `2026-09-27/perturb_u25_retargeted.py`, 6 ARMED,
  per the v1.3 R2-fix receipt; editing it is forbidden to this lane). 1 SUPERSEDED (P-RUNNER-CHOSEN-WINDOW, by SQ-3).
- E4 PASS — diff = web client source, web tests (+ recorded fixture), this lane's perturbation script, NEW receipts only.
- E5 PASS — canonical checker output byte-identical to BASELINE; requirements/status.json byte-identical; served routes byte-identical;
  `git diff BASELINE..head -- petcare_api petcare_runtime requirements governance` empty.
- E6 PASS — no mandatory stop (no plaintext code/secret in fixtures or logs; no server change; no production/cloud/live act).
- E1 — CI on the final head: recorded in the PR / closing checkpoint (a receipt cannot carry its own CI result).
Regression on 3f2b4f4: backend 1142 passed / 0 skipped; web 203 passed; tsc clean; governance scans 0/0/0.
The only change after CODE_COMMIT is this receipt file.

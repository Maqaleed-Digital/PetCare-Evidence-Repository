# U25 · NFR-08 MFA step-up mechanism — built, NOT registered (SQ-3), 2026-09-26

```
PROGRAMME=MVC-BUILD-RUNNER-001 v1.2   UNIT=U25   BASE_MAIN=6e7479ed1f1c15f78ba18297d4c8dbb6d8e676d9 (U24 merged, PR #70)
BRANCH=build/u25-nfr08-mfa
NFR-08: EVIDENCE_INCOMPLETE (unchanged) — the ratified evidence_definition ("role enforcement and MFA on sensitive
  operations"; ratified_text EMPTY) does not name the sensitive operations, the step-up freshness window or recovery.
  Per v1.2: build the mechanism, choose none of them, register nothing -> SPONSOR_QUEUE SQ-3.
```

## Build
- `mfa.py`: TOTP per RFC 6238 (HMAC-SHA1, 30 s, 6 digits, ±1 step), constant-time comparison, single-use codes
  (last used step stored; PostgreSQL update is atomic). No SMS factor (EXTERNAL:SMS_GATEWAY).
- Secret storage: AES-256-GCM ciphertext only (`cryptography==44.0.2` added to both requirement files — no hand-rolled
  crypto); key resolved lazily through the governed secret provider (`PETCARE_MFA_KEY_SECRET_ID`, default
  `PETCARE_MFA_ENCRYPTION_KEY`), unavailable key -> 503 fail closed; the secret is returned once as an otpauth URI and
  never logged. Migration 0052: `mfa_factor`, `mfa_step_up` (bound to one server session).
- Routes: `POST /api/me/mfa/enrol`, `/confirm`, `/step-up`. Enforcement middleware: a request whose route template
  ("METHOD /path") is in `PETCARE_MFA_SENSITIVE_OPERATIONS` needs a confirmed factor and a step-up of THIS session no
  older than `PETCARE_MFA_STEP_UP_MAX_AGE_SECONDS`.
- NOT chosen by the runner: the operation list (default EMPTY — nothing enforced), the freshness window (NO default;
  operations configured without it fail closed at startup), recovery (not built).

## Tests (controls; not evidence)
RFC 6238 vectors · enrol / wrong code / confirm / replay refused / secret absent from logs and stored as ciphertext ·
with ONE operation and a window configured in-test: not enrolled -> MFA_ENROLMENT_REQUIRED, no step-up ->
MFA_STEP_UP_REQUIRED, after step-up -> allowed, another session of the same person -> refused, after the window -> refused ·
policy defaults (empty / none) and fail-closed configuration · PG: ciphertext only; 8 concurrent uses of one step -> exactly 1.

## Perturbations
```
P-BYPASS-STEP-UP             middleware never enforces            -> FAILS  ARMED
P-STEP-UP-NOT-SESSION-BOUND  any session of the person counts     -> FAILS  ARMED
P-NO-FRESHNESS               step-up never expires                -> FAILS  ARMED
P-REPLAY-ALLOWED             a code can be reused                 -> FAILS  ARMED
P-RUNNER-CHOSEN-WINDOW       a default window (900 s) invented    -> FAILS  ARMED
P-PLAINTEXT-SECRET           secret stored unencrypted            -> FAILS  ARMED
P-PG-REPLAY-RACE             PG single-use guard removed          -> PG FAILS  ARMED
PERTURBATIONS=7 ARMED=7 VACUOUS=0
```

## SPONSOR_QUEUE SQ-3 (new)
NFR-08 — which operations are "sensitive" (the route list), the step-up freshness window, and the recovery path for a
lost factor. Needed to enforce and evidence NFR-08. Safely built meanwhile: the whole mechanism (above). Class:
SPONSOR_PRODUCT_DECISION.

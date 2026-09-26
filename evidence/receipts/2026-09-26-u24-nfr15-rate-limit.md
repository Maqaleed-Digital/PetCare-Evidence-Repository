# U24 · NFR-15 API rate limiting — EVIDENCED, 2026-09-26

```
PROGRAMME=MVC-BUILD-RUNNER-001 v1.2   UNIT=U24   BASE_MAIN=591539d0e9c9cdba380fabbe2ed9a37955eca66a (GA-1 acts, PR #69)
BRANCH=build/u24-nfr15-rate-limit
NFR-15: EVIDENCE_INCOMPLETE -> EVIDENCED (ratified evidence_definition: served-app test that excess requests are throttled
  and normal traffic is not; NON_PROD; dependency NONE). No FR state changed.
```

## Build (binding parameters: ratified NFR-15 text + v1.2 U24)
- `ratelimit.py`: 100 requests/minute per authenticated principal (principal from the VALIDATED SESSION), 30/minute per
  anonymous client IP, fixed one-minute windows; excess -> 429 with `Retry-After` (seconds to the window's end).
- Client IP = TCP peer; `X-Forwarded-For` honoured ONLY when the peer is on the explicit trusted-proxy list
  (`PETCARE_TRUSTED_PROXIES`, default EMPTY), taking the right-most untrusted hop.
- Shared state: `rate_limit_counter` (migration 0051), one row per (bucket, minute), incremented by a single atomic
  `INSERT … ON CONFLICT DO UPDATE … RETURNING` — every worker/process shares the count. Memory mode (non-production)
  uses an in-process counter like every other memory-mode repository.
- Enforced by an HTTP middleware on `main:app` — every served route.
- Configurable (ratified): `PETCARE_RATE_LIMIT_PRINCIPAL_PER_MIN` / `_ANONYMOUS_PER_MIN`; an invalid value FAILS CLOSED at
  startup. Auditable (ratified): `GET /api/admin/rate-limits` (platform admin) returns the effective limits and their
  source; startup logs the policy; the first excess of an authenticated principal in a window is chained
  (`rate_limit.throttled`).
- Test harness: the repository-root conftest configures high limits for suites that are not about rate limiting (the
  real-time tests poll thousands of times per minute). The NFR-15 tests run the DEFAULT policy (`Policy.from_env({})`).

## Evidence (NFR_EVIDENCE)
`test_nfr15_rate_limit.py`: principal 100 ok / 101st 429 with Retry-After, spoofed `X-Actor-Id` ignored, second principal
unaffected, window reset, throttle audited · anonymous 30 ok / 31st 429 with spoofed XFF ignored · default policy is the
ratified one and configuration is validated. Controls (not registered): trusted-proxy XFF; PG two-worker shared count
(`test_nfr15_rate_limit_postgres.py`, 101 concurrent hits across two pools -> counts 1..101, exactly 100 allowed).

## Perturbations
```
P-RAISE-PRINCIPAL-LIMIT     default 100 -> 150                    -> FAILS  ARMED
P-RAISE-ANONYMOUS-LIMIT     default 30 -> 60                      -> FAILS  ARMED
P-KEY-BY-HEADER-IDENTITY    principal from X-Actor-Id header      -> FAILS  ARMED
P-TRUST-ANY-FORWARDED-FOR   XFF honoured from any peer            -> FAILS  ARMED
P-NO-429                    excess answered 200                   -> FAILS  ARMED
P-LOST-UPDATE               upsert resets instead of incrementing -> PG FAILS  ARMED
PERTURBATIONS=6 ARMED=6 VACUOUS=0
```

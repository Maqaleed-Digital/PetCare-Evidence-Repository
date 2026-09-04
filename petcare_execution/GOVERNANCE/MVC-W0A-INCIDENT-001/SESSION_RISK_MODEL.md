# Session risk model — `petcare_api/routers/auth.py`

Read-only analysis of the current implementation. No forged token was generated.

```
SESSION_MECHANISM            = SIGNED COOKIE (itsdangerous URLSafeTimedSerializer)
                               cookies: petcare_session (HttpOnly), petcare_role (NOT HttpOnly)
SIGNING_ALGORITHM            = itsdangerous default HMAC (timestamped, URL-safe)
SESSION_TTL                  = 28800s (8 hours) — COOKIE_MAX_AGE
REFRESH_TTL                  = none — no refresh token exists
SERVER_SIDE_SESSION_STORE    = NONE (stateless; _users is an in-memory pilot store)
REVOCATION_MECHANISM         = NONE — no jti, no deny-list, no logout invalidation
KEY_ROTATION_BEHAVIOUR       = single key, no fallback/previous-key list
OLD_KEY_ACCEPTANCE           = NO — the serializer verifies against SECRET_KEY only
SESSION_INVALIDATION_CAPABILITY = ROTATION IS INVALIDATION
```

## Two consequences that matter

**TTL is not a mitigation while a key is compromised.** `max_age` is enforced
server-side at `loads(token, max_age=COOKIE_MAX_AGE)`, so an *individual* token
expires after 8 hours. But anyone holding the signing key can mint a fresh token
at will. The 8-hour ceiling bounds a stolen token, not a stolen key.

**Rotation alone achieves global invalidation.** Because there is exactly one key
and no previous-key acceptance list, changing `SECRET_KEY` makes every previously
issued cookie fail signature verification immediately. No separate session-purge
step is required, and none is available. This is a favourable property for
remediation: IR-06 collapses into IR-04.

## Forgery impact, conditional

The session payload carries identity, role and (post-W0-C) tenant. A party holding
the signing key could mint a cookie asserting any user, any role, any tenant, and
it would validate as legitimate — including against the W0-B authorization binding,
which is precisely the ordering hazard W0-A's docstring names.

```
FORGERY_IMPACT_IF_KEY_WAS_LIVE = CRITICAL
FORGERY_IMPACT_REALISED        = UNKNOWN — conditional on a deployment that
                                 carried the vulnerable code with SECRET_KEY unset;
                                 no such deployment is evidenced (see
                                 VULNERABLE_SERVING_WINDOW.md)
```

The severity is unchanged and high. What is unproven is whether the precondition
ever obtained.

## Current source state

```
CURRENT_SOURCE_HARDCODED_KEY    = NO
CURRENT_SESSION_KEY_ENFORCEMENT = FAIL-CLOSED at import (RuntimeError)
                                  rejects unset, blank, AND the retired literal
CURRENT_SOURCE_FIXED            = YES (local canonical branch only — NOT on origin/main)
```

Verified armed, not vacuous: reintroducing `os.getenv("SECRET_KEY", <default>)`
into an isolated copy fails 3 guards —
`test_t_sec_01_unset_secret_refuses_to_start`,
`test_t_sec_04_no_literal_fallback_in_source`,
`test_w0a_no_getenv_supplies_a_default_signing_key`.
The canonical tree was not modified (`MODIFIED_TRACKED_FILES=0`).

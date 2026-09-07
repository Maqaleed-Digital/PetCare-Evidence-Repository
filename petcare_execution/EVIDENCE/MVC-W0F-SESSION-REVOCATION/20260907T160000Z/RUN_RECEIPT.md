# MVC-W0F-SESSION-REVOCATION — AC-7 server-side revocable sessions

**Base:** `ad10910cdc4b69be743490eb2b6fef50aaa7cb6f` (after PR-A / #18)
**Scope:** NON_PRODUCTION_ONLY · PR-B

## The decision AC-7 required

The W0-F pack:

> Because there is one key and no fallback list, **rotating the key invalidates
> every existing session**. If W0-F introduces a server-side session store or a
> previous-key list, that property is lost and an explicit revocation path
> becomes mandatory. Whichever way it goes, it must be a decision, not a side
> effect.

```
W0F_SESSION_REVOCATION=SERVER_SIDE_STORE_WITH_EXPLICIT_REVOCATION_PATH
PREVIOUS_KEY_LIST=NOT_INTRODUCED
KEY_ROTATION_ROLE=EMERGENCY_SYSTEM_WIDE_ONLY
```

A server-side store is introduced. Key rotation therefore stops being the
revocation mechanism and becomes what it should always have been: an emergency,
system-wide capability. Per-user and per-session revocation happen in the store,
without touching the signing key.

**Why that matters more than it sounds.** Before this, revoking one compromised
session meant rotating the key and signing *everyone* out. A revocation whose
blast radius is the entire user base is one nobody actually uses — so in practice
sessions were not revocable at all. AC7-06 asserts the new property directly:
nothing in the store references `SECRET_KEY`, `_serializer`,
`URLSafeTimedSerializer` or `itsdangerous`, so revocation *cannot* have become
key-dependent by accident.

A previous-key acceptance list was deliberately **not** introduced. It would have
created a second, ungoverned revocation model sitting beside this one — the
outcome the pack's "not a side effect" wording warns against.

## What a signed cookie cannot establish

A validly signed cookie proves the payload was written by this service and not
altered. It cannot prove the session is *still* valid — that the user has not
signed out, been disabled, or had the session revoked. Signature integrity is a
statement about the past; session validity is a statement about now. That gap is
what the store closes, and it is why integration must consult the store even when
the signature verifies.

## Controls — AC7-01..06, all armed

| Control | Property | Result |
|---|---|---|
| AC7-01 | revoked session denied | PASS |
| AC7-02 | tenant-A session denied in tenant B | PASS |
| AC7-02b | cross-tenant *revocation* refused | PASS |
| AC7-03 | expired session denied server-side | PASS |
| AC7-04 | unknown session id denied | PASS |
| AC7-05 | revoking one user leaves another active | PASS |
| AC7-05b | revoke-all does not cross tenants | PASS |
| AC7-06 | revocation requires no key rotation | PASS |

Plus: no session may be created without a tenant (W0-C); revocation is idempotent
and does not overwrite the timestamp recording when it happened; and `tenant_id`
carries no default on any store operation — the W0-I finding applied here before
it could recur.

`get_active()` returns `None` for unknown, revoked, expired and cross-tenant
alike. The caller cannot distinguish them, deliberately: telling an attacker
whether a session id exists is a small oracle, and no legitimate caller needs the
difference.

## Perturbation — four probes, each biting its own control

| # | Violation | Controls that fired |
|---|---|---|
| P1 | active-check removed from `get_active` | 5 failed — AC7-01, 03, 05b, 06 |
| P2 | tenant match removed from `get_active` | 1 failed — **AC7-02 exactly** |
| P3 | user+tenant match removed from `revoke_all_for_user` | 2 failed — AC7-05, 05b |
| P4 | tenant match removed from `revoke` | 1 failed — **AC7-02b exactly** |

P2 and P4 each failing exactly one control is the useful signal: the tenant
guards are independent of the liveness guards rather than one broad check
reported four times.

Restored after every probe: 12 passed.

## Honest scope boundary — integration is NOT done

```
AC7_STORE_IMPLEMENTED=YES
AC7_CONTROLS_ARMED=YES
AC7_INTEGRATED_INTO_read_session=NO
```

This must not be read as AC-7 complete. The store exists and its semantics are
fixed and proven, but `read_session()` does not yet consult it, so **revoking a
session does not yet affect a live request.** Until integration lands, revocation
is a capability, not an enforcement.

Integration is deliberately separate because it changes authentication behaviour
for every request: sign-in must create a record and place its id in the payload,
and `read_session` must deny when the store says the session is not active. That
is a small change with a large blast radius, and it deserves its own step with
its own end-to-end controls rather than being appended here.

## Regression

```
serving API           82 passed   (was 70; +12 AC-7 controls)
governance + root    186 passed
runtime              247 passed
secret_scan          SCANNED=3828 ALLOWLISTED=0 FINDINGS=0  CLEAN
```

No existing test modified. `ASSERTIONS_WEAKENED=0`.

## Boundary

```
PRODUCTION_MUTATED=NO   LIVE_DB_MUTATED=NO   SESSION_STATE_APPLIED=NO
SECRETS_CREATED=NO      EXTERNAL_DASHBOARD_MUTATED=NO
```

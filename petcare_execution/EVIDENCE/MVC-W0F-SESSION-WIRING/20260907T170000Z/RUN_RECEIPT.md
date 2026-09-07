# MVC-W0F-SESSION-WIRING — AC-7 integrated into the governed auth path

**Base:** `22c9efe0ed79c2db4a9106d03169ce061b12a52b` (after PR-B / #19)
**Scope:** NON_PRODUCTION_ONLY

Closes the gap the previous run flagged in its own receipt: the store existed and
its controls were armed, but `read_session()` did not consult it, so revocation
was a capability rather than an enforcement.

## B0 — live state, verified not assumed

```
PR #18 (PR-A)  MERGED 2026-09-07T14:00:39Z  ad10910cdc4b69be743490eb2b6fef50aaa7cb6f
PR #19 (PR-B)  MERGED 2026-09-07T14:12:33Z  22c9efe0ed79c2db4a9106d03169ce061b12a52b
session_store.py on main: PRESENT
wired into auth.py:       NO
```

The continuation instruction assumed PR-B was still open. It had merged. This run
is therefore new work on a new branch, not a continuation of an open PR — the
store was landed, the wiring was not.

## B1 — wiring

`read_session()` now enforces the store, and the **order is load-bearing**:

```
1  signature verification        (unchanged, first, never skipped)
2  payload shape check           (unchanged)
3  sid present                   -> else SESSION_NOT_ESTABLISHED
4  store says active             -> else SESSION_REVOKED_OR_EXPIRED
```

Sign-in creates the record **before** minting the cookie, and the cookie carries
only the session id. A cookie whose id is not in the store is not a session,
however well signed it is.

None of the forbidden shapes were introduced:

```
PREVIOUS_KEY_LIST_PRESENT=NO
LOOKUP_WITHOUT_SIGNATURE_ACCEPTED=NO
LEGACY_COOKIE_FALLBACK=NO      (a sid-less cookie is refused, not admitted)
TENANT_OPTIONAL_LOOKUP=NO
```

### One semantic distinction the wiring forced

`seed_user` permits an identity with no tenant, and `test_t_ten_02` requires such
an identity to reach the route and be refused there with
`403 NO_TENANT_AUTHORITY` — not refused at the session layer with a 401. So the
store had to distinguish two things that both look like "falsy tenant":

```
None   the identity holds NO tenant assignment. Legitimate; the session is real
       and fails closed downstream at require_tenant().
""     a MALFORMED tenant — a value that was lost, not absent. Refused.
```

Collapsing them would either have broken W0-C's fail-closed test or admitted a
session keyed on a value that could later collide.

## B2 — key rotation must still revoke

```
T_SESSION_ROTATE_01=PASS
KEY_ROTATION_REVOKES_EXISTING_SESSION=YES
```

Flow: real sign-in → record confirmed in store → authenticated request succeeds →
signing key rotated in the isolated test process → pre-rotation cookie presented →
**denied 401 `INVALID_SESSION`**, with the store record deliberately left
**active**, so the denial demonstrably comes from signature verification and not
from the store.

```
P_SESSION_ROTATE_01=FAILED_AS_REQUIRED  (control binds; NOT vacuous)
  probe: on BadSignature, accept the payload via loads_unsafe() — i.e. honour a
         stored session without verifying the current signing key
  result: 2 controls failed —
    test_t_session_rotate_01_key_rotation_denies_pre_rotation_sessions
    test_signature_is_verified_before_the_store_is_consulted
  restored: 5 passed
```

### The first probe was ineffective, and that nearly produced a false verdict

The initial perturbation attempt reported **5 passed**, which under the
instruction's rule reads as `CONTROL_VACUOUS` and would have halted the PR.

It was not vacuous — the probe had not applied. Re-run with the file diff
verified before the tests ran (`grep PERTURBATION` on the target), the same
control failed immediately.

The lesson is worth recording because it generalises: **an ineffective
perturbation and a vacuous control are indistinguishable from the test output
alone.** A perturbation must be shown to have reached the code path before its
result means anything. Every probe in this run was verified applied before being
believed.

## B3 — proof the tests reach the store through the governed path

```
HANDCRAFTED_COOKIE_TESTS_PRESENT=NO
REAL_SIGNIN_STORE_TEST_PRESENT=YES
REAL_SIGNIN_STORE_TEST=
  petcare_api/tests/test_session_store_e2e.py::
  test_t_session_store_e2e_01_signin_creates_a_stored_session_and_revocation_denies_it
```

Checked rather than assumed: no test in `petcare_api/tests/` constructs a cookie
by hand. Every existing helper already drives `POST /api/auth/sign-in`. The
module-level controls in `test_session_revocation.py` construct a store directly
and prove its *semantics*; they could not prove it was *wired*, which is why the
end-to-end file exists.

T-SESSION-STORE-E2E-01 does all six required steps: real sign-in, record
confirmed present in the store, real cookie used on a protected route, record
revoked, same cookie refused, denial reason asserted
(`SESSION_REVOKED_OR_EXPIRED`).

## B4 — AC-7 controls

```
AC7_01=PASS  revoked session denied            (module + over the wire)
AC7_02=PASS  tenant-A session denied in tenant B
AC7_03=PASS  expired session denied server-side
AC7_04=PASS  unknown/deleted session denied
AC7_05=PASS  revoking one user leaves another active (module + over the wire)
AC7_06=PASS  individual revocation needs no key rotation
AC7_07=PASS  key rotation invalidates pre-rotation sessions   [NEW]
```

AC7-06 and AC7-07 are the pair that matters. Together they say: revocation of one
session must not require rotation, **and** rotation must still revoke everything.
A store that satisfied only the first would have silently cost the emergency
property — every other control would still pass while global rotation quietly
stopped working.

## B5 — identity and tenant authority

Existing proven controls bind unchanged and were not duplicated:
`test_tenant_authority.py` (T-TEN-01..06), `test_session_bound_authorization.py`
(W0-B), `test_professional_authority.py` (T-PROF-01..07),
`test_tenant_scope_signatures.py` (estate guard).

### The estate guard caught a real regression in this run

Adding `SESSION_STORE` above `seed_user` moved it from line 172 to 179, and the
allowlist was keyed on the line number — so the guard failed.

That is brittleness in the guard, not a defect in the code: a line-keyed
exemption breaks whenever anything above it moves, and the cheap fix is to bump
the number, which trains the next person to edit the exemption rather than
examine it. The key is now `file::function(param)`, and the guard was
re-perturbed after the change to confirm it still bites.

## B6 / B7 — not done in this run

```
SECRET_PROVIDER=CONTRACT_DEFINED_NOT_IMPLEMENTED
SECRET_FALLBACK_GUARD=EXISTING_W0A_ONLY (no new guard added)
IDENTITY_MIGRATION_DRY_RUN=NOT_RUN
DATA_STORE_ADAPTER=NOT_IMPLEMENTED
```

Stated plainly rather than implied. This run did the wiring and its proofs; the
secret-provider abstraction and the identity-migration schema and dry-run remain
exactly as PR-A specified them, unimplemented.

## B8 — W0-G / W0-H / W0-J residue

```
W0G_STATUS=READY_PENDING_PRODUCTION_GATE — chain persistence needs the store
           provisioned and migration 0028 applied (GATE_LIVE_APPLY)
W0H_STATUS=READY_PENDING_PRODUCTION_GATE — seller population needs the store
           provisioned and migration 0029 applied (GATE_LIVE_APPLY)
W0J_STATUS=READY_PENDING_PRODUCTION_GATE — persisted user store needs
           provisioning plus the identity migration
           (GATE_LIVE_APPLY + GATE_IRREVERSIBLE_ACTION)
```

None is CLEAN and none is blocked on further design. Each now waits on a gated
apply.

## B9 — regression

```
serving API           87 passed   (was 82; +5 end-to-end wiring controls)
governance + root    186 passed
runtime              247 passed
secret_scan          SCANNED=3832 ALLOWLISTED=0 FINDINGS=0  CLEAN
prohibited_literal   SCANNED=373  ACTIVE_LITERAL_DEFAULT=0
evidence bundles     24 bundles, 156 artefacts, FAILED=0

Web and responsive suites not re-run: no web source was touched.
Last measured (PR #16): 120 vitest, tsc clean, 90/90 Playwright.
```

One existing guard file was modified — `test_tenant_scope_signatures.py`, to make
the allowlist key line-independent. No assertion was removed or weakened; the
guard was re-perturbed after the change and still fires.

```
ASSERTIONS_WEAKENED=0
```

## Boundary

```
PRODUCTION_MUTATED=NO   LIVE_DB_MUTATED=NO      LIVE_DB_QUERIED=NO
SECRETS_CREATED=NO      EXTERNAL_DASHBOARD_MUTATED=NO
MIGRATIONS_APPLIED=NO   SESSION_STATE_PERSISTED=NO (in-memory store)
```

# A8 — AC7-01..07 re-proven on PostgreSQL, through the governed serving path

```
SESSION_STORE_BACKEND_TESTED=POSTGRESQL_AND_IN_MEMORY
AC7_01=PASS_ON_POSTGRES
AC7_02=PASS_ON_POSTGRES
AC7_03=PASS_ON_POSTGRES
AC7_04=PASS_ON_POSTGRES
AC7_05=PASS_ON_POSTGRES
AC7_06=PASS_ON_POSTGRES
AC7_07=PASS_ON_POSTGRES
KEY_ROTATION_POSTGRES_RESULT=PASS
KEY_ROTATION_PG_STORE_RECORD_ACTIVE_DURING_TEST=YES
DENIAL_SOURCE=SIGNATURE_VERIFICATION
P_SESSION_ROTATE_PG_01_RESULT=FAILED_AS_REQUIRED
```

The previous receipt recorded `SESSION_STORE_BACKEND_TESTED=IN_MEMORY_ONLY`. That
matters more than it sounds: every AC-7 control passed against a dict, and a dict
cannot disagree with itself about `NULL`, cannot have a conditional `UPDATE` match
zero rows, and has no notion of a transaction. The controls were true of the
semantics and silent about the implementation production will run.

## The path is the real one

Each control drives `POST /api/auth/sign-in` and a real protected route with the
PostgreSQL adapter installed into the serving module's own namespace — the same
indirection production uses. Nothing constructs a cookie by hand and nothing
inserts a session record directly.

`test_the_serving_path_is_actually_backed_by_postgres` is the vacuity guard for
the whole file: it asserts the adapter type, asserts `is_durable`, and then reads
the session row back **out of the database** rather than out of an object. Without
it, a fixture that silently failed to install the adapter would leave every
control below green — proving exactly what the previous receipt already said was
proven.

## T-SESSION-ROTATE-PG-01

1. real sign-in through the endpoint → a persistent row in `app_session`
2. an authenticated request on a protected route succeeds
3. the session record is left ACTIVE
4. the signing key is rotated in this process only
5. **asserted before the request**: `describe(sid)` returns a record,
   `revoked_at IS NULL`, and `get_active(...)` still resolves it
6. the pre-rotation cookie is presented again
7. result: `401 INVALID_SESSION`

Step 5 is what makes step 7 mean anything. If the record were revoked or missing,
a 401 would prove nothing about rotation.

**Perturbation `P-SESSION-ROTATE-PG-01`** — on `BadSignature`, accept the payload
via `loads_unsafe()`, honouring a stored session without verifying the current
key. Marker verified, content diff verified, then: 2 controls failed
(`test_t_session_rotate_pg_01…`,
`test_signature_is_verified_before_the_postgres_store_is_consulted`). Restored:
13 passed. The control binds and is not vacuous.

## AC7-06 and AC7-07 are a pair

A store satisfying only AC7-06 would silently cost the emergency property while
every other control still passed. AC7-06 additionally asserts that the signing
key did **not** change during individual revocation, so "revocation works" cannot
be satisfied by rotating the key.

## Two defects the wiring exposed

**Registration minted a cookie with no session id.** `read_session` refuses a
cookie without `sid` (`SESSION_NOT_ESTABLISHED`), so every protected route
returned 401 to a user who had just registered successfully and been handed
cookies — while `/api/auth/me`, which parses the cookie itself rather than going
through `read_session`, answered 200. A registered user appeared signed in and
could do nothing. `register` now creates the session record.

**A consumed invite code came back on restart.** Seeding re-created
`_invite_codes` wholesale, so a spent pilot code became spendable again. The
persistent upsert deliberately does not touch `consumed_at` / `consumed_by`, and
a control asserts a spent code stays spent across a simulated restart.

```
TESTS=petcare_api/tests/test_session_store_postgres_e2e.py   13 passed
```

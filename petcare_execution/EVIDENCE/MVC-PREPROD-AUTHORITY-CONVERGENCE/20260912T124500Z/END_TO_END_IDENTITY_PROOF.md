# A15 / A16 — the production identity path, proven end to end

```
END_TO_END_IDENTITY_PROOF=PASS
POSTGRES_TEST_BACKEND=POSTGRESQL 16.11 (local ephemeral)
LIVE_DB_TOUCHED=NO
```

The only way a production identity comes into existence after `PRE1_RULING=1-B`,
driven for real against PostgreSQL:

| # | Step | Assertion |
|---|---|---|
| 1 | a synthetic tenant is created deliberately | `is_assignable` is true; nothing auto-created it |
| 2 | `POST /api/auth/register`, invite-gated | `201` |
| 3 | the minted role is the CANONICAL id | `role == "owner"` — the assertion CONF-01 would have failed |
| 4 | registration assigns NO tenant | `tenant_id is None` — W0-C: tenant is a server-side act, never a form field |
| 5 | explicit tenant assignment | checked against the registry |
| 6 | `POST /api/auth/sign-in` | a real `app_session` ROW, carrying tenant and role |
| 7 | a permitted route | `201` |
| 8 | an `audit_event` row | tenant-scoped, actor role server-established |
| 9 | the tenant foreign key | joins to a real `tenant` row |
| 10 | the chain verifies | `ok` |
| 11 | cross-tenant access | `403 TENANT_SCOPE_DENIED` |
| 12 | session revoked, cookie re-presented | `401 SESSION_REVOKED_OR_EXPIRED` |

```
SEED_HELPER_USED=NO
DIRECT_DB_FIXTURE_FOR_THE_USER=NO
HARDCODED_PASSWORD_IN_APPLICATION_SOURCE=NO
```

The identity is created by driving the endpoint, because the path a deployment
uses is the path that must be under test. Tests that seeded a value no production
path produced are how CONF-01 survived for as long as it did.

## Two negatives alongside it

- **registration cannot mint a non-canonical role** — an invite code is the only
  way in, and `0033` constrains `allowed_role` to the canonical catalogue, so
  seeding an invite for `pharmacy` is refused before a registration can use it.
- **an identity cannot be assigned an unregistered tenant** — the deliberate
  assignment in step 5 is checked, and `TenantDenied` is raised.

## The step with no governed API

Step 5 is performed through the identity repository, which is the operator-side
boundary, rather than by writing SQL — a raw insert would prove the database
works and nothing about the path an operator would take.

There is no admin route for it. Recorded as
`TENANT_ASSIGNMENT_HAS_NO_GOVERNED_API` and carried into the activation pack as
`PRE-6`: sufficient for a rehearsal, insufficient for an operated system.

```
TESTS=petcare_api/tests/test_end_to_end_identity_postgres.py   3 passed
```

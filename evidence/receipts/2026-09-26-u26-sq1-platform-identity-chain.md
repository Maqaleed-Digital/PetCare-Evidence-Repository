# U26 · SQ-1 → AC-FR-01-03 — platform identity audit chain, 2026-09-26

```
PROGRAMME=MVC-BUILD-RUNNER-001 v1.2   UNIT=U26   BASE_MAIN=c6b04505b5c7accc6d0266f6cc6343dfe37e8df9 (U25 merged, PR #71)
BRANCH=build/u26-sq1-platform-identity-chain
AUTHORITY=governance/sponsor_acts/MVC-SQ1-PLATFORM-IDENTITY-AUDIT-001.md
ACT_HASHES[SQ1]=639c82bf3cebc9cd0347b9683b853a6085362b467d5ccc7dd99ebdd59af20c43
AC-FR-01-03: gaps [AUDIT, PERSISTENCE, TENANT_ISOLATION] -> []  (EVIDENCED)
FR-01: REACHABLE_TESTED (unchanged; AC-FR-01-04 remains COUNSEL:L-2)
```

## Build
- `platform_identity_audit.py`: a SEPARATE chain (`chain_id=platform-identity`) with the same canonical hashing as the
  tenant chain (`verify_hash_chain`). Records carry no tenant; `core()` refuses a record containing `tenant_id`
  (no sentinel tenant). Subject is the user id when known, else `email-sha256:<digest>` — no plaintext email.
- Migration **0053** `platform_identity_chain_head` + `platform_identity_event` (no tenant column, `chain_seq` UNIQUE).
  Non-prod code only; nothing applied to any live database. **Migration count changes: 57 -> 58.** REQUEST-002 (the
  2026-09-13 production-apply plan) cites the earlier chain and therefore REMAINS STALE; this unit does not refresh it.
- `PostgresPlatformIdentityAudit`: append in one transaction, head row `SELECT … FOR UPDATE`.
- `routers/auth.py`: registration, failed registration, vet licence submission and EVERY failed sign-in (including an
  identity that has a tenant) are written to the platform chain, never to a tenant chain. Failed sign-in for an unknown
  identity verifies against a dummy hash and returns the same 401 `INVALID_CREDENTIALS` body as a wrong password.
- `GET /api/admin/platform-identity-audit` (platform_admin): chain verification + events.
- Tenant chain untouched: `audit_event.tenant_id` stays NOT NULL (asserted by the PG test).

## Evidence registered (AC-FR-01-03)
| Type | Test |
|---|---|
| AUDIT | test_sq1_platform_identity_chain.py::test_registration_success_and_failure_are_on_the_platform_chain_only |
| AUDIT | test_sq1_platform_identity_chain.py::test_every_failed_sign_in_is_on_the_platform_chain_even_for_an_identity_with_a_tenant |
| AUDIT | test_fr01_account_authority.py::test_sign_in_and_sign_out_are_chained_and_sign_out_ends_the_session (U20) |
| AUDIT | test_fr01_account_authority.py::test_ending_a_membership_keeps_history_attributable (U20) |
| PERSISTENCE | test_sq1_platform_identity_chain_postgres.py::test_the_platform_chain_is_durable_serialised_and_tenantless_and_the_tenant_invariant_holds |
| TENANT_ISOLATION | test_fr01_account_authority.py::test_tenant_authority_is_server_held_and_a_moved_membership_fails_closed (U20) |
| TENANT_ISOLATION | test_sq1_platform_identity_chain.py::test_every_failed_sign_in_is_on_the_platform_chain_even_for_an_identity_with_a_tenant |

FR-01 binding cites ACT_HASHES[SQ1]; fitness `audit_actor_source` NONE -> SESSION (the stale
AUTH_EVENTS_OUTSIDE_AUDIT_CHAIN basis line replaced).

## Perturbations
```
P-FAILED-SIGNIN-TO-TENANT-CHAIN  failed sign-in of a tenant identity -> tenant chain   -> FAILS  ARMED   (mandated)
P-NULL-TENANT-ON-TENANT-CHAIN    audit_event.tenant_id DROP NOT NULL                   -> PG FAILS  ARMED (mandated)
P-REGISTRATION-UNCHAINED         auth.user_registered not chained                      -> FAILS  ARMED
P-SENTINEL-TENANT-ALLOWED        platform record may carry tenant_id                   -> PG FAILS  ARMED
P-DISTINGUISHABLE-RESPONSE       unknown identity -> different 401 body                -> FAILS  ARMED
P-PLATFORM-HEAD-UNLOCKED         head read without FOR UPDATE                          -> PG FAILS  ARMED
PERTURBATIONS=6 ARMED=6 VACUOUS=0
```

## Regression (local)
pytest 1125 passed, 0 skipped · web 192 passed, tsc clean · secret / evidence-bundle / prohibited-literal scans 0 ·
checker regenerated (served routes 97 -> 98).

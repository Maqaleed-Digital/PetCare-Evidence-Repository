# MyVetiCare — W0-G audit persistence + pre-production convergence, 2026-09-12

Durable session receipt. Where this disagrees with any summary, transcript or
handoff, the repository and the register outrank it (Rule 14).

```
RULE_13=GREEN_CI_NECESSARY_NOT_SUFFICIENT
RULE_14=LIVE_REGISTER_OUTRANKS_NARRATIVE
RULE_15=WRITE_AUTHORITY_PRECEDES_INTEGRITY_CHAIN
RULE_16=CONTROL_DELIVERED_ONLY_WHEN_GOVERNED_PATH_REACHES_IT
RULE_17=PERTURBATION_PROVEN_APPLIED_BEFORE_ADJUDICATION
RULE_18=RESIDUE_REMEASURED_FROM_LIVE_SOURCE
```

## Heads

```
START_HEAD=77d921ecbaee96807d2c84501348a10b4566f311
PR21_STATUS=MERGED   PR21_MERGE_SHA=5609719f0d4598472c302108642e7b013a893c06
PR22_STATUS=MERGED   PR22_MERGE_SHA=77d921ecbaee96807d2c84501348a10b4566f311
PR23_STATUS=MERGED   PR23_MERGE_SHA=7d8a36f08339682e90d6b1c71208ffe51ff7d6a2
                     2026-09-12T11:26:26Z, base=main
END_HEAD=7d8a36f08339682e90d6b1c71208ffe51ff7d6a2
HARNESSONLY_MERGE_DENIAL=NO   (the W0-F lane recorded YES; it did not recur here)
```

The harness-only merge denial recorded in the previous receipt is cleared.

```
W0F_STATUS=NON_PRODUCTION_IMPLEMENTATION_COMPLETE   (verified by artefact, not inherited)
```

## W0-G

```
W0G_STARTING_CLASSIFICATION=RESIDUE_REMAINING
W0G_LIVE_FINDING=the authoritative writer was `_audit_log`, a module-level Python
                 list; no audit repository existed; ZERO audit_event rows were
                 written by any code path
AUDIT_REPOSITORY_IMPLEMENTED=YES   petcare_api/audit_repository.py
AUDIT_POSTGRES_IMPLEMENTED=YES     0032_w0g_audit_chain_persistence.sql
AUDIT_SERVING_PATH_WIRED=YES       11 call sites reach AUDIT_REPO.append_event
AUDIT_BACKEND_TESTED=POSTGRESQL_AND_IN_MEMORY
W0G_FINAL_STATUS=READY_PENDING_PRODUCTION_GATE
```

NOT rounded up. Two items remain open and are not claimed closed:

```
ARCH_01_SIGNATURES_OR_ANCHORING=OPEN        specification question, carried from W0-G
AUTH_EVENTS_OUTSIDE_AUDIT_CHAIN=OPEN_GAP    13 events; entering them needs a tenant
                                            and inventing one is what W0-C removed
```

## W0-H / W0-J — re-measured from live source

```
W0H_LIVE_STATUS=READY_PENDING_PRODUCTION_GATE
  0029 authored; seller_id has 0 occurrences in petcare_api; SET NOT NULL is a
  commented step with a recorded precondition; 7 controls
W0J_LIVE_STATUS=READY_PENDING_PRODUCTION_GATE
  scrypt live; user_identity persisted; rehash-on-login writes through the
  repository; blocked additionally on PRE-1
```

## PRE-1 — tenant assignment

```
PRE1_SOURCE_COUNT=3
PRE1_MIGRATABLE_BEFORE_DECISION=0
PRE1_QUARANTINED=3                    all UNRESOLVED_NO_TENANT
PRE1_EXISTING_AUTHORITY_FOUND=NO
PRE1_DECISION_REQUIRED=YES
PRE1_DECISION_PACKET=READY
```

The finding beneath the finding: **there is no tenant registry anywhere in the
estate.** No catalogue table in any of the 37 migrations; `tenant_id` is an
unconstrained `TEXT NOT NULL` with no foreign key; no governance artefact names a
tenant. The only tenant-shaped identifiers — `tenant_jeddah_001`,
`tenant_riyadh_001` — exist only inside EP-05/EP-06 test fixtures and are NOT
offered as options.

```
TENANT_REGISTRY_EXISTS=NO
SEED_PASSWORD_IS_A_PUBLIC_LITERAL=YES   petcare_api/main.py:106,108,110
REPOSITORY_VISIBILITY=PUBLIC
```

## PRE-2 / CONF-01 — role authority

```
CONF01_STATUS=OPEN
PRE2_VOCABULARY_A=Owner / Veterinarian / Platform Admin / Partner Clinic Admin
                  (access_control.py; the only set require_role accepts)
PRE2_VOCABULARY_B=owner / veterinarian / platform_admin / partner_clinic_admin
                  (minted by seed_user and registration; in the session and cookie)
PRE2_VOCABULARY_C=owner / vet / pharmacy / admin
                  (petcare_web/middleware.ts, which ALIASES V-B into V-C)
PRE2_EXISTING_AUTHORITY_FOUND=NO_RATIFIED_AUTHORITY
PRE2_DECISION_REQUIRED=YES
PRE2_DECISION_PACKET=READY
PRE2_RECOMMENDATION=OPTION_C (machine IDs as authority + display labels separate),
                    with OPTION_A as its first step
```

There are THREE vocabularies, not two, and the third decides the recommendation:
`middleware.ts` is written to alias the MACHINE forms, and `strings.ts` already
localises the display names into Arabic and English — a token that must be
translated cannot also be the token authorization compares.

Live consequence: **every identity this system creates is refused by every
protected backend route with `403 Unknown role`.** The suite does not show it
because tests that need a working session seed the V-A spelling directly, which
no production path produces.

```
RETIRED_ROLE_SURVIVES_IN_WEB_AS_SHORT_FORM=YES
  alias + /pharmacy route + page + onboarding + home CTA
GUARD_BLIND_TO_IT=YES   needle "pharmacy_operator" vs short form "pharmacy"
```

## Sponsor decision pack

```
SPONSOR_DECISION_PACK=petcare_execution/GOVERNANCE/MVC-PREPROD-SPONSOR-DECISION-001/
                      MVC-PREPROD-SPONSOR-DECISION-PACK-001.md
STATUS=PROPOSED / AWAITING_SPONSOR_RULING
```

One document, two decisions, one ruling. No approval is written on the Sponsor's
behalf.

## Regression

```
REGRESSION_TOTALS
  ROOT      pytest tests                    228 passed
  RUNTIME   pytest petcare_runtime/tests    247 passed
  API       pytest petcare_api/tests        245 passed
  COMPOSITE the CI command                  720 passed      (baseline 698)
  228 + 247 + 245 = 720 — the per-suite sum check

POSTGRES_TOTALS
  test_postgres_integration.py          35
  test_session_store_postgres_e2e.py    13
  test_identity_migration_postgres.py   12
  test_audit_persistence_postgres.py    22
  TOTAL                                 82 passed
  POSTGRES_TEST_BACKEND=POSTGRESQL 16.11 local ephemeral / postgres:16 in CI
  LIVE_DB_TOUCHED=NO

  prohibited_literal   SCANNED=389   ACTIVE_LITERAL_DEFAULT=0
  secret_scan          SCANNED=3876  ALLOWLISTED=0  FINDINGS=0  CLEAN
  evidence bundles     BUNDLES=28  ARTEFACTS=186  FAILED=0

  CI on #23: 713 passed + 7 pre-existing skips = 720; TypeScript clean;
             web unit 120; responsive 90.

  ASSERTIONS_WEAKENED=0  CONTROLS_REMOVED=0  CONTROLS_STRENGTHENED=1 (T-CHAIN-05)

PERTURBATION_TOTALS
  7 probes, PROBE_MARKER_VERIFIED=7/7, DIFF_VERIFIED=7/7,
  CONTROL_FAILED_AS_REQUIRED=7/7, RESTORED_PASS=7/7, VACUOUS=0
```

## Evidence

```
EVIDENCE_DIR=petcare_execution/EVIDENCE/MVC-W0G-AUDIT-PERSISTENCE/20260912T113000Z
EVIDENCE_SHA256=EVIDENCE_SHA256.txt in that directory (12 artefacts)
```

## Findings — recorded, not quietly fixed

```
1  Two functions named `_audit`, one authoritative and one a log line. Renamed.
2  `audit_chain_durability` was a fixed string persistence would have made FALSE
   — the MVC-INC-ATTEST-001 defect inverted. Now computed.
3  audit_event had no ordering column; occurred_at is TEXT, and a tie reorders
   the chain into a verification failure that looks like tampering.
4  The per-test fixture cleared audit rows but not the chain head, so a clean
   chain reported as tampering. Six controls failed together, each passed alone.
5  This repository's own CI non-skip guard named two of four PostgreSQL suites
   while passing. Fixed in the same PR.
6  No tenant registry exists anywhere in the estate.
7  The seed identities' password is a public literal in a PUBLIC repository.
8  Three role vocabularies, not two.
9  A full `pharmacy` role surface survives in the web, invisible to the guard.
10 `fail_closed_reason` in /api/governance/status still reads "W0-B pending"
   although W0-B is delivered. NOT changed — a fail-closed posture claim is a
   governance statement, and it understates rather than overstates.
```

## State

```
OPEN_ENGINEERING_RESIDUE
  ARCH-01 signatures/anchoring (specification)
  AUTH_EVENTS_OUTSIDE_AUDIT_CHAIN (needs a governed answer, not code)
  CLINICAL_SERVING_PERSISTENCE (outside W0-F/W0-G; recorded in the W0-F bundle)

OPEN_SPONSOR_DECISIONS
  PRE-1 tenant assignment / disposition of the three seed identities
  PRE-2 CONF-01 role authority
  PRE-2D disposition of the web `pharmacy` role surface

OPEN_PRODUCTION_GATES
  GATE_LIVE_APPLY          provision · apply schema · apply identity migration
  GATE_CREDENTIAL_ENTRY    create the session signing secret
  GATE_IRREVERSIBLE_ACTION decommission the in-memory seeding

NEXT_GENUINE_GATE=SPONSOR_PREPROD_DECISION_PRE1_PRE2
```

```
GITHUB_SUPPORT_REFS_PULL_1_6=NOT_SENT
  Parallel external housekeeping. Not touched by this run, not claimed closed.
  Submission is an external-account/dashboard action.
```

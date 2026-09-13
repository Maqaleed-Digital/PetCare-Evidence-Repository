# MyVetiCare — Option A pilot substrate, 2026-09-13

```
RULE_13=GREEN_CI_NECESSARY_NOT_SUFFICIENT
RULE_16=A_ROUTE_THAT_IS_NOT_MOUNTED_IS_NOT_DELIVERED
LANE=OPTION_A · RX INTAKE -> VET VERIFICATION -> DISPENSE
ENVIRONMENT=NON_PRODUCTION_ONLY
PRODUCTION_MUTATION=NONE
```

## Headline

```
MYVETICARE_OPTION_A=BLOCKED_AT_TRUE_GATE
PHARMACARE_OPTION_A_PILOT_READY_IN_NONPROD=NO
NEXT_GENUINE_GATE=SPONSOR_PRODUCT_ACT · PHARMACY_AUTHORIZATION_PRINCIPAL
```

The substrate is built, proven and durable. The **actor** is not available, and
cannot be made available by engineering.

## The gate, stated precisely

Option A's commercial definition requires, at steps 5 and 6, that *the pharmacy*
sees a verified item and *the pharmacy* dispenses it. No identity in this estate
can be that actor:

```
petcare_runtime/src/petcare/pharmacy/review.py
    start_pharmacy_review      -> if actor_role != ROLE_PHARMACY: PermissionError
    add_review_note            -> if actor_role != ROLE_PHARMACY: PermissionError
    progress_pharmacy_review   -> if actor_role != ROLE_PHARMACY: PermissionError

petcare_runtime/src/petcare/auth/access_control.py:9
    ROLE_PHARMACY_OPERATOR = "Pharmacy Operator"        # a DISPLAY form (CONF-01 shape)

petcare_api/roles.py
    ALLOWED_ROLES = {platform_admin, partner_clinic_admin, veterinarian, owner}
    PHARMACY_ROLE=REMOVE                                 # not an authorization principal
```

So the pharmacy review path raises for **all four** roles the platform can mint.
It is unreachable by construction, not merely unwired. Admitting the principal
is a Sponsor product act (W0-D, invariant I-5) and additionally turns on a
regulatory fact this estate does not hold — whether a non-veterinarian may
lawfully dispense a veterinary medicine in KSA (`REQ-DISP-AUTH-FAILCLOSED`,
BRD V3.2 §11.1, "must not be widened for convenience").

```
NEW_ROLE_INTRODUCED=NO
DISPENSING_AUTHORITY=VETERINARIAN (unchanged)
```

## What WAS delivered

```
START_SHA=a96bd39a7456475ec3c4e45e84bba8b14816c74e
BRANCH=feat/option-a-rx-pilot-substrate

FR14=DELIVERED_NONPROD
FR27_OPTION_A=PARTIAL · BLOCKED_AT_SPONSOR_GATE

PRESCRIPTION_POSTGRES_PERSISTENCE=YES   migration 0036 + both repositories
PRESCRIPTION_UPLOAD=YES                 local adapter; production store NOT bound
VET_VERIFICATION=YES                    ISSUED -> VET_VERIFIED -> DISPENSED
PHARMACY_BACKEND_WIRED=N/A              see "not mounted, deliberately"
SERVED_APP_REACHABILITY=YES             9 routes on main.app, asserted
PHARMACY_UI_REAL_BACKEND=YES            queue/detail/dispense against real APIs
ARABIC_OPTION_A=YES                     ar/en, dir switched on the surface
TENANT_ISOLATION=PASS
AUDIT_PERSISTENCE=PASS                  chained, verified in PostgreSQL
```

### The defects closed on the way

1. **Prescriptions were a module-level dict.** `_prescriptions` died with the
   process and was invisible to every other instance.
2. **A prescription was dispensable the instant it existed.** The only state
   guard was `status == "ISSUED"`. There was no verification step at all.
3. **The audit actor came from a client header.** Every prescription route took
   `x_actor_id: Header(...)` and wrote it into the log as the actor — so the log
   recorded whoever the client said it was, on routes whose entire purpose is
   attributing a clinical act. Now server-derived from the session (W0-B).
4. **The PostgreSQL controls were not running in this environment.** `psycopg`
   was absent, so 8 suites skipped. A skipped integration suite and a passing
   one are indistinguishable in a summary line.
5. **A pharmacy UI bug, caught by its own new test.** A 409 refresh cleared the
   error banner before the user could read it.

### Not mounted, deliberately

```
PHARMACY_GATEWAY_MOUNTED=NO  (recorded, asserted by a control)
```

`petcare_runtime.pharmacy.fastapi_app` is a separate app with 11 read-only
surfaces. It is not mounted, for two reasons:

* `build_gateway_auth_context` accepts ANY non-empty `Authorization: Bearer
  <string>` — the token is never validated — and reads actor and tenant straight
  from client headers. Mounting it would reintroduce W0-B into the served app.
* its read surfaces can only return records that only `ROLE_PHARMACY` can
  create, and that role does not exist.

Mounting it would have raised the route count and delivered nothing.
`test_served_app_reachability.py` fails if anyone mounts it.

## Evidence

Two environments, reconciled separately. **CI is the authoritative one.**

### CI — the number that describes the programme

```
                       main@a96bd39      PR #38        delta
Python estate          882 p /  7 s      925 p / 7 s   +43 passed
PostgreSQL non-skip    160 p /  0 s      170 p / 0 s   +10
Web unit               120 p             127 p         + 7
Responsive regression   —                 90 p
CONCLUSION=success   JOBS_SKIPPED=0   STEPS_SKIPPED=0

RECONCILIATION (exact):
  +41  new Option A controls
  + 2  new dispensing controls (5 -> 7)
  = 43
```

The **7 skips are PRE-EXISTING and unchanged** — the seven
`@port_source_available` tests in
`tests/governance/test_cross_repository_traceability.py`, which need a second
repository checked out (`MVC_PORT_SOURCE_ROOT`) that CI does not provide. Same
seven before and after this branch. Not introduced here, and not fixed here.

### Local — and why its baseline was lower

```
REGRESSION_BEFORE=729 passed, 8 skipped
REGRESSION_AFTER =932 passed, 0 skipped
```

The local baseline was low because **this workstation** had no `psycopg`, so 8
PostgreSQL suites skipped at collection. CI always had it and always ran them.
Installing the declared dependency unlocked 160 tests **locally only** — it is
not a gain for the programme, and the CI table above is the one that describes
what this branch changed. It is recorded because a local run that reports 8
skipped PostgreSQL suites is a local run producing no PostgreSQL evidence, and
this lane's central claim is about durable storage.

```
WEB_TYPECHECK=CLEAN          WEB_BUILD=SUCCESS (/pharmacy 3.49 kB)
POSTGRESQL=REAL — CI service container; locally an ephemeral cluster,
           41 migrations replayed
SKIPPED_ON_OPTION_A_PATH=0   (in both environments)
```

Each Option A suite was also run **alone**, not only in the combined
invocation — scope is per-invocation:

```
test_option_a_workflow                  19 passed
test_prescription_persistence_postgres  10 passed
test_served_app_reachability            12 passed
test_dispensing_fail_closed              7 passed
```

### Perturbations — 4 applied, 4 armed, 0 vacuous

Each mutation was confirmed to have landed in the working tree BEFORE the
control was run, and each file was restored byte-identical afterwards.

```
P1  served-app route unmounted        -> reachability   1 failed   ARMED
P2  verification gate bypassed        -> dispensing     3 failed   ARMED
P3  tenant predicate weakened         -> isolation      2 failed   ARMED
P4  durable store swapped for memory  -> persistence    3 failed   ARMED
RESTORED_IDENTICAL=4/4
```

## Governance controls that fired during this lane

Recorded because each caught a real defect in work authored here, which is the
argument for keeping them:

```
test_tenant_scope_signatures     InMemoryPrescriptionRepository(tenants=None)
                                 — a tenant that may be omitted may be ignored.
                                 Made REQUIRED.
test_ci_postgres_coverage        the new PostgreSQL suite was not named in the
                                 CI non-skip step. Added.
test_retired_role_family         ARIA role="alert" beside a pharmacy test id,
                                 and the prose "no pharmacy role in this",
                                 both read as authority declarations. Reworded
                                 rather than registered as exemptions.
surface-states (PORT-08)         the new queue region went blank while loading.
                                 Empty state now renders in every no-rows state.
```

## Out of scope — not claimed, not built

```
OUT_OF_SCOPE=FR13,FR15_GENERAL_ROUTING,FR16,FR19,FR20,FR30
```

The `/pharmacy` surface previously displayed "Safety checks" (FR-15) and
"Cold-chain tracking" (FR-16) cards. Both named capabilities that do not exist.
They were **removed**, not left showing an empty state: a card that names a
capability reads as a delivered feature whatever its body says.

## Open items

```
OPEN-1  Programme-wide REQ/MVC/FR register reconciliation — Sponsor authority.
        A minimal bridge for FR-14/FR-27 only is at
        evidence/traceability/OPTION_A_FR14_FR27_BRIDGE.md
OPEN-2  Pharmacy authorization principal — THE gate above.
OPEN-3  Production object store for attachments is NOT bound.
        `ProductionObjectStore` raises rather than falling back to local disk.
        Binding it is GATE_CREDENTIAL_ENTRY.
OPEN-4  PRE-EXISTING, outside this lane, NOT changed:
        petcare_runtime/src/petcare/uphr/service.py timeline search filters on
        `str(item)` — the whole record dict — so a hex-substring term ("cbc")
        matches records whose UUIDs happen to contain it. Makes
        test_ep01_ep02_wave_03.py::test_timeline_can_search nondeterministic at
        roughly 1% per run. Observed once during this lane; passes alone and on
        re-run. Changing search semantics is a product decision.
```

## What a Sponsor decision would unlock

If a pharmacy principal is admitted, the remaining work is small and the
substrate is already shaped for it: `verified_by_vet_id` is stored separately
from `issuing_vet_id` so a separation-of-duties rule applies to existing rows
without a migration, and the queue endpoint's role check is a single predicate.

If instead KSA law confirms dispensing is a veterinary act, Option A is already
complete for a **clinic-operated** pilot — and the pharmacy's role becomes
visibility, which the queue already serves.

```
MIGRATION_0036_APPLIED_TO_PRODUCTION=NO
PRESCRIPTION_ROWS_CREATED=0
TENANT_ROWS_CREATED=0
```

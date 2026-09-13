# Option A — the FR-14 / FR-27 traceability bridge

```
SCOPE=OPTION_A_PILOT_ONLY
STATUS=MINIMAL_BRIDGE
BROADER_REGISTER=NOT_ATTEMPTED (recorded below as an open item)
```

## Why this file is small on purpose

Three identifier namespaces are in live use in this estate and none of them is a
superset of the others:

```
REQ-<NAMESPACE>     serving-layer invariants, asserted by name in tests
MVC-<DOMAIN>-nn     governance artefacts and custody records
FR-nn               BRD feature requirements — EXTERNAL to this repository
```

Reconciling all three is a programme-wide act that needs Sponsor authority over
the requirement register, and Option A is not blocked on it. What this file does
is narrower and sufficient: it names, for the two requirements this lane
touches, every identifier already in the tree that governs them — so a reader
starting from `FR-14` reaches the controls, and a reader starting from a control
reaches the requirement.

**Nothing is renumbered and no sealed receipt is rewritten.** Every identifier
below is retained as a live alias; this is an index, not a migration.

---

## FR-14 — prescription record and lifecycle

```
FR14_STATE_BEFORE=PARTIAL / REACHABLE
FR14_STATE_AFTER=DELIVERED (non-production)
```

| Identifier | Kind | What it governs | Where |
|---|---|---|---|
| `FR-14` | BRD | Prescription intake, record, lifecycle | BRD (external) |
| `REQ-DISP-AUTH-FAILCLOSED` | serving invariant | Dispensing authority fails closed to veterinarian while the professional-authority class is unclassified (BRD V3.2 §11.1) | `petcare_api/main.py`, `petcare_api/tests/test_dispensing_fail_closed.py` |
| `PERSIST-01` | serving invariant | A process configured for a durable store does not serve from memory | `petcare_api/persistence.py` |
| `W0-G` | governance | Audit chain over a durable store; the argument this migration reuses | `petcare_api/audit_repository.py` |
| `TENANT-05`, `PRE-1` | governance | A tenant is a governed object; an unregistered scope is refused | migration `0034`, `petcare_api/tenants.py` |
| migration `0036` | schema | `prescription`, `prescription_status_transition`, `prescription_document` | `petcare_runtime/migrations/0036_option_a_prescription_persistence.sql` |

Controls:

```
petcare_api/tests/test_option_a_workflow.py                 19
petcare_api/tests/test_prescription_persistence_postgres.py 10
petcare_api/tests/test_dispensing_fail_closed.py             7
petcare_api/tests/test_served_app_reachability.py           12
petcare_web/__tests__/pharmacy-queue.test.tsx                7
```

## FR-27 — pharmacy-side verification and dispense

```
FR27_STATE_BEFORE=PARTIAL / UNWIRED
FR27_STATE_AFTER=PARTIAL / BLOCKED_AT_SPONSOR_GATE
```

| Identifier | Kind | What it governs | Where |
|---|---|---|---|
| `FR-27` | BRD | Pharmacy verification and dispense | BRD (external) |
| `PHARMACY_ROLE=REMOVE` | Sponsor ruling | `pharmacy` is not an authorization principal | `petcare_api/roles.py`, `petcare_web/middleware.ts` |
| `W0-D` / invariant `I-5` | governance | Changing the role catalogue is a Sponsor product act | CP-2 W0-D, migration `0031` |
| `MVC-RETIRED-ROLE-CUSTODY-001` | custody | The retired role must not appear in live source | `tests/governance/test_retired_role_absence.py` |
| `CONF-01` | recorded defect | Machine IDs vs display labels as authority | `petcare_api/roles.py` |
| `DOMAIN_CAPABILITY_PENDING_ROLE_BINDING` | governance | Pharmacy domain capabilities retained, awaiting a role to bind them to | `petcare_web/middleware.ts` |

**Why FR-27 is not closed.** The `petcare_runtime.pharmacy` review workflow —
`start_pharmacy_review`, `add_review_note`, `progress_pharmacy_review` — gates
every write on `actor_role != ROLE_PHARMACY`, which resolves to
`ROLE_PHARMACY_OPERATOR = "Pharmacy Operator"` in
`petcare_runtime/src/petcare/auth/access_control.py`. That role is excluded from
the canonical authority set by `PHARMACY_ROLE=REMOVE`. So the pharmacy review
path raises `PermissionError` for **every one of the four roles the platform can
mint**, and it is unreachable by construction rather than merely unwired.

Admitting a pharmacy principal is a Sponsor product act and additionally turns
on a regulatory fact this estate does not hold — whether a non-veterinarian may
lawfully dispense a veterinary medicine in KSA. It is not done here.

What Option A delivers instead, under the **existing** governed actor:

```
/api/prescriptions/queue/awaiting-dispense   veterinarian, partner_clinic_admin
/api/prescriptions/{id}/verify               veterinarian
/api/prescriptions/{id}/dispense             veterinarian  (unchanged authority)
```

---

## Open items, recorded rather than silently deferred

```
OPEN-1  Programme-wide REQ/MVC/FR register reconciliation.
        Needs Sponsor authority over the requirement register. NOT attempted.

OPEN-2  Pharmacy authorization principal.
        Sponsor product act + KSA regulatory fact. Blocks FR-27 closure and
        blocks any external-pharmacy pilot login.

OPEN-3  UPHR timeline search matches opaque identifiers.
        petcare_runtime/src/petcare/uphr/service.py filters on `str(item)`, the
        whole record dict, so a search term that is a hex substring ("cbc")
        matches records whose UUIDs happen to contain it. Makes
        petcare_runtime/tests/test_ep01_ep02_wave_03.py::test_timeline_can_search
        nondeterministic at roughly 1% per run. PRE-EXISTING, outside Option A,
        and NOT changed here — altering search semantics is a product decision.
```

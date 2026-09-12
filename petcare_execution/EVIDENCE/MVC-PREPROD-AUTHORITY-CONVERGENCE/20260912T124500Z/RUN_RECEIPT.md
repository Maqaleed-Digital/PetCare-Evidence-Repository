# MyVetiCare — pre-production authority convergence, 2026-09-12

```
RULE_13=GREEN_CI_NECESSARY_NOT_SUFFICIENT
RULE_14=LIVE_REGISTER_OUTRANKS_NARRATIVE
RULE_15=WRITE_AUTHORITY_PRECEDES_INTEGRITY_CHAIN
RULE_16=CONTROL_DELIVERED_ONLY_WHEN_GOVERNED_PATH_REACHES_IT
RULE_17=PERTURBATION_PROVEN_APPLIED_BEFORE_ADJUDICATION
RULE_18=RESIDUE_REMEASURED_FROM_LIVE_SOURCE
RULE_19=NO_FALSE_TAMPER_FINDING_UNDER_CORRECT_OPERATION
```

## Terminal state

```
PRE1_IMPLEMENTED=YES        SEED_RUNTIME_PATH_PRESENT=NO
PRE2_IMPLEMENTED=YES        CONF01_STATUS=CLOSED
PHARMACY_ROLE_PRESENT=NO    PHARMACY_DOMAIN_CAPABILITIES=REBOUND_OR_EXPLICITLY_NON_AUTHORITATIVE
TENANT_REGISTRY_IMPLEMENTED=YES   TENANT_ROWS_CREATED=0
IDENTITY_MIGRATION_REHEARSAL=PASS_EMPTY_BY_DESIGN
END_TO_END_IDENTITY_PROOF=PASS
W0F/W0G/W0H/W0J=READY_PENDING_PRODUCTION_GATE
PRODUCTION_ACTIVATION_READINESS=READY
NEXT_GENUINE_GATE=GATE_LIVE_APPLY
```

## The four things worth reading

**1 · A published credential could have become three production accounts.**
The seed password was a literal in a PUBLIC repository, and W0-F's persistence is
what would have made the accounts permanent. Removed, with the startup path that
created them. `LIVE_APPLICATION_CREDENTIAL_LITERAL_COUNT=0`.

**2 · CONF-01 is closed, proven through registration rather than a fixture.**
A registered identity now reaches its route. The two 403s that bracket the change
mean opposite things: `Unknown role` said the system rejected its own vocabulary;
`NO_TENANT_AUTHORITY` says this identity has no scope yet, which is W0-C working.

**3 · A tenant is now a governed object, and the registry ships empty.**
`TENANT_ROWS_CREATED=0`. No `platform`, no test-fixture identifier promoted. The
migration cannot create the tenant it needs — the foreign key refuses and no
identity lands.

**4 · The migration is empty by design, not blocked.**
`SOURCE=0` rather than `QUARANTINED=3`. A quarantine of three is a backlog; a
source of zero is a migration with nothing to do.

## Findings recorded, not acted on

```
TENANT_ASSIGNMENT_HAS_NO_GOVERNED_API   registration cannot assign a tenant and
  no admin route does; the only path is an operator calling the repository.
  Carried into the activation pack as PRE-6.
PILOT_INVITE_CODES_ARE_PUBLIC_LITERALS  OWNER-PILOT-001 / VET-PILOT-001 are still
  seeded at startup from source literals in a PUBLIC repository. Outside the
  ruling's scope; removing invite-gated registration is a product act.
PRE2D_PHARMACY_SURFACE_DISPOSITION      not ruled; the capability question is
  answered, the surface's long-term disposition is not.
ARCH01_SIGNATURES_OR_ANCHORING          open, untouched.
AUTH_EVENTS_OUTSIDE_AUDIT_CHAIN         open, untouched.
```

## Two defects this lane produced and caught in its own controls

**SEED-01 measured the suite, not the startup path** — a shared in-memory
repository meant the count reflected other modules' fixtures. Now proven in a
fresh subprocess.

**SEED-02c could not see its own perturbation** — a negative lookbehind meant to
skip `password_hash` skipped `DEFAULT_ADMIN_PASSWORD` too. Found because the probe
designed to break the control did not. A perturbation that fails to break a
control is a finding about the control.

## Boundary

```
PRODUCTION_MUTATED=NO       LIVE_DB_MUTATED=NO
CLOUD_RESOURCE_TOUCHED=NO   EXTERNAL_DASHBOARD_MUTATED=NO
SECRET_CREATED=NO           TENANT_ROWS_CREATED=0
MIGRATIONS_APPLIED_TO_PRODUCTION=NO   (0033/0034 authored and rehearsed only)
```

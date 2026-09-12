# MyVetiCare — governed tenant-assignment control path, 2026-09-12

```
RULE_13=GREEN_CI_NECESSARY_NOT_SUFFICIENT
RULE_14=LIVE_REGISTER_OUTRANKS_NARRATIVE
RULE_15=WRITE_AUTHORITY_PRECEDES_INTEGRITY_CHAIN
RULE_16=CONTROL_DELIVERED_ONLY_WHEN_GOVERNED_PATH_REACHES_IT
RULE_17=PERTURBATION_PROVEN_APPLIED_BEFORE_ADJUDICATION
RULE_18=RESIDUE_REMEASURED_FROM_LIVE_SOURCE
RULE_19=NO_FALSE_TAMPER_FINDING_UNDER_CORRECT_OPERATION
```

## What this lane was authorized to do, and did

Sponsor ruling of 12 September 2026 authorized one non-production lane. All
sixteen numbered items were carried out; the twelve proof points are mapped to
named controls in `TENANT_MEMBERSHIP_SERVICE.md`.

```
GOVERNED_PATH_IMPLEMENTED=YES
ROLE_PARAMETER=ABSENT
AUDIT_MODEL=TWO_EVENT
TENANT_VALIDATION=REGISTRY, unknown and disabled fail closed as one answer
REVOCATION_PATH=YES          READBACK_PATH=YES
ATOMICITY=ONE TRANSACTION, armed and proven by induced failure
DIRECT_REPOSITORY_ACCESS=PROVEN NOT AN AUTHORIZED SERVING PATH
REGRESSION=842 passed (242 / 247 / 353)   baseline 802
PERTURBATIONS=6, all proven applied, all restored, 0 vacuous
```

## Items 4 and 5 needed no engineering

`PRE4_SESSION_POLICY=INVALIDATE_ALL` selects behaviour AC7-07 already proves on
PostgreSQL. `ENGINE_VARIANT=RDS_POSTGRESQL` selects a variant no code path
branches on, and the ruling's added constraint — no RDS-specific semantics — is
already guarded by the D.21 portability contracts. Both are recorded so a future
reader does not look for an implementation that does not exist.

## Item 2 remains unruled, and that is a decision

```
ITEM_2_STATUS=UNRESOLVED
PRODUCTION_TENANT_CREATION_AUTHORIZED=NO
```

The lane needed no production tenant: the governed path validates against the
registry, and synthetic fixtures exercise it. They acquire no production
authority.

## Boundary

```
PRODUCTION_MUTATED=NO       LIVE_DB_MUTATED=NO
PRODUCTION_TENANT_CREATED=NO  PRODUCTION_IDENTITY_CREATED=NO
SECRET_CREATED=NO           CLOUD_RESOURCE_TOUCHED=NO
MIGRATION_APPLIED_TO_PRODUCTION=NO
P1_AUTHORIZED=NO
```

## Open

```
ITEM_2  first production tenant                UNRESOLVED (Sponsor)
ITEM_6  GITHUB_SUPPORT_REFS_PULL_1_6           NOT_SENT — open, not closed
        ARCH-01 signatures / anchoring         OPEN
        AUTH_EVENTS_OUTSIDE_AUDIT_CHAIN        OPEN
        PRE-2D pharmacy surface disposition    OPEN
        PILOT_INVITE_CODES_ARE_PUBLIC_LITERALS OPEN
NEXT_GENUINE_GATE=GATE_LIVE_APPLY (P1 — provision the database)
```

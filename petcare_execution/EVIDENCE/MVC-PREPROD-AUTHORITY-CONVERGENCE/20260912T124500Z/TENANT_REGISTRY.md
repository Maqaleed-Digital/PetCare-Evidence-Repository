# PRE-1 · the tenant registry foundation

```
TENANT_REGISTRY_IMPLEMENTED=YES
TENANT_ROWS_CREATED=0
TENANT_DEFAULT_PRESENT=NO
TENANT_INFERENCE_PRESENT=NO
```

## The gap this answers

PRE-1 asked which tenant three identities belonged to. The search returned
nothing, and the absence was the finding: no catalogue table in 33 migrations, no
foreign key, no governance artefact naming a tenant. `tenant_id` was an
unconstrained `TEXT` column, so a typo produced a new, empty, perfectly
functional scope that nothing would ever report.

A tenant is now a **governed object**: something that must exist before an
identity can belong to it.

## Migration 0034 — additive, and empty

```sql
CREATE TABLE tenant (tenant_id PK, display_name, status, created_at, disabled_at, …)
ALTER TABLE user_identity ADD CONSTRAINT fk_user_identity_tenant FOREIGN KEY …
ALTER TABLE app_session   ADD CONSTRAINT fk_app_session_tenant   FOREIGN KEY …
```

`NULL` remains permitted on both. An identity with **no** tenant assignment is
the legitimate state W0-C defines, failing closed downstream at
`require_tenant()` — and a foreign key does not constrain `NULL`, so the governed
absence survives while an invented value does not. A registry that forced every
identity to hold a tenant would force callers to invent one, which is the outcome
PRE-1 exists to prevent.

### `audit_event` deliberately has NO foreign key

Its `tenant_id` is `NOT NULL` and legitimately holds `UNATTRIBUTED` for events
from the unauthenticated UI probe. A foreign key would require an `UNATTRIBUTED`
row — **a fake tenant that every unauthenticated probe event would then appear to
belong to**. `TENANT-09` forbids that, and the instruction is explicit: do not
force a fake tenant merely to satisfy a foreign key.

```
AUDIT_EVENT_TENANT_FK=ABSENT_BY_DESIGN
```

### No rows

Not `tenant_jeddah_001`, not `tenant_riyadh_001` — those appear only in
EP-05/EP-06 test fixtures and no governance record establishes either. Promoting
a value whose authority is a file under `tests/` would afterwards be
indistinguishable from one the Sponsor chose.

## Controls

| ID | Control | Result |
|---|---|---|
| TENANT-01 | an unknown tenant assignment is denied — repository and foreign key | PASS |
| TENANT-02 | a tenant must exist before a tenant-scoped identity or session | PASS |
| TENANT-03 | a disabled tenant receives no new identity or session — the rule a foreign key **cannot** express | PASS |
| TENANT-04 | there is no default tenant; `platform` is not special and is not a row | PASS |
| TENANT-05 | nothing infers a tenant from an address, a role or a name | PASS |
| TENANT-06 | a cross-tenant session cannot resolve | PASS |
| TENANT-07 | a cross-tenant audit read is refused | PASS |
| TENANT-08 | foreign-key integrity, asserted by writing SQL directly (`SQLSTATE 23503`) | PASS |
| TENANT-09 | a missing registry fails closed rather than skipping the check | PASS |
| TENANT-10 | the migration cannot create the tenant it needs; the write fails and no identity lands | PASS |

```
TESTS=petcare_api/tests/test_tenant_registry.py   18 passed
```

## Both implementations perform the same refusals

The in-memory repositories take the registry too. A memory mode that accepted a
tenant the database would reject would mean the suite proves the weaker of the
two, and the control would first fail in production against the implementation
nobody had run.

The registry is a **required** constructor argument, without a default —
`tests/governance/test_tenant_scope_signatures.py` forbids a tenant-bearing
parameter that may be omitted, and it is right to: a registry that could be left
out is one that gets left out. Passing `None` explicitly is still allowed and
still fails closed; it is a decision at the call site rather than an omission.

## Recorded gap

```
TENANT_ASSIGNMENT_HAS_NO_GOVERNED_API=OPEN
```

Registration establishes identity and never tenant authority (W0-C), and no admin
route assigns a tenant. The only path today is an operator calling the identity
repository. Sufficient for a rehearsal, insufficient for an operated system — P5
needs an assignment path that is itself audited.

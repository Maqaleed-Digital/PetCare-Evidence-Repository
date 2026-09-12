# Genesis controls - what each clause of the ruling is proved by

## Section 2 - the procedure and its fixed role

| control | proof |
|---|---|
| resulting role is fixed to `platform_admin` | `test_g01`; `ROLE_PLATFORM_ADMIN` is a module constant written into the `INSERT` |
| no arbitrary role parameter | `test_the_genesis_procedure_has_no_role_parameter` - AST over the signature, so the property is the parameter's **absence**, not its validation. No `*args`/`**kwargs` either. |
| cannot create another privileged role | `test_g12` - `platform_admin_genesis.granted_role` has a CHECK admitting one value; the database refuses independently of the service |
| cannot elevate an existing identity | `test_the_genesis_procedure_never_updates_an_existing_identity` - `INSERT` only; no `UPDATE`, no `ON CONFLICT`, no upsert |
| no default credential | `test_g16` (blank refused, nothing written) and `test_the_genesis_path_embeds_no_credential` (no literal in module or script) |
| credential stays at the gate | `execute()` takes `password_hash`, never `password`; the script reads it from a TTY, never argv |

## Section 3 - tenant context

| control | proof |
|---|---|
| creates no tenant | `test_g02` - `SELECT count(*) FROM tenant` is 0 after the act |
| infers no tenant value | the administrator's `tenant_id` is `NULL`; no code path derives one |
| the ruled identifier stays out of creating code | `test_production_tenant_not_created.py` - which **fired during this lane** against the genesis module's own docstring, and the identifier was removed |

## Section 4 - the genesis audit record

| required | where it is |
|---|---|
| identifiable as a genesis event | `event_name = platform_admin.genesis` |
| the target identity | `resource_id` |
| the resulting role | carried in the event name; also `granted_role` in the consumption record |
| the tenant context | `tenant_id = UNATTRIBUTED` |
| the governing ruling | `reason_code` |
| the execution timestamp | `occurred_at` |
| the result | `action_result = success` |
| no invented actor | `actor_id` and `actor_role` are `UNATTRIBUTED`, neither in `ALLOWED_ROLES` (`test_g05`) |

The governed field set was **not** widened: all twelve fields are the existing
`GOVERNED_EVENT_FIELDS`. `test_g07` proves the chain still verifies afterwards.

## Section 5 - single use

| control | proof |
|---|---|
| proves no `platform_admin` exists | `test_g10` |
| proves the authority is unconsumed | `test_g09` |
| marked consumed | `test_g08` |
| second invocation fails closed | `test_g09` - with a **different** identity, so it proves single use rather than idempotence |
| the intended administrator exists | `test_g18` - readback via the consumption record, not by searching for any administrator |
| no additional privileged identity | `test_g17` - exactly one identity, one `platform_admin`, zero sessions |
| durable, not by convention | `test_g11` - asserted against the schema with the service bypassed entirely |

## Section 6 - transaction and failure semantics

| control | proof |
|---|---|
| no privileged identity without its audit record | `test_g13` - audit write forced to fail; no identity, no event, no ledger row |
| no audit record claiming an uncreated administrator | `test_g14` - consumption collision; zero audit events |
| fails closed without durable persistence | `test_g15` |

## Section 7 - steady state

| withheld | proof it stays withheld |
|---|---|
| a reusable bootstrap endpoint | `test_no_http_route_exposes_the_genesis_path`, `test_the_serving_application_does_not_import_the_genesis_path` |
| seed identities | `test_startup_creates_no_platform_admin` |
| default administrator credentials | `test_the_genesis_path_embeds_no_credential` |
| a second `platform_admin` | `test_g09`, `test_g11`, and the singleton PK + unique index |

## Sections 8 and 9 - the production boundary

`test_the_migration_creates_no_identity_and_consumes_nothing` proves applying
the chain is not the act. `P1_GENESIS_STEP-001.md` is a prepared step whose
every production value is `<INPUT_REQUIRED>`; executing it is `GATE_LIVE_APPLY`
plus `GATE_CREDENTIAL_ENTRY`, both `NOT_AUTHORIZED`.

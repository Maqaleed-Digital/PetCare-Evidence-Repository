# Perturbation matrix - every genesis control, armed

A control that passes proves nothing unless the state it forbids is reachable.
Each row below breaks exactly one property, runs the control that claims to
catch it, and requires that control to **fail**. Every file was restored
byte-for-byte afterwards and the restore was asserted, not assumed.

```
ARMED=13/13  VACUOUS=0
```

| # | perturbation | control | verdict |
|---|---|---|---|
| P-01 | add `role: str = 'owner'` to `execute()` | `test_the_genesis_procedure_has_no_role_parameter` | CONTROL_FAILED_AS_REQUIRED |
| P-02 | turn the identity `INSERT` into an upsert | `test_the_genesis_procedure_never_updates_an_existing_identity` | CONTROL_FAILED_AS_REQUIRED |
| P-03 | add a default administrator password literal | `test_the_genesis_path_embeds_no_credential` | CONTROL_FAILED_AS_REQUIRED |
| P-04 | drop the singleton primary key | `test_the_single_use_property_is_enforced_by_the_schema` | CONTROL_FAILED_AS_REQUIRED |
| P-05 | add an identity `INSERT` to the migration | `test_the_migration_creates_no_identity_and_consumes_nothing` | CONTROL_FAILED_AS_REQUIRED |
| P-06 | `import platform_admin_genesis` in `main.py` | `test_the_serving_application_does_not_import_the_genesis_path` | CONTROL_FAILED_AS_REQUIRED |
| P-09 | write provenance `SEED` instead of `GENESIS` | `test_g03_the_genesis_identity_carries_genesis_provenance` | CONTROL_FAILED_AS_REQUIRED |
| P-10 | set the audit `actor_id` to the target | `test_g05_the_genesis_event_actor_is_unattributed_and_never_invented` | CONTROL_FAILED_AS_REQUIRED |
| P-11 | accept an absent credential | `test_g16_genesis_refuses_to_invent_a_credential` | CONTROL_FAILED_AS_REQUIRED |
| P-12 | swallow `AuditWriteFailed` and report success | `test_g13_an_audit_failure_leaves_no_privileged_identity` | CONTROL_FAILED_AS_REQUIRED |
| P-13 | bind the administrator to a tenant | `test_g02_the_genesis_admin_holds_no_tenant_and_creates_none` | CONTROL_FAILED_AS_REQUIRED |
| P-07c | remove BOTH service preconditions + singleton PK + GENESIS unique index + count invariant | `test_g09_a_second_genesis_attempt_fails_closed` | CONTROL_FAILED_AS_REQUIRED |
| P-08b | remove the existing-administrator precondition + the count invariant | `test_g10_genesis_refuses_when_a_platform_admin_already_exists` | CONTROL_FAILED_AS_REQUIRED |

## The two that needed a second pass - recorded because the first answer was wrong

P-07 and P-08 were first run as single-line perturbations, removing one service
precondition each. **Both controls kept passing.** That reads at first like two
vacuous controls, and the honest options were a vacuous assertion or a layered
defence. They were re-run with the layers stripped one at a time:

| | layers removed | outcome |
|---|---|---|
| P-07a | the consumed-authority precondition | still failed closed |
| P-07c | + the existing-administrator precondition, the singleton PK, the GENESIS unique index, the count invariant | **control fired** |
| P-08a | the existing-administrator precondition | still failed closed |
| P-08b | + the post-write count invariant | **control fired** |

So the controls are live, and the single-use property does not rest on any one
check. That is the result section 5 asks for - *"enforced by durable production
state, not by operator memory or documentation alone"* - and it was
demonstrated rather than asserted. Had only the single-line runs been recorded,
the matrix would have reported two vacuous controls and been wrong.

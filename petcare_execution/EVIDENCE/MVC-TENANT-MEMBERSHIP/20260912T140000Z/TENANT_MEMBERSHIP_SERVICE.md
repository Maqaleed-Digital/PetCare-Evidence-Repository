# The governed tenant-assignment control path

```
GOVERNED_PATH_IMPLEMENTED=YES    petcare_api/tenant_membership.py
ROUTES=POST /api/admin/identities/{user_id}/tenant   (assign · reassign · revoke)
       GET  /api/admin/identities/{user_id}/tenant   (readback)
AUTHORITY=platform_admin, from the validated session
AUDIT_MODEL=TWO_EVENT
ROLE_PARAMETER=ABSENT
DIRECT_REPOSITORY_ACCESS=NOT_AN_AUTHORIZED_SERVING_PATH
```

## The twelve authorized proof points

| # | Ruling requirement | Control |
|---|---|---|
| 1 | implement the governed service/API | `petcare_api/tenant_membership.py` + two routes |
| 2 | the API accepts no role parameter | `test_the_request_model_has_no_role_field`, `test_a_role_field_in_the_body_is_rejected_outright` (×4), `test_the_service_signature_takes_no_target_role` |
| 3 | assignment, reassignment, revocation | `test_a_first_assignment_writes_the_addition_event_only`, `test_a_reassignment_is_visible_in_each_tenants_own_audit_history`, `test_a_revocation_writes_the_removal_event_only` |
| 4 | the two-event audit model | as above, plus `test_no_previous_tenant_field_was_added_to_the_governed_record`, `test_the_reason_field_carries_no_encoded_tenant_transition` |
| 5 | old- and new-tenant audit visibility, independently | `test_a_reassignment_is_visible_in_each_tenants_own_audit_history`, `test_the_tenant_scoped_read_shows_each_tenant_only_its_own_event` |
| 6 | first assignment and revocation semantics | the two single-event controls above |
| 7 | cross-tenant administration | `test_a_platform_admin_administers_membership_across_tenants`, `test_a_tenantless_platform_admin_can_still_administer` |
| 8 | unauthorized actors refused | `test_a_non_admin_cannot_change_membership` (×2), `test_an_unauthenticated_caller_cannot_change_membership`, `test_a_header_cannot_assert_the_admin_role`, `test_a_denied_attempt_writes_no_membership_audit_event` |
| 9 | unknown and disabled tenants fail closed | `test_an_unknown_tenant_fails_closed`, `test_a_disabled_tenant_fails_closed`, `test_an_unknown_and_a_disabled_tenant_are_one_answer` |
| 10 | repository-direct mutation is not an authorized path | `test_no_route_other_than_the_governed_one_writes_tenant_membership`, `test_a_direct_repository_write_produces_no_audit_event`, `test_the_governed_path_refuses_to_operate_on_a_non_durable_store` |
| 11 | tenant changes do not alter role authority | `test_a_membership_change_leaves_the_role_untouched` (×3), `test_a_membership_change_cannot_grant_platform_admin`, `test_the_target_route_authority_is_unchanged_after_a_move` |
| 12 | end-to-end with synthetic fixtures | the whole suite, against ephemeral PostgreSQL; no production tenant or identity exists |

```
TESTS=petcare_api/tests/test_tenant_membership_postgres.py   39 passed
```

## `TENANT_ASSIGNMENT != ROLE_ASSIGNMENT`, implemented as an absence

The ruling forbids the path from accepting a role or changing one. That is
implemented by **not having the parameter**, not by validating it:

- `TenantMembershipRequest` has exactly `tenant_id` and `reason`, with
  `extra="forbid"` — a smuggled `role`, `actor_role`, `new_role` or
  `target_role` is rejected with `422` before any handler runs.
- `set_membership` has no target-role parameter. `actor_id` and `actor_role`
  describe the **caller**, are read from the validated session, and are written
  only into the audit record's actor fields.
- The identity write names one column: `UPDATE user_identity SET tenant_id = …`.
- The service re-reads the role after the update and **rolls back** if it
  changed. Belt and braces on a path whose whole purpose is to be unable to
  escalate.

A parameter that does not exist cannot be misused, and a field that is never
named cannot be overwritten.

## One transaction, because ordering cannot save it

`audit_event` and `user_identity` are in the same database, so the change and its
records commit together via `append_event_on`, which appends inside a
caller-owned transaction.

Ordering alone is not sufficient, and it is worth stating why:

```
record first → a failed update leaves a log entry for a change that did not happen
update first → a failed record leaves an unaudited mutation
```

Both are worse than a rollback. `test_a_failure_leaves_neither_the_identity_nor_the_log_changed`
induces a failure after both events are written and asserts the identity did not
move, no audit rows survived, and the chain still verifies.

Two appends in one transaction take the chain-head lock once and receive
consecutive sequence numbers — asserted by
`test_the_two_events_of_one_change_are_consecutive_in_the_chain`, so nothing
interleaves between the removal and the addition of a single change.

## Why the two-event model was necessary, not stylistic

`query_events_for_tenant` filters on a single `tenant_id`. A reassignment
recorded once, under the destination, would leave **the tenant an identity left
with no record that it left** — its own audit history would show its perimeter
unchanged. The removal event scoped to the origin is what closes that.

The governed field set is unchanged at twelve fields, and the old→new pair is not
encoded into `reason_code`: the ruling forbids hiding structured state in an
unvalidated field, and a control asserts neither tenant id appears there.

## A guard extended rather than widened

`test_t_ten_06_no_route_trusts_body_tenant_directly` fired on the new route: a
`body.tenant_id` not wrapped by `require_tenant()`.

It is a true new case rather than a defect. `require_tenant()` answers *"which
tenant may THIS CALLER act on"* — and a `platform_admin` administering across
tenants is authorised to act outside its own scope by ruling. Wrapping the
destination in it would be wrong twice.

The guard now carries a named, bound exemption for administrative destinations,
stating the authority that replaces tenant-scope authorization
(`require_admin` + validation against the governed registry) and binding to the
control that proves it. A second control asserts the exempted route still exists
and that the reason still names its authority — an exemption whose route has
moved protects nothing while reading as a considered decision.

## Boundary

```
PRODUCTION_TENANT_CREATED=NO      PRODUCTION_IDENTITY_CREATED=NO
LIVE_DB_TOUCHED=NO                SECRET_CREATED=NO
SYNTHETIC_FIXTURES_ONLY=YES       (they acquire no production authority)
P1_AUTHORIZED=NO
```

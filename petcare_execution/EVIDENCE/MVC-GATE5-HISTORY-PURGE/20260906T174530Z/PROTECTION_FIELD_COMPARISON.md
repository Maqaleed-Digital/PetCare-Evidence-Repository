# Protection — field-for-field comparison against the required state

Live read of `repos/Maqaleed-Digital/PetCare-Evidence-Repository/branches/main/protection`,
performed in this closeout, and again from the fresh clone.

| field | required | live | verdict |
|---|---|---|---|
| `required_status_checks.strict` | `true` | `true` | PASS |
| `required_status_checks.checks` length | `1` | `1` | PASS |
| `required_status_checks.checks[0].context` | `verify` | `verify` | PASS |
| `required_status_checks.checks[0].app_id` | `15368` | `15368` | PASS |
| `enforce_admins.enabled` | `true` | `true` | PASS |
| `required_pull_request_reviews` | `null` | absent (null) | PASS |
| `restrictions` | `null` | absent (null) | PASS |
| `allow_force_pushes.enabled` | `false` | `false` | PASS |
| `allow_deletions.enabled` | `false` | `false` | PASS |
| `required_linear_history.enabled` | `false` | `false` | PASS |
| `required_conversation_resolution.enabled` | `false` | `false` | PASS |
| `block_creations.enabled` | `false` | `false` | PASS |
| `lock_branch.enabled` | `false` | `false` | PASS |
| `allow_fork_syncing.enabled` | `false` | `false` | PASS |

```
PROTECTION_RESTORED           = YES
PROTECTION_RESTORED_IDENTICAL = YES
REQUIRED_CHECK                = verify
REQUIRED_CHECK_APP_ID         = 15368
STRICT                        = true
ADMIN_ENFORCEMENT             = true
ALLOW_FORCE_PUSHES            = false
ALLOW_DELETIONS               = false
```

`app_id` is checked explicitly. A required check named `verify` supplied by a
different app would satisfy a name-only comparison while silently changing who
can satisfy the gate; that is why the id is pinned and asserted separately.

A `diff` of the writable-field projection of the live response against
`PROTECTION_BEFORE.json` is **empty**.

# Identity migration — reconciliation report

```
IDENTITY_SOURCE_COUNT=3
IDENTITY_MIGRATABLE_COUNT=0
IDENTITY_QUARANTINED_COUNT=3
IDENTITY_REJECTED_COUNT=0
APPLIED=NO (dry run — zero authoritative rows written)
```

## Reconciliation checks (plan §12)

| check | result |
|---|---|
| no_row_lost | PASS |
| no_row_invented | PASS |
| no_role_elevated | PASS |
| no_migrated_row_without_tenant | PASS |
| no_email_appears_twice | PASS |
| every_hash_is_a_known_format | PASS |
| no_plaintext_password_present | PASS |

## Quarantine

| source_record_id | reason | source_role | source_tenant |
|---|---|---|---|
| `u-admin-001` | UNRESOLVED_NO_TENANT | `platform_admin` | `None` |
| `u-vet-001` | UNRESOLVED_NO_TENANT | `veterinarian` | `None` |
| `u-owner-001` | UNRESOLVED_NO_TENANT | `owner` | `None` |

## Counts by reason

```
UNRESOLVED_NO_TENANT=3
```


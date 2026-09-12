# A8 — ephemeral PostgreSQL audit proof

```
POSTGRES_TEST_BACKEND=POSTGRESQL
POSTGRES_TEST_VERSION=16.11 (local ephemeral) / postgres:16 (CI service)
POSTGRES_TEST_LOCATION=LOCAL_EPHEMERAL
LIVE_DB_TOUCHED=NO
CLOUD_RESOURCE_TOUCHED=NO
MIGRATIONS_IN_CHAIN=37
MIGRATIONS_APPLIED_CLEANLY=37
```

| Proof | Result |
|---|---|
| the migration chain applies from empty | 37/37, no errors |
| `audit_event` exists with `prev_hash`, `event_hash`, `chain_seq` | YES |
| `audit_chain_head` exists, seeded `('default','GENESIS',1)` | YES |
| a real application flow persists an event | YES — sign-in then `POST /api/appointments` writes a row |
| row fields reflect SERVER-established identity and tenant | YES — tenant from the session, actor prefixed when client-asserted |
| the chain verifies | YES |
| mutation breaks verification | YES — `UPDATE` → `hash_mismatch`; `DELETE` → `prev_hash_mismatch` |
| a cross-tenant read is refused | YES |
| restart does not erase history | YES — a NEW repository over the same database sees the same count and verifies |
| the chain continues across instances | YES — a second repository links to the first's last event rather than restarting at GENESIS |
| migration re-run works through the ledger | YES — `apply_migrations.py`: 37 applied, then 0 |

## A defect the fixture caught

Six controls failed together in one file and every one passed alone. The
per-test reset emptied `audit_event` but not `audit_chain_head`, so the head
pointed at the digest of a row that no longer existed: the next test's first
append linked to a vanished predecessor and `verify_chain` reported
`prev_hash_mismatch` — **a clean chain reported as tampering, in a test that did
nothing wrong**.

That is precisely the failure mode the head row exists to prevent, arriving from
the other direction. The fixture now resets the head with the rows.

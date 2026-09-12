# A16 — audit + role + tenant, integrated

```
AUDIT_INTEGRATION_RESULT=PASS
```

The three W0 surfaces now meet on one row. A governed route completing writes an
`audit_event` whose:

- **tenant** comes from the validated session (never a body or a header) and
  names a tenant that exists in the registry;
- **actor role** is the canonical machine id the identity actually holds;
- **chain position** is allocated under the `audit_chain_head` row lock, so
  concurrent writes cannot fork the chain into a false tamper report;
- **verification** passes, and fails on an `UPDATE` or a `DELETE`.

Proven in `test_the_full_governed_identity_path` steps 7–10 against PostgreSQL,
and by the 22 AUD controls carried forward unchanged from the W0-G lane.

## Cross-tenant, on all three surfaces

| Surface | Control | Result |
|---|---|---|
| session | a tenant-A session cannot resolve in tenant B | PASS |
| route | a body naming another tenant is refused `403 TENANT_SCOPE_DENIED` | PASS |
| audit | a tenant-scoped read returns no other tenant's events; `get_event` gives no oracle | PASS |

## RULE 19 — the integrity mechanism does not produce false tamper findings

Recorded because this lane's predecessor produced one. The W0-G fixture emptied
`audit_event` without resetting `audit_chain_head`, so the next append linked to a
vanished predecessor and `verify_chain` reported `prev_hash_mismatch` — **a clean
chain reported as tampering, in a test that did nothing wrong**.

That is exactly the defect RULE 19 names, and it was in the harness rather than
the mechanism. The chain's ordering and concurrency semantics are built so that
ordinary correct operation cannot produce a false positive:

- ordering is by `chain_seq`, allocated under the head lock — never by
  `occurred_at`, which is `TEXT` and ties;
- linkage is one transaction serialised on one row, so two concurrent appends
  cannot both claim the same predecessor;
- the reset path now restores the head with the rows.

`test_the_chain_continues_across_repository_instances` asserts the positive
form: a second repository instance links to the first's last event rather than
restarting at genesis.

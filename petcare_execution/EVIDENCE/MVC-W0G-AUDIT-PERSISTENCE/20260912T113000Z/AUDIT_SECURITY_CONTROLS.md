# A6 — audit security controls

```
TESTS=petcare_api/tests/test_audit_persistence_postgres.py   22 passed
      petcare_api/tests/test_audit_chain_wired.py             6 passed
      petcare_api/tests/test_audit_probe_authority.py         6 passed
```

| ID | Control | Result |
|---|---|---|
| AUD-01 | an unauthenticated write produces no authoritative record — tenant `UNATTRIBUTED`, actor and role `client-asserted:` prefixed | PASS |
| AUD-02 | a client-supplied tenant cannot override the session tenant | PASS |
| AUD-03 | a client-supplied actor cannot become an authenticated actor | PASS |
| AUD-04 | a client-supplied role can never match a real role — asserted across every member of `VALID_ROLES` | PASS |
| AUD-05 | a tenantless identity is refused a tenant-scoped read with `403 NO_TENANT_AUTHORITY` | PASS |
| AUD-06 | a tenant-scoped read cannot return another tenant's events; a query parameter cannot select the tenant; `get_event` gives no cross-tenant oracle | PASS |
| AUD-07 | a legitimate persisted chain verifies | PASS |
| AUD-08 | modifying a persisted row breaks verification — `hash_mismatch` at the right index | PASS |
| AUD-09 | a forged event is chained like any other and is still never authoritative | PASS |
| AUD-10 | a real governed route writes an `audit_event` row to PostgreSQL | PASS |
| AUD-11 | an in-memory-only path cannot satisfy AUD-10 | PASS |
| AUD-12 | an unreachable store fails closed rather than dropping events | PASS |

## AUD-09 is the one worth reading twice

An event filed through the unauthenticated probe is hashed and linked like any
other, **and the chain verifies**. The integrity proof lends the forgery its own
credibility. What stops it being authoritative is that its identity fields are
neutralised at the boundary — not that the chain rejected it.

That is why persistence does not close W0-G's open ARCH-01 question, and why the
control asserts the limit rather than leaving verification to imply more than it
proves.

## AUD-01 is phrased as "no authoritative record", not "denied"

`POST /audit/ui` is unauthenticated **by design**: it accepts events from a
surface that may have no session yet, so it cannot be gated. The property W0-G
hardened, and this preserves now that the record is durable, is that the caller
cannot choose what the record says about identity.

## AUD-12 and unaudited mutation

`append_event` raises `AuditWriteFailed` and nothing catches it to continue. An
action that mutates state while its audit write silently fails is an unaudited
mutation, and afterwards it is indistinguishable from an action that never
happened. Failing the request is the direction that keeps the log a record of
what occurred.

## Global / platform events

No default tenant was reintroduced to accommodate them. `UNATTRIBUTED` is a
sentinel for the one surface with a governed decision behind it, and
`test_unattributed_is_not_a_real_scope` asserts it is not a usable scope.
Authentication events remain outside the chain rather than being given a tenant —
see `SERVING_PATH_REACHABILITY.md`.

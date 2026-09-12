# A5 — every audit write path, inventoried

RULE 16: a repository that exists but is never reached delivers nothing.

## Authoritative writer — `main.py::_audit()`

Ten governed call sites, plus the UI probe. All now reach
`AUDIT_REPO.append_event()`; none appends to a list.

| CALL_SITE (main.py) | ROUTE / SERVICE | AUTHORITY_SOURCE | TENANT_SOURCE | ACTOR_SOURCE | REPOSITORY_REACHED | PERSISTED |
|---|---|---|---|---|---|---|
| 333 | `POST /audit/ui` | none — unauthenticated by design | session if present, else `UNATTRIBUTED` | `client-asserted:` prefixed | YES | YES |
| 395 | `POST /api/appointments` | `require_role` (session) | `require_tenant` (session) | `X-Actor-Id` + session role | YES | YES |
| 418 | appointments — denial path | same | same | same | YES | YES |
| 467 | `GET /api/pets/{id}/timeline` | same | same | same | YES | YES |
| 490 | timeline — denial path | same | same | same | YES | YES |
| 537 | consultation session | same | same | same | YES | YES |
| 568 | consultation note | same | same | same | YES | YES |
| 621 | `POST /api/prescriptions` | same | same | same | YES | YES |
| 644 | prescriptions — denial path | same | same | same | YES | YES |
| 689 | dispense | same | same | same | YES | YES |
| 726 | consent | same | same | same | YES | YES |

```
SHADOW_AUTHORITATIVE_LIST=NONE
```

`_audit_log` no longer exists. It was replaced rather than shadowed: a second
copy would be a second source of truth, and the one that disagreed would be the
one nobody was reading.

## Non-authoritative writer — `routers/auth.py`

Thirteen call sites, previously behind a function **also named `_audit`**. Two
functions with the same name, one authoritative and one not, is how a reviewer
comes to believe authentication events are in the audit log.

Renamed `_log_auth_event`, with a docstring stating plainly that nothing it
writes is hashed, linked, persisted or verifiable.

| CALL_SITE | EVENT | REPOSITORY_REACHED | PERSISTED |
|---|---|---|---|
| auth.py ×13 | `auth.sign_in_failed` / `_success`, `auth.register_failed`, `auth.user_registered`, `auth.me_called`, `auth.sign_out` | NO — log line only | NO |

### Why these are NOT routed into the chain

A governed record requires a tenant — `audit_event.tenant_id` is `NOT NULL` — and
these events are mostly **pre-authentication**: a failed sign-in has no
authenticated actor, no established tenant, and frequently no identity at all.

Routing them in would require inventing a tenant, and a default tenant is exactly
what W0-C removed and what the audit probe's own hardening refuses to
reintroduce. `UNATTRIBUTED` exists for the UI probe because a governed decision
stands behind it; extending it to authentication would be taking that decision by
implementation.

```
AUTH_EVENTS_OUTSIDE_AUDIT_CHAIN=OPEN_GAP_RECORDED
```

Closing it needs a governed answer on how a tenantless security event is
recorded. It is recorded rather than closed by guessing.

## Read paths

| ROUTE | AUTHORITY | SCOPE |
|---|---|---|
| `GET /audit/events` | `require_admin` | whole chain — privileged and cross-tenant by necessity, since the chain is one sequence over every tenant |
| `GET /audit/events/tenant` | `require_tenant` (session) | the caller's tenant only; a query parameter cannot choose it |
| `GET /audit/chain/verify` | `require_admin` | whole chain |

## One field that would have become a false claim

`/api/governance/status` returned the fixed string
`"IN_PROCESS_ONLY — … persistence is W0-F"`. True when written; **false** the
moment the service is configured for a durable store — the MVC-INC-ATTEST-001
defect inverted, a service misreporting a control it now has. It is now computed
from the configured repository, and `audit_chain_persisted` and
`audit_chain_active` remain two separate fields, because a chain over a volatile
store is a real control against tampering and a real non-control against loss.

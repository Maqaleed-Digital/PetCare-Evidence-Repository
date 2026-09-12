# CONF-01 — closed

```
CONF01_STATUS=CLOSED
```

## What the defect was

Three vocabularies. The serving layer minted machine ids, `require_role()`
accepted only the display forms, and the web middleware aliased the machine ids.

> **Every identity the system created was refused by every protected route with
> `403 Unknown role`.**

The suite did not show it because tests that needed a working session seeded the
display spelling directly — a value no production path ever produced. That is the
blind spot, and it is why the closure proof below refuses to use a fixture.

## The proof

`test_conf01_a_registered_identity_is_no_longer_refused_as_an_unknown_role`
drives the REAL registration endpoint:

```
POST /api/auth/register  (invite-gated, role=owner)     -> 201
  minted role == "owner"                                 the CANONICAL id
POST /api/appointments   (with the registered session)  -> 403 NO_TENANT_AUTHORITY
```

The 403 is the point. Before 2-C this request produced `403 Unknown role` from
`require_role` — a string detail, because the system did not recognise its own
vocabulary. It now produces `403 NO_TENANT_AUTHORITY` from `require_tenant`,
which runs *after* the role guard has accepted the role and after the route's own
role set has admitted it.

**Two 403s that mean opposite things**: one says the system rejects the
vocabulary it mints; the other says this identity has no scope yet, which is W0-C
working exactly as designed — registration establishes identity, never tenant
authority.

## The full path, to 200

`test_the_full_governed_identity_path` (PostgreSQL) carries it the rest of the
way: registration → canonical role → deliberate tenant assignment → sign-in →
permitted route `201` → persisted `audit_event` → chain verified → cross-tenant
refused → session revoked → refused.

No seed helper. No direct database fixture for the user.

## Stated as a set equality

```python
assert api.VALID_ROLES is roles_module.ALLOWED_ROLES
```

The minted vocabulary and the accepted vocabulary are now the SAME OBJECT, not
two sets that happen to agree. CONF-01 was exactly those two sets differing.

# Consent Registry — Purpose Enforcement at the API Layer

## Enforcement Points

Purpose-limitation enforcement occurs at two layers:

1. **API layer** (this document): `consent_registry` validates that the `purpose` in a
   `ConsentCheckRequest` matches the declared purpose of the requested `scope_id`.
2. **Caller layer**: Downstream services must call `/v1/consent/check` *before* accessing
   owner data, not after. Skipping this check is a policy violation.

## Purpose Matching Algorithm

```
function check_purpose(scope_id, purpose, caller_role):
  scope = CONSENT_SCOPE_MAP[scope_id]
  if scope is null:
    return DENY("UNKNOWN_SCOPE")
  if purpose != scope.purpose:
    return DENY("PURPOSE_MISMATCH — declared purpose does not match scope definition")
  if caller_role not in scope.permitted_roles:
    return DENY("ROLE_NOT_PERMITTED_FOR_SCOPE")
  return ALLOW
```

Callers may not substitute a different purpose string to access a scope defined for another
purpose. Any mismatch returns `403 FORBIDDEN_CONSENT_REQUIRED` with
`reason: "PURPOSE_MISMATCH"`.

## Consent Check Audit

Every call to `POST /v1/consent/check` emits a `consent_checked` event to `audit_ledger`
regardless of the outcome (ALLOW or DENY). The event includes:

- `owner_id` (opaque UUID)
- `scope_id`
- `caller_role`
- `purpose`
- `outcome` (`allow` or `deny`)
- `ts_utc`

## Revocation Propagation

When a revocation is processed:

1. `ConsentRecord.status` set to `revoked`.
2. `consent.revoked` event published to internal event bus.
3. Downstream services must invalidate cached consent decisions within **5 minutes**.
4. `consent_revoked` audit event emitted to `audit_ledger`.

If the event bus is unavailable, the revocation is still persisted and will propagate
on next bus reconnection. Downstream services must re-check consent before each operation
— caching consent for more than 5 minutes is prohibited.

## Prohibited Patterns

| Pattern                                             | Response                          |
|-----------------------------------------------------|-----------------------------------|
| Calling `/check` after accessing data (retroactive) | N/A — consent check has no effect post-access; audit will show gap |
| Using `purpose: "veterinary_care"` to access pharmacy data | `403 FORBIDDEN_CONSENT_REQUIRED: PURPOSE_MISMATCH` |
| Polling `/check` to infer consent state (>60 req/min)| `429 RATE_LIMITED_CONSENT_CHECK` |

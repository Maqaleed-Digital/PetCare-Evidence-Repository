# Audit Ledger — Immutability Rules

## Core Guarantee

Once an event is appended to `audit_ledger`, it **cannot be modified or deleted** for the
duration of its retention period. This guarantee is enforced at multiple layers.

## Hash Chain

Each event stores `prev_hash = SHA-256(canonical_json(event[n-1]))`. The genesis event
uses `prev_hash = "0" × 64`. Any modification to a historical event invalidates the chain
from that point forward, which is detectable by `/v1/audit/verify`.

### Verification

```
GET /v1/audit/verify?from_sequence=0&to_sequence=latest
→ { "valid": true|false, "broken_at_sequence": null|<int>, "checked": <int> }
```

Verification is run:
- On every node restart
- Daily via scheduled job at 03:00 UTC
- On demand by `admin` role

## Storage Constraints

| Constraint                         | Enforcement                                              |
|------------------------------------|----------------------------------------------------------|
| No `UPDATE` on audit rows          | Database role `audit_writer` has `INSERT` only           |
| No `DELETE` on audit rows          | Database role `audit_writer` has no `DELETE` privilege   |
| Schema migrations are additive only | Column drops blocked by migration linter                 |
| Replica required                   | Write to primary; replica verified within 60s            |

## Retention Enforcement

| Event category          | Minimum retention | Authority          |
|-------------------------|-------------------|--------------------|
| All audit events        | 3 years           | PDPL Article 19    |
| Access-denial events    | 3 years           | PDPL Article 19    |
| Consent change events   | 3 years post-expiry | PDPL Article 19  |
| Clinical signoff events | 5 years           | Saudi MoH guidance |

Events past retention are **archived** (cold storage, encrypted), not deleted, until a formal
data-destruction request is approved by legal.

## Purge Exemptions

No event may be purged if:
- It is referenced by an open regulatory inquiry.
- It relates to a consent currently under dispute.
- Its retention period has not elapsed.

Purge requests must be approved by two admins and logged in the purge-approval audit trail
(which is itself immutable).

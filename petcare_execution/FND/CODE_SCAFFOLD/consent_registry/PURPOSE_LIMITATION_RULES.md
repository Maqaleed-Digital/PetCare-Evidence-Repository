# Consent Registry — Purpose Limitation Rules

## Principle

Data collected for one purpose must not be used for an incompatible purpose without fresh
consent. This is codified in PDPL Article 5 and enforced at runtime by `consent_registry`.

## Enforcement Model

Before any service accesses a data category, it must call:

```
GET /v1/consent/{owner_id}/check?scope={scope_id}&caller_role={role}&purpose={purpose}
→ { "allowed": true|false, "reason": "...", "expires_at": "..." }
```

The registry evaluates:
1. Is the `scope_id` granted for this `owner_id`?
2. Is the `caller_role` listed in `permitted_roles` for the scope?
3. Is the `purpose` exactly the purpose declared in the scope?
4. Has the consent not expired?

If all four checks pass → **ALLOW**. Otherwise → **DENY** (logged to `audit_ledger`).

## Purpose Codes

| Purpose Code             | Description                                          | Allowed Scopes                         |
|--------------------------|------------------------------------------------------|----------------------------------------|
| `veterinary_care`        | Diagnosis, treatment, preventive care                | cs-health-read, cs-health-write        |
| `medication_dispensing`  | Prescription fulfilment and dispensing               | cs-pharmacy                            |
| `emergency_care`         | Life-threatening emergency triage and treatment      | cs-emergency                           |
| `governance_compliance`  | Internal SLA and audit monitoring                    | cs-audit-admin                         |
| `regulatory_compliance`  | SDAIA / PDPL regulatory reporting                    | cs-evidence-export                     |

## Prohibited Repurposing

| Original Purpose     | Prohibited Secondary Use                      | Enforcement                        |
|----------------------|-----------------------------------------------|------------------------------------|
| `veterinary_care`    | Marketing, insurance risk scoring             | Hard deny — no override            |
| `emergency_care`     | Routine health profiling after emergency ends | Auto-expire cs-emergency after 72h |
| `medication_dispensing` | Pharmaceutical research without fresh consent | Hard deny                       |

## Consent Expiry

| Scope ID          | Default TTL      | Renewable |
|-------------------|------------------|-----------|
| cs-health-read    | No expiry        | N/A       |
| cs-health-write   | No expiry        | N/A       |
| cs-pharmacy       | Per prescription | Yes       |
| cs-emergency      | 72 hours         | No (fresh consent required) |
| cs-audit-admin    | No expiry        | N/A       |
| cs-evidence-export | 90 days         | Yes       |

## Revocation Propagation

On revocation of any scope, `consent_registry` publishes a `consent.revoked` event to the
internal event bus. All downstream services must flush cached consent decisions within
**5 minutes** of receiving this event.

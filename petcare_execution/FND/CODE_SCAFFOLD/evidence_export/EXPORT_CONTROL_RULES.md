# Evidence Export — Export Control Rules

## Purpose

These rules govern which data may be exported, who may request exports, and what controls
must be applied before an artifact is released.

## Authorisation

Only principals with the `admin` role and the `cs-evidence-export` consent scope active may
create or download export artifacts.

Two-admin approval is required for:
- `full_compliance` export type
- Any export covering more than 12 months of data
- Any cross-border export

## Pre-Export Checks

Before an export artifact is generated, `evidence_export` enforces:

| Check                          | Rule                                                              |
|--------------------------------|-------------------------------------------------------------------|
| Caller role                    | Must be `admin`                                                   |
| Consent scope                  | `cs-evidence-export` must be `ACTIVE` for caller's clinic        |
| Pseudonymisation               | PII fields replaced with pseudonyms before inclusion             |
| Cross-border flag              | If `cross_border == true`, SDAIA approval reference required     |
| Date range sanity              | `from_date` < `to_date`; max range 24 months per request         |
| Dual approval (if required)    | Second admin `approval_id` verified against `identity_rbac`       |

## Pseudonymisation Rules

| Field Type          | Transformation                                |
|---------------------|-----------------------------------------------|
| Owner name          | Replace with `OWNER-{sha256(owner_id)[:8]}`   |
| Pet name            | Replace with `PET-{sha256(pet_id)[:8]}`       |
| Phone number        | Redacted → `REDACTED`                         |
| Vet name            | Replace with `VET-{sha256(vet_id)[:8]}`       |
| Principal UUID      | Retained as-is (opaque, not PII)              |
| Event timestamps    | Retained as-is                                |

## Artifact TTL and Purge

| Export type         | Default TTL | Max TTL |
|---------------------|-------------|---------|
| `audit_log`         | 30 days     | 30 days |
| `consent_snapshot`  | 30 days     | 30 days |
| `governance_report` | 90 days     | 90 days |
| `full_compliance`   | 90 days     | 90 days |

After TTL expiry, the artifact is automatically deleted and an `export_expired` audit event
is emitted. No extension of TTL is permitted; a new export must be requested.

## Download Limits

- Maximum 3 downloads per artifact lifetime.
- Each download emits an `export_downloaded` event to `audit_ledger`.
- Download links are pre-signed and expire after 1 hour.

## Prohibited Exports

The following are blocked at the API layer with no override:
- Raw (non-pseudonymised) personal data
- Clinical notes or prescriptions in any form
- Cross-border exports without SDAIA approval reference
- Exports initiated by suspended or inactive principals

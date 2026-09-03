# G-S1 — Audit Event Taxonomy (post-P02)

## Auth events
| Event | Source |
|-------|--------|
| `access.denied` | `require_role()` — every 403 |
| `auth.role_resolved` | Caller of role-redirect logic |

## MFA events
| Event | Source |
|-------|--------|
| `mfa.otp_generated` | `generate_otp()` |
| `mfa.verified` | `verify_otp()` success |
| `mfa.failed` | `verify_otp()` — no_record / expired / invalid |

## Admin hub events (Fix-F3 aliases)
| Event | Source | Notes |
|-------|--------|-------|
| `platform_admin.viewed` | Admin hub access, platform_admin role | New role-specific event |
| `clinic_admin.viewed` | Admin hub access, clinic_admin role | New role-specific event |
| `admin_hub.viewed` | Admin hub access, any admin role | DEPRECATED alias — remove v2.0 |

## Clinical events (P01)
| Event | Source |
|-------|--------|
| `consultation.created` | POST /api/consultations |
| `consultation.signed` | POST /api/consultations/{id}/sign |
| `consultation.tamper_attempt` | PATCH on immutable consultation |
| `adverse_event.reported` | POST /api/adverse-events |
| `adverse_event.status_updated` | PATCH /api/adverse-events/{id}/status |

## All events stored in
Table: `audit_events` (append-only, no UPDATE/DELETE in application code)
Fields: `id` (UUID), `event_type`, `payload` (JSON), `created_at` (UTC)

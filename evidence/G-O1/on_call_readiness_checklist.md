# G-O1 — On-Call Readiness Checklist

## Pre-Shift Handover

- [ ] `/api/health` is returning 200 with `db_latency_ms < 50`
- [ ] No open P1/P2 incidents from previous shift
- [ ] Synthetic monitor is active and last check was green
- [ ] PagerDuty rotation confirmed for this shift

## Access Verification

- [ ] SSH access to backend host confirmed
- [ ] `platform_admin` credentials available (MFA device ready)
- [ ] SQLite database file path known and accessible
- [ ] Backend log path accessible (`/var/log/veticare/backend.log`)
- [ ] Audit events query access verified

## Runbook Familiarity

- [ ] P1 DB unavailable runbook reviewed
- [ ] P2 elevated latency runbook reviewed
- [ ] Pharmacy dispense block runbook reviewed
- [ ] Escalation path contacts saved in phone

## Key Endpoints (bookmark)

| Endpoint | Purpose |
|----------|---------|
| `GET /api/health` | Primary health check — DB status + latency |
| `GET /api/admin/audit-events` | Recent audit event stream |
| `POST /api/admin/recalls` | Issue SFDA recall (platform_admin) |

## Monitoring Thresholds to Watch

| Signal | Warning | Critical |
|--------|---------|---------|
| `db_latency_ms` | > 100 ms | > 200 ms or null |
| HTTP 5xx rate | > 1% | > 5% |
| `/api/health` status | `degraded` | `unhealthy` (503) |
| `audit_events` write failures | Any | Any (regulated events) |

## End-of-Shift Handover

- [ ] Document any incidents, anomalies, or changes made during shift
- [ ] Confirm open incidents are tracked and handed over
- [ ] Run final `/api/health` check and record result in shift log
- [ ] Confirm next on-call engineer has acknowledged rotation

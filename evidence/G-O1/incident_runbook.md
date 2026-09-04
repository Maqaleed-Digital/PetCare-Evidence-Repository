# G-O1 — Incident Runbook: VetiCare Backend

## Severity Definitions

| Severity | Criteria | Response time |
|----------|----------|---------------|
| **P1 — Critical** | `/api/health` returns 503; all DB operations failing; data loss risk | 15 min |
| **P2 — High** | Error rate > 5%; DB latency > 200 ms p95; single route class down | 30 min |
| **P3 — Medium** | Elevated latency (< 2× SLO breach); non-critical route failure | 4 hours |
| **P4 — Low** | Single user impact; cosmetic / logging issues | Next business day |

---

## Runbook: P1 — Database Unavailable (`/api/health` returns 503)

### Symptoms
- `GET /api/health` → HTTP 503, `checks.database: false`
- All write endpoints returning 500
- `db_latency_ms: null` in health response

### Diagnosis steps

```bash
# 1. Check health endpoint directly
curl -s https://<host>/api/health | python3 -m json.tool

# 2. Inspect SQLite database file (non-prod)
ls -lh ~/dev/petcare-platform/petcare.db
file ~/dev/petcare-platform/petcare.db

# 3. Check backend logs for SQLAlchemy errors
tail -200 /var/log/veticare/backend.log | grep -E "(ERROR|CRITICAL|sqlalchemy)"

# 4. Verify process is running
ps aux | grep uvicorn
```

### Resolution
1. If SQLite file corrupted → restore from last backup; re-run `create_tables()` migration
2. If disk full → free space; restart uvicorn
3. If process crashed → `systemctl restart veticare-backend` (or equivalent)
4. Verify recovery: `GET /api/health` → 200, `checks.database: true`

---

## Runbook: P2 — Elevated DB Latency

### Symptoms
- `/api/health` returns 200 but `db_latency_ms > 200`
- Write operations slow (> 1 s)

### Diagnosis steps

```bash
# Check for long-running queries / locks (SQLite)
sqlite3 ~/dev/petcare-platform/petcare.db ".timeout 5000" "PRAGMA integrity_check;"

# Check audit_events table size (fire-and-forget writes)
sqlite3 ~/dev/petcare-platform/petcare.db "SELECT COUNT(*) FROM audit_events;"

# Disk I/O stats
iostat -x 5 3
```

### Resolution
1. If `audit_events` table very large → run `VACUUM` during off-peak
2. If disk I/O saturated → schedule maintenance window; migrate to dedicated DB

---

## Runbook: P2 — Pharmacy Dispense 403 Storm

### Symptoms
- High rate of `pharmacy.recalled_batch_block` or `pharmacy.safety_override` audit events
- Clinic reporting dispense blocked unexpectedly

### Diagnosis steps

```bash
# Query recent recall events
sqlite3 ~/dev/petcare-platform/petcare.db \
  "SELECT * FROM recall_events ORDER BY issued_at DESC LIMIT 10;"

# Check inventory recall status
sqlite3 ~/dev/petcare-platform/petcare.db \
  "SELECT sfda_batch_number, recall_status FROM inventory_items WHERE recall_status != 'active';"
```

### Resolution
1. Verify recall issuance was intentional (check SFDA portal)
2. If erroneous recall → platform_admin to `PATCH /api/admin/recalls/{id}/resolve`
3. If recall correct → notify pharmacy operators via RECALL_ALERT channel

---

## On-Call Escalation Path

```
L1: On-call engineer (PagerDuty)
  └─ 15 min no ack → L2: Backend tech lead
       └─ 30 min no resolution → L3: Platform director + CTO
```

## Post-Incident Requirements

- P1/P2: Post-mortem within 48 hours (5-whys template)
- P1: Append-only audit of incident timeline to `audit_events` (event_type: `incident.postmortem`)
- All incidents logged in incident tracker with: timeline, impact, root cause, action items

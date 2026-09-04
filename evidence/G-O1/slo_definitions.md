# G-O1 — SLO Definitions

## Service: VetiCare Backend API

### SLO-1: Availability
| Attribute | Value |
|-----------|-------|
| **Target** | 99.5% monthly uptime |
| **Measurement window** | Rolling 30 days |
| **Error budget** | 3.6 hours/month |
| **Indicator** | HTTP 5xx rate < 0.5% of all requests |

### SLO-2: API Latency (p95)
| Endpoint class | Target p95 | Target p99 |
|----------------|-----------|-----------|
| Health check (`/api/health`) | < 100 ms | < 250 ms |
| Read endpoints (GET) | < 300 ms | < 800 ms |
| Write endpoints (POST/PATCH) | < 500 ms | < 1 200 ms |
| Pharmacy dispense (`POST /api/pharmacy/dispense`) | < 800 ms | < 2 000 ms |

### SLO-3: Database Health
| Attribute | Value |
|-----------|-------|
| **Target** | DB latency < 50 ms (p95, measured by `/api/health`) |
| **Degraded threshold** | > 200 ms — triggers PagerDuty P2 |
| **Critical threshold** | Exception / timeout — `/api/health` returns 503, triggers P1 |

### SLO-4: Audit Log Integrity
| Attribute | Value |
|-----------|-------|
| **Target** | 100% of regulated events written to `audit_events` within 500 ms |
| **Regulated event types** | `consultation.signed`, `consent.granted`, `consent.revoked`, `pharmacy.safety_override`, `sfda.recall_issued`, `access.denied` |

---

## Error Budget Policy

| Burn rate | Action |
|-----------|--------|
| > 5% in 1 hour | Automated alert → on-call engineer |
| > 10% in 6 hours | Incident declared, war-room opened |
| > 50% in 72 hours | Change freeze until budget recovers |

---

## SLI Measurement

Health endpoint probed every 30 s by synthetic monitor.  
APM agent (OpenTelemetry-compatible) on every route handler.  
DB latency surfaced directly in `/api/health` response (`db_latency_ms` field).

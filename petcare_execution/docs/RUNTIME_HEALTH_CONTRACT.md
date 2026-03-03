# Runtime Health Contract — PetCare (PH-L6)

**Document ID:** PETCARE-RUNTIME-HEALTH-v1
**Owner:** Platform Ops
**Last Updated (UTC):** 2026-03-03

## Endpoints (minimum)

### 1) GET /health
Purpose: Liveness — process is up and can serve requests.

Response (200):

{
  "status": "ok",
  "service": "petcare",
  "ts_utc": "20260303T000000Z",
  "version": "dev"
}

### 2) GET /ready
Purpose: Readiness — service is ready to accept traffic.

Response (200):

{
  "status": "ready",
  "deps": {
    "db": "unknown",
    "queue": "unknown"
  },
  "ts_utc": "20260303T000000Z"
}

Failure semantics:
- /health non-200 → process unhealthy
- /ready non-200 → dependency not ready

Governance note:
PH-L6 introduces a reference local health server + smoke harness.
Production systems must mirror this contract.

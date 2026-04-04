DF34 — ROLLBACK AND KILL-SWITCH POLICY

PURPOSE

Define the mandatory control rules for rollback and kill-switch governance.

MANDATORY CONTROLS

1. named rollback readiness
2. named kill-switch authority
3. evidence-backed exception detection
4. human escalation path
5. no autonomous remediation
6. no silent continuation after critical control loss

MONITORING STATES

- monitored_live
- exception_detected
- rollback_ready
- blocked
- stale

FAIL-CLOSED ENFORCEMENT

If any mandatory control is missing:
- monitoring_state = blocked
- publication prohibited
- evidence record required

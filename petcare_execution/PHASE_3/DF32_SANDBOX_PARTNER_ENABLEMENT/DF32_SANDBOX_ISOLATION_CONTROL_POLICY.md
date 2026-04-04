DF32 — SANDBOX ISOLATION CONTROL POLICY

PURPOSE

Define the mandatory control boundaries for sandbox partner participation.

MANDATORY CONTROLS

1. isolated sandbox boundary
2. synthetic or approved non-production data only
3. no production credentials
4. no live integration authority
5. no uncontrolled event propagation
6. no hidden dependency creation
7. full audit logging required

SANDBOX STATES

- sandbox_review_ready
- sandbox_enabled
- restricted
- blocked
- stale

FAIL-CLOSED ENFORCEMENT

If any mandatory control is missing:
- sandbox_state = blocked
- publication prohibited
- evidence record required

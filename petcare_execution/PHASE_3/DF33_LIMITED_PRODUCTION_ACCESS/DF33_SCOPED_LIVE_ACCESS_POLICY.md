DF33 — SCOPED LIVE ACCESS POLICY

PURPOSE

Define the mandatory controls for limited production participation.

MANDATORY CONTROLS

1. explicit scope declaration
2. named approval requirement
3. rollback readiness evidenced
4. monitoring active
5. no privilege expansion
6. no hidden dependency creation
7. no uncontrolled data flow

ACCESS STATES

- review_ready
- limited_production_enabled
- restricted
- blocked
- stale

FAIL-CLOSED ENFORCEMENT

If any mandatory control is missing:
- access_state = blocked
- publication prohibited
- evidence record required

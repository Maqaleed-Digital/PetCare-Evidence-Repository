DF35 — CERTIFICATION READINESS POLICY

PURPOSE

Define the control policy for partner certification readiness.

MANDATORY CONTROLS

1. named certification criteria
2. named evidence basis
3. named approval posture
4. no uncited trust classification
5. no automatic certification
6. no implied privilege expansion

CERTIFICATION STATES

- review_ready
- certification_ready
- restricted
- blocked
- stale

FAIL-CLOSED ENFORCEMENT

If any mandatory control is missing:
- certification_state = blocked
- publication prohibited
- evidence record required

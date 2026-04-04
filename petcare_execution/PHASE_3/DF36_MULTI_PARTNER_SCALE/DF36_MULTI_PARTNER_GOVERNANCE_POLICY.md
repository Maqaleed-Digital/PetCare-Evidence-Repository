DF36 — MULTI-PARTNER GOVERNANCE POLICY

PURPOSE

Define the mandatory controls for governed multi-partner scale.

MANDATORY CONTROLS

1. named partner cohort boundaries
2. named isolation posture
3. named approval requirement
4. named evidence coverage
5. no implicit trust propagation
6. no uncontrolled shared dependency
7. no blanket production expansion

SCALE STATES

- scale_review_ready
- staged_scale_enabled
- restricted
- blocked
- stale

FAIL-CLOSED ENFORCEMENT

If any mandatory control is missing:
- scale_state = blocked
- publication prohibited
- evidence record required

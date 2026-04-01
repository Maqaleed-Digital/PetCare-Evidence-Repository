PETCARE EP-14
Sandbox Isolation Model
Status: LOCKED

1. Isolation Objective

The sandbox exists to let partners validate integrations safely.
It must never become a side channel into production.

2. Isolation Dimensions

Credential Isolation
- sandbox credentials separate from production credentials
- sandbox credential rotation independent of production
- sandbox credentials cannot authenticate against production endpoints

Trace Isolation
- sandbox trace IDs use dedicated namespace
- sandbox request IDs cannot collide with production request IDs
- sandbox audit logs remain separately classifiable

Data Isolation
- sandbox uses synthetic or deterministic simulated data only
- no production tenant records exposed
- no production identifiers reused as authoritative references

Webhook Isolation
- sandbox webhook secrets distinct from production secrets
- sandbox event namespace distinct from production event namespace
- sandbox replay targets cannot receive live production events

Routing Isolation
- sandbox gateway resolves to simulation engine only
- no sandbox route may dispatch into production gateway execution path
- no environment override header may bypass sandbox boundary

State Isolation
- sandbox outcomes are informational and test-oriented only
- sandbox writes do not create production internal requests
- sandbox certifications do not imply production execution rights

3. Allowed Sandbox Behaviors

Allowed:
- simulated request acceptance
- deterministic validation errors
- webhook replay testing
- signature validation testing
- onboarding state progression
- certification evidence collection

Forbidden:
- production order creation
- production referral intake
- production payout initiation
- production approval completion
- production inventory mutation
- production clinical workflow mutation

4. Lock Result

Sandbox is locked as a governed test environment only.

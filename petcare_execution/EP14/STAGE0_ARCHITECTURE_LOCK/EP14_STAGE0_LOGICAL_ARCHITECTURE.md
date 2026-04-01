PETCARE EP-14
Logical Architecture
Status: LOCKED

1. High-Level Flow

External Partner
→ Partner Credential Boundary
→ Sandbox Gateway
→ Endpoint Policy Resolver
→ Simulation Engine
→ Webhook Replay Engine
→ Sandbox Audit and Trace Layer
→ Partner Visibility Surfaces

2. Component Responsibilities

Partner Registry
- stores partner identity
- stores status
- stores allowed scopes
- stores sandbox enablement state
- stores certification state

Credential Registry
- stores sandbox API credentials
- stores future production credential references
- supports rotation state
- enforces environment segregation

Sandbox Gateway
- receives sandbox requests only
- validates headers
- validates environment binding
- routes requests to simulation paths only
- blocks production routing

Endpoint Policy Resolver
- maps endpoint family to allowed sandbox behavior
- enforces request-intake-only contract
- enforces partner and tenant scope
- enforces method and header policy

Simulation Engine
- returns deterministic simulated responses
- simulates order request acceptance
- simulates referral request acceptance
- simulates availability update processing
- simulates catalog batch processing
- never mutates production state

Webhook Replay Engine
- emits replayable sandbox events
- signs webhook payloads with sandbox secrets
- validates partner receiver behavior
- logs delivery attempts
- never sends production events

Onboarding State Machine
- manages partner lifecycle
- gates progression by evidence
- records validation checkpoints
- records certification decision

Governance Enforcement Layer
- blocks production execution
- blocks authority escalation
- blocks payment and treasury exposure
- blocks approval bypass
- blocks environment crossing

Sandbox Audit and Trace Layer
- issues sandbox trace IDs
- records sandbox request chain
- records credential use
- records webhook replay history
- records onboarding transitions

3. Environment Boundary

Sandbox Environment:
- isolated credentials
- isolated traces
- isolated webhook secrets
- isolated event namespace
- simulated response only

Production Environment:
- separate credentials
- separate traces
- separate event namespace
- no sandbox-induced execution path

4. Integration Rule

EP-14 integrates with EP-13 only through the already locked contract surface.
EP-14 may exercise contract behavior in sandbox form only.
EP-14 may not expand the endpoint authority surface.

5. Locked Result

The logical architecture is frozen for Stage 0 and may be implemented only within these responsibilities.

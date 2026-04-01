PETCARE EP-14 Stage 2
Deterministic Implementation Specification
Status: LOCKED
Source of Truth Baseline: 3cde8b8fd3499ab8313a2b7c192ac1a9a646b695

1. Objective

Implement deterministic scaffolding for the EP-14 Partner Operating Layer and Sandbox Environment using only the locked Stage 0 and Stage 1 architecture, contracts, and model semantics.

2. Stage 2 Scope

Delivered in this stage:
- partner registry scaffold
- credential registry scaffold
- sandbox gateway scaffold
- simulation engine scaffold
- webhook replay scaffold
- onboarding state machine scaffold
- governance assertion script
- sample outputs and evidence artifacts

Not delivered in this stage:
- production runtime activation
- production credential issuance
- production routing
- payment or treasury exposure
- approval completion
- live external network listeners
- production data access
- non-simulated sandbox mutation

3. Core Rule

All sandbox writes must remain simulated request-intake-only.
No scaffold may create a production internal request.
No scaffold may dispatch into production runtime.

4. Deterministic Components

Partner Registry Scaffold:
- records partner lifecycle state
- records allowed scopes
- records sandbox enablement
- records certification state

Credential Registry Scaffold:
- records credential environment binding
- records status lifecycle
- enforces sandbox versus production reference separation

Sandbox Gateway Scaffold:
- validates required headers
- validates environment binding
- resolves sandbox endpoint family behavior
- routes only to simulation engine
- blocks production dispatch

Simulation Engine Scaffold:
- returns deterministic outcomes for locked endpoint families
- generates sandbox trace identifiers
- simulates accepted or rejected request-intake outcomes only

Webhook Replay Scaffold:
- builds sandbox-only webhook envelopes
- signs with sandbox-only HMAC
- records replay delivery attempts
- blocks production event replay

Onboarding State Machine Scaffold:
- enforces locked lifecycle transitions
- blocks unauthorized activation
- requires certification before active

5. Governance Continuity

The following must remain true:
- sandbox_endpoint_behavior_families_locked = 9
- all_sandbox_writes_are_simulated_request_intake_only = true
- sandbox_to_production_execution_path_allowed = false
- production_data_access_from_sandbox_allowed = false
- production_events_replayable_from_sandbox = false
- certification_required_before_active = true
- external_execution_authority_transferred = false
- payment_execution_exposed = false
- approval_bypass_exposed = false
- treasury_bypass_exposed = false

6. Stage 2 Result

This stage produces deterministic governed implementation scaffolding only.
Execution authority remains internal to PetCare and outside sandbox operation.

PETCARE EP-13 Stage 2
Deterministic Implementation Specification
Status: LOCKED
Source of Truth Baseline: 5b9d6ea

1. Objective

Implement governed Stage 2 scaffolding for EP-13 using the Stage 1 locked contract only.

This implementation creates deterministic framework-neutral assets for:
- endpoint family registration
- auth and scope enforcement mapping
- integration gateway routing
- request-intake-only controlled write handling
- webhook signing and delivery scaffolding
- audit and trace chain generation
- contract assertions that prevent governance drift

2. Stage 2 Scope

Delivered in this stage:
- endpoint family registry covering the locked EP-13 surface
- scope matrix aligned to read and controlled write boundaries
- integration gateway scaffold with endpoint family resolution
- request validation and governance routing model
- webhook envelope and signing scaffold
- audit and trace linkage scaffold
- deterministic assertion script to verify invariants

Not delivered in this stage:
- production runtime wiring
- live authentication provider integration
- persistent storage adapters
- network listeners
- SDK generation
- partner portal UI
- external execution authority
- payment or treasury mutation capability

3. Architectural Rule

All controlled write requests must be converted into governed internal requests before any downstream processing.

External write path:
- authenticate
- authorize
- validate schema
- resolve endpoint family
- enforce request-intake-only boundary
- create internal request envelope
- emit audit and trace artifacts
- return accepted response

No direct execution path is permitted.

4. Locked Endpoint Families

The Stage 2 registry must lock these 13 endpoint families only:

1. partner_profile
2. orders_collection
3. orders_item
4. referrals_collection
5. referrals_item
6. availability
7. catalog_batches_collection
8. catalog_batches_item
9. webhook_subscriptions_collection
10. webhook_subscription_pause
11. webhook_subscription_resume
12. webhook_subscription_item
13. events_item

5. Read vs Controlled Write Boundary

Read families:
- partner_profile
- orders_collection GET
- orders_item GET
- referrals_collection GET
- referrals_item GET
- catalog_batches_item GET
- webhook_subscriptions_collection GET
- events_item GET

Controlled write families:
- orders_collection POST
- referrals_collection POST
- availability PUT
- catalog_batches_collection POST
- webhook_subscriptions_collection POST
- webhook_subscription_pause POST
- webhook_subscription_resume POST
- webhook_subscription_item DELETE

Controlled write invariant:
Every write family must declare mutation_mode = REQUEST_INTAKE_ONLY.

6. Governance Invariants Preserved

Required invariants:
- external_execution_authority_transferred = false
- payment_execution_exposed = false
- approval_bypass_exposed = false
- treasury_bypass_exposed = false
- ai_mediated_external_execution = false
- hidden_mutation_paths = false
- all_controlled_writes_are_internal_requests_only = true
- tenant_isolation_required = true
- partner_scope_required = true
- traceability_required = true

7. Files Produced

- petcare_execution/EP13/STAGE2_IMPLEMENTATION/EP13_STAGE2_IMPLEMENTATION_SPEC.md
- petcare_execution/EP13/STAGE2_IMPLEMENTATION/endpoint_family_registry.json
- petcare_execution/EP13/STAGE2_IMPLEMENTATION/auth_scope_matrix.json
- petcare_execution/EP13/STAGE2_IMPLEMENTATION/integration_gateway_scaffold.py
- petcare_execution/EP13/STAGE2_IMPLEMENTATION/webhook_delivery_scaffold.py
- petcare_execution/EP13/STAGE2_IMPLEMENTATION/audit_trace_scaffold.py
- petcare_execution/EP13/STAGE2_IMPLEMENTATION/contract_assert.py
- petcare_execution/EP13/STAGE2_IMPLEMENTATION/EP13_STAGE2_NOTION_UPDATE.md
- petcare_execution/EP13/STAGE2_IMPLEMENTATION/EP13_STAGE2_EMERGENT_PROMPT.md

8. Deterministic Validation

The contract assertion script must confirm:
- exactly 13 endpoint families exist
- no forbidden capability is exposed
- every controlled write family is request-intake-only
- all required scopes exist
- every family has tenant and partner scoping
- webhook event types remain within the locked set

9. Stage 2 Result

This stage produces deterministic governed implementation scaffolding only.
Execution authority remains internal to PetCare.
No partner receives execution or approval authority.

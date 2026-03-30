# NEXT_SCOPE_EXECUTION_SPEC

## Next Epic
EP-07 B2B Marketplace Integration

## Next Build Entry
PETCARE-PHASE-1-BUILD-EP07-WAVE-01

## Wave Objective
Establish the governed partner onboarding registry and verification state model.

## WAVE-01 Scope
- partner entity model
- partner type classification
- partner verification state machine
- required registration fields
- registry persistence
- deterministic query surfaces for onboarding and verification status
- audit-ready partner onboarding output

## WAVE-01 Non-Goals
- no pricing engine
- no settlement execution
- no payment flow
- no autonomous partner activation
- no scorecard calculation yet

## WAVE-01 Candidate Files
- "petcare_runtime/src/petcare/partner_network/models.py"
- "petcare_runtime/src/petcare/partner_network/service.py"
- "petcare_runtime/src/petcare/partner_network/repository.py"
- "petcare_runtime/src/petcare/partner_network/query.py"
- "petcare_runtime/src/petcare/api/routes_ep07_wave01.py"
- "petcare_runtime/tests/test_partner_onboarding_registry.py"
- "petcare_runtime/migrations/0019_ep07_wave_01_partner_registry.sql"

## Required Behaviors
- deterministic partner registration
- explicit verification states
- explicit activation eligibility
- tenant-aware partner ownership
- auditable transitions
- safe query surfaces for verified and unverified partners

## Proposed Verification States
- draft
- submitted
- under_review
- verified
- rejected
- suspended

## Proposed Partner Types
- clinic
- pharmacy
- diagnostics
- logistics
- emergency_provider
- marketplace_service

## Proposed Wave Sequence After WAVE-01
- WAVE-02 → SLA and contract governance
- WAVE-03 → catalog ingestion and normalization
- WAVE-04 → governed pricing rules
- WAVE-05 → settlement and reconciliation baseline
- WAVE-06 → scorecards and disputes
- CLOSURE → cross-wave integrity closure

## Acceptance Criteria For WAVE-01
- partner registry persists deterministic records
- verification transitions are validated and test-covered
- verified state is explicit and queryable
- activation eligibility is derived, not assumed
- tests pass
- no EP-01 through EP-06 behavior changes

PetCare — PETCARE-AI-FND-3
Agent Runtime Integration Specification

Status
Implementation-ready integration artifact

Purpose
Integrate the completed agent orchestrator with the surrounding PetCare AI runtime contracts:
- prompt layer composition
- governance runtime binding
- model gateway binding
- deterministic synthetic request and response verification

Architecture Alignment
This pack implements the integration path:
Assistive AI UI Components
→ Agent Orchestration Layer
→ AI Governance Runtime
→ Context Assembly + Policy Enforcement
→ Domain Runtime Services
→ Model Gateway
→ Logging, Monitoring, Evaluation

Scope
In scope:
- prompt composition from orchestrator output
- governance runtime adapter contract
- model gateway adapter contract
- deterministic synthetic request fixtures
- deterministic integration test pack
- evidence pack generation

Out of scope:
- autonomous diagnosis
- autonomous prescriptions
- autonomous treatment authorization
- autonomous consultation closure
- external network calls
- modifications to validated PH runtimes
- modifications to governance scripts
- modifications to closure scripts

Integration Units
1. prompt_composer.ts
Builds a final prompt package from orchestrator payload:
- system policy layer
- role layer
- context layer
- task layer

2. governance_runtime_adapter.ts
Defines a deterministic governance binding contract that:
- records prompt and output metadata
- enforces approval requirements
- captures override capability markers
- returns stable governance decisions

3. model_gateway_adapter.ts
Defines a deterministic model gateway binding contract that:
- accepts the composed prompt package
- returns a stable synthetic response envelope
- does not call any external provider in this pack

4. synthetic_requests.ts
Provides canonical fixtures for each approved task family:
- summarize_history
- draft_consult_note
- medication_safety_review
- emergency_intake_support
- operations_forecast
- client_followup_draft

5. integration_test_pack.ts
Runs all synthetic requests through:
- AgentRuntimeController
- PromptComposer
- GovernanceRuntimeAdapter
- ModelGatewayAdapter

Required Outcomes
- blocked requests remain blocked
- allowed requests produce a composed prompt package
- governance binding returns review requirements deterministically
- model gateway returns synthetic response envelopes deterministically
- all outputs remain assistive only

Determinism Rules
- no randomness
- no timestamps in decision logic
- no hidden I/O
- no state mutation outside the function scope
- same input must produce same output shape and same deterministic fields

Protected Zones
Do not modify:
- consent semantics
- RBAC semantics
- audit taxonomy
- clinical sign-off immutability
- escalation referral semantics

Stop Condition
If this pack requires any protected-zone semantic change:
- do not proceed with semantic mutation
- write STOP_REPORT.md
- explain the exact required change and why

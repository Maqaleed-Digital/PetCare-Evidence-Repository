PetCare — PETCARE-AI-FND-2
Agent Orchestrator Implementation Specification

Status
Implementation-ready execution artifact

Purpose
Implement the governed agent orchestration layer defined by the PetCare agentic AI architecture.
This layer must:
- route requests to specialized assistive agents
- assemble safe context
- enforce policy before any model call
- preserve veterinarian and pharmacist human authority
- remain detached from autonomous clinical action

Scope Boundary
In scope:
- agent runtime controller
- agent router
- context assembler
- policy enforcer
- deterministic implementation artifacts
- evidence pack generation for this execution pack

Out of scope:
- autonomous diagnosis
- autonomous prescription
- autonomous treatment authorization
- autonomous consultation closure
- mutation of validated PH clinical runtimes
- modification of governance scripts
- modification of closure scripts

Authoritative Architecture Mapping
Flow:
Assistive AI UI Components
→ Agent Orchestration Layer
→ AI Governance Runtime
→ Context Assembly + Policy Enforcement
→ Domain Runtime Services
→ Model Gateway
→ Logging, Monitoring, Evaluation

Implementation Units
1. types.ts
Shared contracts for requests, context, routing, policy decisions, and orchestration results.

2. agent_router.ts
Maps a task type to one of:
- clinical_copilot
- pharmacy_safety
- emergency_triage
- operations_intelligence
- client_communication

3. context_assembler.ts
Builds a safe, redacted, deterministic context envelope from provided request inputs.
No external fetches are performed in this pack.
This pack defines assembly contract only.

4. policy_enforcer.ts
Applies assistive-only and role-aware guardrails before orchestration proceeds.

5. agent_runtime_controller.ts
Coordinates:
- route selection
- context assembly
- policy enforcement
- model payload assembly
- deterministic orchestration output

Guardrails
The orchestrator must block requests that attempt to:
- sign medical records
- prescribe medication
- finalize triage decisions
- close consultations autonomously

Approved Task Families
- summarize_history
- draft_consult_note
- medication_safety_review
- emergency_intake_support
- operations_forecast
- client_followup_draft

Routing Matrix
summarize_history -> clinical_copilot
draft_consult_note -> clinical_copilot
medication_safety_review -> pharmacy_safety
emergency_intake_support -> emergency_triage
operations_forecast -> operations_intelligence
client_followup_draft -> client_communication

Determinism Rules
- no randomness
- no current-time logic inside orchestrator decisions
- no hidden network fetches
- no mutation of source clinical state
- output shape must be stable for the same input

Evidence Requirements
This pack must produce:
- file listing
- deterministic manifest with sha256
- implementation run log
- pushed commit hash as source of truth

Stop Condition
Stop only if implementation requires changing:
- consent semantics
- RBAC semantics
- audit taxonomy
- clinical sign-off immutability
- escalation referral semantics

If any protected-zone change is required, do not proceed with semantic mutation.
Create STOP_REPORT.md instead.

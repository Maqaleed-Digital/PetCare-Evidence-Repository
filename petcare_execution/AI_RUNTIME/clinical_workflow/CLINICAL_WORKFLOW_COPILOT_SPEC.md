PetCare — PETCARE-AI-INT-3
Clinical Workflow Copilot Integration

Status
Implementation-ready governed workflow integration artifact

Purpose
Integrate assistive clinical agents into governed workflow adapters for:
- consultation workflow
- triage board workflow
- pharmacy review workflow
- emergency workflow

Architecture Alignment
This pack connects workflow adapters to the governed AI runtime:
Workflow Surface
→ Assistive Workflow Adapter
→ Agent Orchestrator
→ Governance Runtime
→ Context Assembly
→ Domain Runtime Services
→ Model Gateway

Scope
In scope:
- consultation copilot integration adapter
- triage board integration adapter
- pharmacy review integration adapter
- emergency workflow integration adapter
- workflow validation pack
- Python validation runner
- evidence generation

Out of scope:
- autonomous diagnosis
- autonomous prescriptions
- autonomous treatment authorization
- autonomous consultation closure
- external network calls
- changes to validated PH runtimes
- changes to governance scripts
- changes to closure scripts

Safety Guarantees
- all workflow outputs remain assistive only
- human approval remains mandatory for clinical decisions
- no write authority is granted by these adapters
- adapters only prepare governed workflow payloads and hints

Required Outcomes
- workflow adapters are explicit and deterministic
- validation succeeds without repo-local node package dependency
- all outputs remain assistive only
- workflow integration preserves read/write boundary discipline

Determinism Rules
- no randomness
- no current-time logic in governance decisions
- no hidden I/O
- no mutation of validated PH runtimes
- same input must produce same output shape

Protected Zones
Do not modify:
- consent semantics
- RBAC semantics
- audit taxonomy
- clinical sign-off immutability
- escalation referral semantics

Stop Condition
If this pack requires protected-zone semantic mutation:
- do not proceed with semantic change
- write STOP_REPORT.md
- explain exact required change and why

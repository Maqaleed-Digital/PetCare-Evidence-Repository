# AI Production Activation Specification
## Pack: PETCARE-AI-OPS-1

### Overview
This specification governs the production activation of the PetCare AI Runtime. All AI agents operate in assistive-only mode. No autonomous clinical decisions are permitted.

### Activation Model
- **Activation Scope**: Pilot cohort only (AI_PILOT_ALPHA)
- **Kill Switch**: GLOBAL_AI_KILL_SWITCH provides instant runtime halt
- **Cohort Control**: PILOT_COHORT_REGISTRY gates clinic eligibility
- **Assistive Boundary**: All AI outputs are advisory; human approval mandatory for all clinical decisions

### Governance Constraints
- Diagnosis: FORBIDDEN (assistive suggestion only)
- Prescription: FORBIDDEN (assistive suggestion only)
- Treatment Authorization: FORBIDDEN (human approval required)
- Consultation Closure: FORBIDDEN (clinician must close)
- Triage Finalization: FORBIDDEN (review_required state only)

### Activation Prerequisites
1. All FND packs (FND-1 through FND-8) validated and committed
2. All INT packs (INT-1 through INT-8) validated and committed
3. Kill switch in ACTIVE state (runtime enabled)
4. Pilot cohort registry populated with approved clinics
5. Human approval gate verified operational

### Production Controls
- `ai_runtime_kill_switch.ts`: Global kill switch with isAIRuntimeAllowed()
- `runtime_activation_registry.ts`: Per-clinic activation state
- `pilot_cohort_governance.ts`: Cohort eligibility and governance rules
- `pilot_release_evidence_export.ts`: Evidence bundle for release audit

### Protected Zones (Never Modified)
- Consent semantics
- RBAC semantics
- Audit taxonomy
- Clinical sign-off immutability
- Escalation referral semantics

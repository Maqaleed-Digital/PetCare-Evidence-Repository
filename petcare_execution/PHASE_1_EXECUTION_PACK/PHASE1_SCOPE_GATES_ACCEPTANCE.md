# PETCARE PHASE 1 SCOPE, GATES, AND ACCEPTANCE

Pack ID: PETCARE-PHASE-1-EXECUTION-PACK

## 1. Authoritative references used

- PetCare BRD v1.1
- PetCare AI-Native Technical Architecture v1.0
- PetCare Vendor and SI Enablement Pack v1.0
- PetCare Notion Execution Mapping Pack v1.0
- PetCare Agentic AI Layer Technical Architecture
- PetCare Agentic AI Feature Layer BRD
- PetCare Emergent-Heavy Execution Strategy
- Governed Adoption Blueprint

## 2. Execution sequence

1. EP-01 Identity, Access, Consent Baseline
2. EP-02 UPHR Core
3. EP-03 Tele-Vet MVP
4. EP-04 Pharmacy MVP
5. EP-05 AI Controlled Activation
6. EP-06 Security, Audit, Evidence, Ops Baseline

## 3. Epic-level acceptance

### EP-01 Identity, Access, Consent Baseline
Must deliver:
- Role matrix finalized for PHASE 1 actors
- RBAC enforcement boundary defined
- Consent capture and revoke baseline defined
- Purpose limitation baseline defined
- Audit events defined for identity and consent actions

Hard gates:
- G-S1
- G-R1

Acceptance:
- Roles enumerated and least-privilege aligned
- Unauthorized access path defined and testable
- Consent grant and revoke path defined
- Purpose-restricted access path defined
- Audit events explicitly listed

### EP-02 UPHR Core
Must deliver:
- Structured pet health schema
- Timeline and versioning model
- Audit-linked CRUD baseline
- Secure attachment rules
- AI redaction boundary for prompt-safe use

Hard gates:
- G-C1
- G-S1
- G-A1

Acceptance:
- Allergies, meds, vaccines, labs, notes included
- Timeline supports filter and search requirements
- Clinical data changes auditable
- Document access is access-controlled
- Prompt redaction requirements defined

### EP-03 Tele-Vet MVP
Must deliver:
- Booking lifecycle
- Consultation workflow
- Session notes model
- Immutable sign-off rule
- Red-flag escalation logic
- Emergency referral packet baseline

Hard gates:
- G-C1

Acceptance:
- Booking state model defined
- Consultation notes require vet sign-off
- Post-sign notes are immutable
- Red flags force escalation path
- Referral packet includes summary, allergies, meds, consent check

### EP-04 Pharmacy MVP
Must deliver:
- Rx lifecycle states
- Review and approval path
- Safety warning model
- Block-rule model
- Dose guardrail coverage baseline
- Fulfillment status lifecycle

Hard gates:
- G-C1
- G-R1
- G-O1

Acceptance:
- Rx states are explicit
- Allergy, contraindication, and interaction warnings covered
- Overrides are logged
- Dose guardrails account for species, weight, age baseline
- Fulfillment status model is defined

### EP-05 AI Controlled Activation
Must deliver:
- AI intake MVP definition
- Vet copilot note drafting definition
- Prompt/output logging model
- Override workflow
- Human approval enforcement boundary
- Assistive-only AI rule preserved

Hard gates:
- G-A1
- G-C1

Acceptance:
- AI output classes are defined
- AI never signs, prescribes, or finalizes decisions
- Logging includes role, case id, model version, timestamps
- Override reason codes exist
- Vet approval required where mandated

### EP-06 Security, Audit, Evidence, Ops Baseline
Must deliver:
- Security baseline checklist
- Audit verification baseline
- Initial observability expectations
- Evidence attachment rules for hard-gated work
- Release-readiness dependency list for later phases

Hard gates:
- G-S1
- G-O1

Acceptance:
- Security checklist is attached to phase scope
- Audit samples are expected outputs
- Evidence links are required before done status
- Ops readiness dependencies are listed

## 4. Protected zones

The following semantics are protected:
- Consent scopes
- RBAC role semantics
- Audit event taxonomy semantics
- Clinical sign-off immutability semantics
- Escalation rule semantics

No executor may change these without STOP_REPORT.md and approval.

## 5. Implementation readiness output expected after this pack

The next implementation run should create:
- Deterministic repo backlog slice for EP-01 through EP-02 first
- Service boundaries for UPHR
- API contract baseline
- Data model baseline
- UI route and component slice baseline
- Tests and evidence requirements per hard-gated story

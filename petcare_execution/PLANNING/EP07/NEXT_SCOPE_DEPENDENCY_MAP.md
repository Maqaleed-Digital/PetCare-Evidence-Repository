# NEXT_SCOPE_DEPENDENCY_MAP

## Epic
EP-07 B2B Marketplace Integration

## Dependency Baseline
This map identifies the minimum already-governed capabilities that EP-07 must reuse without semantic mutation.

## Dependency Set

### D-01 Identity and RBAC
Source epic:
EP-01

Required for:
- partner admin roles
- platform admin roles
- access restrictions by tenant and partner
- least-privilege enforcement for onboarding and catalog actions

Dependency expectation:
EP-07 must consume existing role and enforcement semantics without redefining protected role behavior.

### D-02 Consent and Audit
Source epic:
EP-01 and EP-02

Required for:
- partner data access boundaries
- audit records for onboarding, verification, pricing, and settlement events
- evidence-ready partner lifecycle traceability

Dependency expectation:
EP-07 must emit auditable partner lifecycle events and preserve consent and purpose-limitation boundaries where records are involved.

### D-03 UPHR and Clinical Context
Source epic:
EP-02

Required for:
- future partner referrals and partner-facing data packaging
- traceability of external handoff contexts
- structured pet and care data compatibility

Dependency expectation:
EP-07 planning must preserve the system-of-record model and avoid cross-domain data duplication.

### D-04 Tele-Vet Workflow and Escalation Semantics
Source epic:
EP-03

Required for:
- downstream partner handoff support
- referral continuity
- operator-governed case transition readiness

Dependency expectation:
EP-07 must not override escalation or clinical sign-off behaviors.

### D-05 Pharmacy Lifecycle Controls
Source epic:
EP-04

Required for:
- catalog compatibility
- partner medication and service mapping
- downstream fulfillment and recall alignment

Dependency expectation:
EP-07 pricing and partner catalog behavior must remain compatible with medication safety and operational routing rules.

### D-06 AI Governance Boundary
Source epic:
EP-05

Required for:
- explainable partner recommendations in future waves
- assistive-only AI boundaries
- logging and override compatibility

Dependency expectation:
EP-07 must not introduce autonomous decisioning.

### D-07 Emergency Network
Source epic:
EP-06

Required for:
- emergency clinic network continuity
- partner availability and SLA alignment
- future marketplace-driven partner routing expansion

Dependency expectation:
EP-07 partner models must remain compatible with governed emergency partner constructs already sealed.

## EP-07 Internal Capability Dependencies

### I-01 Partner Registry Foundation
Must exist before:
- verification workflow
- SLA attachment
- catalog ingestion
- settlement identity mapping

### I-02 Verification State Model
Must exist before:
- transaction eligibility
- partner activation
- service publication
- scorecard participation

### I-03 SLA Contract Model
Must exist before:
- breach event emission
- partner performance measurement
- scorecards
- governed service availability commitments

### I-04 Catalog Model
Must exist before:
- pricing rules
- settlement logic
- partner offer publication

### I-05 Pricing Model
Must exist before:
- governed offer calculation
- reconciliation
- partner statement preparation

### I-06 Settlement Baseline
Must exist before:
- statement issuance
- dispute workflows
- scorecards tied to commercial outcomes

## Dependency Conclusion
EP-07 should begin with registry and verification, then contract and SLA, then catalog, then pricing, then settlement, then scorecards and disputes.

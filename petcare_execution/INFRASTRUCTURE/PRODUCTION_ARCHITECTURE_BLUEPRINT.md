PETCARE-PRODUCTION-INFRASTRUCTURE-DEPLOYMENT
PRODUCTION_ARCHITECTURE_BLUEPRINT

Status
Authoritative baseline for production infrastructure activation.

Source Baseline
- State: portfolio_governance_complete
- Prior pack: PETCARE-PORTFOLIO-GOVERNANCE-COMPLETE
- Prior evidence: petcare_execution/EVIDENCE/PETCARE-PORTFOLIO-GOVERNANCE-COMPLETE/20260316T063858Z

Objective
Activate the governed production infrastructure baseline required to operate PetCare in a real KSA production environment while preserving sovereignty, auditability, regulatory alignment, and assistive-only AI boundaries.

Target State
petcare_production_environment_ready

Infrastructure Scope
1. Production cloud landing zone
2. Network topology and segmentation
3. Application runtime topology
4. Transactional database topology
5. Object storage topology
6. Edge and API gateway controls
7. Secrets and key management
8. Observability and incident readiness
9. CI/CD deployment controls
10. Evidence and release validation

Architecture Principles
- KSA data residency by default
- Immutable auditability
- Human-in-the-loop for clinical and regulated actions
- Zero-trust access model
- Least privilege access control
- Environment separation across dev, test, prod
- Deterministic releases with evidence packs
- AI governance preserved end to end

Production Component Baseline
A. Edge and Access
- Public DNS entry
- WAF
- TLS termination
- API gateway
- tenant and partner header enforcement
- request throttling and rate limiting

B. Runtime Layer
- web application runtime
- API application runtime
- worker runtime for async tasks
- workflow runtime for governed operational flows

C. Data Layer
- PostgreSQL primary datastore
- read replica optional for scale
- object storage for documents, media, exports
- backup storage and retention policy
- encrypted audit/event storage

D. Observability Layer
- centralized logs
- metrics collection
- tracing
- alert routing
- SLO dashboards
- incident runbook references

E. Security Layer
- secrets manager
- KMS-backed key management
- role-scoped runtime identities
- restricted network paths
- encryption in transit and at rest

F. Delivery Layer
- CI test gate
- security gate
- release packaging
- deployment validation
- rollback path
- evidence pack generation

Environment Policy
Development
- synthetic or masked data only
- no production secrets
- relaxed scale, strict governance parity

Test
- integration-safe environment
- release candidate validation
- production-like topology where practical

Production
- KSA-resident only
- locked secrets flow
- audited deploy path
- break-glass access controlled and logged

Hard Gate Mapping
G-S1 Security Gate
- network segregation
- secrets management
- runtime identity boundaries
- encryption coverage
- validation checklist

G-R1 Regulatory and Privacy Gate
- KSA residency flag
- storage locality declaration
- audit retention boundary
- consent-sensitive data handling preserved

G-A1 AI Governance Gate
- prompt and output logging path preserved
- AI runtime secrets segregated
- model routing keys isolated
- approval and override evidence preserved

G-O1 Operational Readiness Gate
- metrics, logs, traces, alerts
- deployment validation
- rollback procedure
- incident response ownership

Deployment Model Decision
Recommended baseline:
- single governed production environment
- modular monolith runtime
- managed PostgreSQL
- managed object storage
- gateway and WAF at edge
- observability stack enabled from day one
- CI/CD with pre-deploy and post-deploy validation

Out of Scope for this Pack
- app feature delivery
- schema redesign
- vendor-specific infrastructure code
- production secrets values
- actual live deployment credentials
- protected clinical workflow semantics changes

Acceptance Criteria
- all infrastructure baseline files created
- deployment and validation scripts created
- manifest generation automated
- evidence directory generated deterministically
- git working tree committed and pushed

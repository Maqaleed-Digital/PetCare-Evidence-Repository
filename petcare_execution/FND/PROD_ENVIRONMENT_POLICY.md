PetCare PH42-A
Production Environment Isolation Policy
Status: Canonical for PH42-A (Environment Separation)
Owner: Waheeb
Scope: Dev, Test/Staging, Production
Purpose: Enforce strict environment isolation for regulated production readiness

1. Objectives

This policy defines mandatory isolation rules between environments to ensure:
- KSA data residency intent is not violated by non-production workflows
- Production secrets are never exposed to non-production systems
- Production PHI/PII is never used in dev/test
- AI logs are isolated by environment with environment-specific retention and access controls
- Release governance supports regulator-grade audit readiness

2. Environment Definitions

Environment: DEV
- Purpose: Developer iteration, scaffolding, local validation
- Data: Synthetic only
- Secrets: Local dev secrets only; never shared with test/prod
- AI Logs: Ephemeral; no PHI/PII; shortest retention

Environment: TEST (or STAGING)
- Purpose: Pre-prod integration testing, QA, controlled demos
- Data: Masked or synthetic only; never production snapshots containing PHI/PII
- Secrets: Test secrets only; never shared with dev/prod
- AI Logs: Limited retention; no PHI/PII; access restricted

Environment: PROD
- Purpose: Live clinical production candidate runtime
- Data: Live PHI/PII subject to PDPL and clinical governance requirements
- Secrets: Production-only; stored and accessed via production secret store
- AI Logs: Production-only store with enforced access control and defined retention
- Audit: Append-only audit requirements apply

3. Non-Negotiable Rules

R-01 Secret Non-Reuse
- No secret value may be reused across DEV/TEST/PROD
- No shared API keys, tokens, credentials, signing keys, or encryption keys
- Production secrets must not be readable by CI jobs running for non-production branches

R-02 Production Data Prohibition in Non-Prod
- DEV and TEST must never contain production PHI/PII
- Any dataset used outside PROD must be synthetic or masked, with written provenance

R-03 Environment Labeling
All runtime logs, AI logs, and audit events must carry:
- environment: dev | test | prod
- tenant_id
- actor_role (if applicable)
- timestamp_utc
This enables separation, filtering, exportability, and audit defensibility.

R-04 Network and Access Separation
- Production databases and storage endpoints must not be reachable from DEV/TEST networks
- Admin access must be least privilege and logged
- No direct DB access for engineers in PROD unless emergency procedure is invoked

R-05 Build and Release Separation
- DEV builds may not deploy to PROD
- PROD deployment requires controlled release workflow and explicit approvals
- Artifact provenance must be maintained (build id, commit id, evidence references)

4. Production Secret Store Requirements

Production secret store must support:
- Per-environment namespaces
- Rotation capabilities
- Access logging
- Least privilege access policies

Minimum rotation requirement:
- 90-day rotation for PROD credentials and signing keys
- Immediate emergency rotation for suspected compromise

5. AI Log Isolation Requirements

AI logs must be environment-separated:
- Separate storage location per environment
- Separate access control policy per environment
- Separate retention rules per environment
- Explicit redaction policy enforced before any AI prompt leaves regulated boundary

Production AI logs must support:
- Exportability for audit review
- Stable schema including environment, model_version, tenant_id, actor role, timestamp
- Immutable or tamper-evident storage model (defined in PH42-B)

6. Evidence Requirements (PH42-A)

PH42-A closure pack must snapshot:
- This policy file
- Environment isolation matrix
- Secret rotation SOP
- AI environment log isolation policy
- Environment negative test cases
- Guard check script
- PH42-A closure pack script

7. Out of Scope (PH42-A)

- Changing POLICY.md or REGISTRY.json
- Implementing runtime secret stores
- Implementing immutable audit ledger (PH42-B)
- Implementing PDPL runtime enforcement (PH42-C)

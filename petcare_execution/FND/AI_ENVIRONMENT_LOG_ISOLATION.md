PetCare PH42-A
AI Environment Log Isolation Policy
Status: Canonical for PH42-A (AI Governance Separation)

1. Objective

Ensure AI prompts, outputs, and evaluations are isolated by environment to prevent:
- Production PHI/PII leakage into non-production systems
- Cross-environment contamination of evaluations and monitoring
- Unauthorized access to sensitive logs

2. Required Log Fields (Minimum Schema)

All AI log records must carry:
- environment: dev | test | prod
- timestamp_utc
- tenant_id
- actor_role (owner | vet | pharmacy | partner | admin | system)
- model_provider
- model_version
- operation_type (intake | summarize | suggest | classify | other)
- input_redacted: true | false
- output_redacted: true | false
- request_id (trace correlation)

3. Storage Separation

DEV
- storage: dev-only
- retention: minimal
- data: no PHI/PII; redaction enforced

TEST
- storage: test-only
- retention: limited
- data: no PHI/PII; redaction enforced

PROD
- storage: prod-only, residency-compliant
- retention: defined by governance policy
- data: PHI/PII allowed only as required and under policy
- access: least privilege; audited access
- export: audit export supported

4. Access Control

- No engineer should browse PROD AI logs by default
- Access must be gated and logged
- Any access to PROD AI logs must be justifiable and time-bound

5. Evaluation Isolation

- Evaluation datasets must never be sourced from production PHI/PII without explicit approvals and masking
- Baseline tests for dev/test must be synthetic

6. Evidence (PH42-A)

This policy is documented and included in PH42-A closure pack snapshots.
Runtime enforcement will be validated in later phases.

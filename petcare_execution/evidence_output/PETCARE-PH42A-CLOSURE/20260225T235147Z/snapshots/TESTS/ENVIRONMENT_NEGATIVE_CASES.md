PetCare PH42-A
Environment Isolation Negative Cases
Status: Governance-negative tests (documentation-driven)

Purpose
Define negative cases that must fail in a compliant system, proving isolation rules are enforced.

A. Secrets and Configuration

NEG-ENV-01
Scenario: A production secret is present in repository tracked files.
Expected: Guard check fails; CI must fail.

NEG-ENV-02
Scenario: A .env file is tracked by git containing any secret values.
Expected: Guard check fails; CI must fail.

NEG-ENV-03
Scenario: A CI workflow references PROD_SECRET for a non-deploy job.
Expected: Guard check flags workflow; CI must fail.

B. Data Separation

NEG-ENV-04
Scenario: Non-production database contains records labeled environment=prod.
Expected: Data migration/seed pipelines must reject; validation fails.

NEG-ENV-05
Scenario: Dev or test environment uses a production database endpoint.
Expected: Connection must be blocked by network/policy; guard checks must flag config.

C. AI Logs

NEG-ENV-06
Scenario: AI logs in dev/test contain environment=prod.
Expected: Validation fails; logs must be isolated.

NEG-ENV-07
Scenario: AI prompt logs in dev/test contain unredacted PHI/PII markers.
Expected: Redaction policy must reject or redact; validation fails.

D. Artifact Governance

NEG-ENV-08
Scenario: evidence_output artifacts are tracked in git.
Expected: Guard check fails; CI must fail.

NEG-ENV-09
Scenario: Production-only configuration files are committed without explicit sanitization.
Expected: Guard check fails unless whitelisted example file; CI must fail.

E. Access Control (Policy-Level)

NEG-ENV-10
Scenario: Engineer role has default access to prod logs or prod database.
Expected: Access must be denied unless emergency procedure invoked; audit record required.

Notes
These are governance-negative cases for PH42-A. Runtime enforcement test automation will be expanded in later phases.

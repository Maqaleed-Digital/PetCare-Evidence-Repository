PetCare PH42-A
Environment Isolation Matrix
Status: Canonical for PH42-A (Operational Separation Summary)

1. Matrix

Category: Data
- DEV: Synthetic only
- TEST: Masked or synthetic only
- PROD: Live PHI/PII

Category: Secrets
- DEV: Local dev secrets only; never shared
- TEST: Test-only secrets; isolated namespace
- PROD: Production-only secrets; isolated namespace; rotation required

Category: Network Access
- DEV: Local or dev network only
- TEST: Staging network only
- PROD: Production network only; not reachable from dev/test networks

Category: Storage
- DEV: Local or dev storage
- TEST: Staging storage; no PHI/PII
- PROD: Residency-compliant production storage; PHI/PII permitted with controls

Category: AI Logging
- DEV: Ephemeral; shortest retention
- TEST: Limited retention; restricted access
- PROD: Production-only store; defined retention; exportable for audit

Category: Audit
- DEV: Standard logs acceptable
- TEST: Standard logs acceptable
- PROD: Append-only requirements apply (PH42-B)

Category: CI Access
- DEV: CI may access dev/test secrets if required for tests
- TEST: CI may access test secrets only
- PROD: CI must not access prod secrets for untrusted branches; deployment workflow only

Category: Personnel Access
- DEV: Engineers allowed
- TEST: Engineers and QA allowed
- PROD: Least-privilege; licensed roles; emergency access procedure required

2. Mandatory Assertions (to be checked by scripts)

A-01 No committed secrets in repository
A-02 No .env or env files tracked (unless explicitly sanitized examples)
A-03 No evidence_output artifacts tracked (must be ignored)
A-04 No references to production secrets in CI workflows for non-deploy jobs
A-05 Environment labeling present in policy artifacts (document-level in PH42-A; runtime-level in later phases)

3. Notes

This matrix is a governance control. Enforcement scaffolding begins in PH42-A and becomes runtime-enforced in later phases.

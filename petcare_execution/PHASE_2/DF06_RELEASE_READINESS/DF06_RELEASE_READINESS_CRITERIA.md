PETCARE DF06
Release Readiness Criteria

Decision States
READY
BLOCKED
EXCEPTION_REVIEW_REQUIRED

Release is READY only if every item below is PASS

1. Source Integrity
Production candidate must come from pushed main
Artifact digest must be recorded
No dirty working tree
No local-only artifact allowed

2. Build and Test Integrity
Required CI pipeline status PASS
Application test suites PASS
Dependency lock state present and unchanged for release candidate
Container image or deployment artifact immutable and referenced by digest

3. Runtime Readiness
Nonprod deployment verified on the intended release candidate
Health and readiness checks PASS
No unresolved Sev1 or Sev2 incident tied to the release candidate

4. Security and Access Readiness
Prod service accounts separated from nonprod
Prod secrets separated from nonprod
Least-privilege IAM reviewed
No public exposure unless explicitly approved in writing

5. Operational Readiness
Monitoring baseline configured
Alert routing configured
Named on-call owner identified
Rollback path identified and verified

6. Governance Readiness
Named release authority approval present
Named deploy authority approval present
Evidence pack checklist complete
Change record created

7. Data and Change Safety
No destructive migration without explicit rollback procedure
Backward compatibility reviewed for app and configuration changes
Manual checkpoint required before first prod exposure

Blocked Conditions
Any CI failure
Any missing artifact digest
Any missing approval
Any unresolved critical incident
Any undefined rollback path
Any missing alert route
Any production secret or identity shared with nonprod
Any request to expose prod publicly without explicit approval

DF06 Output Rule
If any item is not PASS, production promotion remains BLOCKED.

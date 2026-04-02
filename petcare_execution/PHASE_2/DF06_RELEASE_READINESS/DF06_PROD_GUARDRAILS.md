PETCARE DF06
Production Deployment Guardrails

Guardrails
1. No direct production deployment from local workstation
2. No deployment to prod without explicit approval record
3. No public unauthenticated prod exposure unless explicitly approved
4. Prod runtime identity must be prod-only
5. Prod secrets must be prod-only
6. Prod environment variables must be versioned through controlled release flow
7. No sandbox or nonprod credential reuse
8. No destructive schema change without rollback plan
9. No release when monitoring or alerting is unavailable
10. No release during unresolved critical incident
11. No mutable latest-tag deployment; artifact digest only
12. No hidden hotfix outside the evidence and approval path

Mandatory Controls to Implement After Design Approval
Manual approval gate before prod deploy
Artifact digest pinning
Prod-only deployment service account
Prod-only secret bindings
Prod post-deploy verification step
Recorded rollback target
Release evidence output

Explicit Block Rules
If any guardrail cannot be enforced, prod activation remains blocked.

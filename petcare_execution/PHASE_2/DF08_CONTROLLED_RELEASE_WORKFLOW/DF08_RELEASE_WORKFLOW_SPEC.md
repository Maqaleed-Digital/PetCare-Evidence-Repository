PETCARE DF08
Release Workflow Specification

Sequence (MANDATORY)

STEP 1 — Release Gate Check
→ petcare_df07_release_gate_check.sh

STEP 2 — Post-Deploy Verification (Nonprod only)
→ petcare_df07_post_deploy_verify.sh

STEP 3 — Evidence Pack Generation
→ petcare_df07_evidence_pack.sh

Rules

- Execution must stop on first failure
- No step skipping allowed
- Evidence must always be produced
- Workflow is reusable and deterministic

Blocked Conditions

- Missing environment variables
- Invalid artifact digest
- Health/readiness failure
- Evidence generation failure

Governance Result

Workflow simulates full release lifecycle
WITHOUT activating production

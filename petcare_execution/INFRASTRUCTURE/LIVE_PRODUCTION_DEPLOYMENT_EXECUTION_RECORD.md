PETCARE-LIVE-PRODUCTION-DEPLOYMENT-AND-VERIFICATION
LIVE_PRODUCTION_DEPLOYMENT_EXECUTION_RECORD

Purpose
Create the governed live production deployment execution record for PetCare.

State Transition
- Current: petcare_production_environment_ready
- Target: petcare_live_production_verified

Execution Record Fields
- release version
- source commit hash
- deployment environment
- deployment date and time UTC
- deploy operator
- release approver
- change window identifier
- linked evidence directory
- linked rollback runbook reference
- linked go-live gate reference
- deployment outcome
- post-deploy verification outcome

Required Rules
- source commit hash must be recorded exactly
- deploy operator and approver must be named
- linked evidence path is mandatory
- no live deployment is considered complete until post-deploy verification is attached
- any failed critical check must trigger rollback decision capture

Deployment Outcome States
- pending
- in_progress
- completed
- completed_with_followup
- rolled_back
- failed

Completion Rule
The live deployment execution record is complete only when:
- deployment outcome is captured
- post-deploy verification outcome is captured
- evidence path is attached
- final source-of-truth commit is recorded

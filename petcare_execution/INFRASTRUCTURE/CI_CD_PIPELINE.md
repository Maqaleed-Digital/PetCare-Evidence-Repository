PETCARE-PRODUCTION-INFRASTRUCTURE-DEPLOYMENT
CI_CD_PIPELINE

Purpose
Define the governed production delivery pipeline.

Pipeline Stages
1. Source integrity
- correct branch and baseline verification
- clean working tree before run

2. Build and test
- unit/integration checks as applicable
- deterministic script execution
- manifest builder execution

3. Security checks
- secret scan
- config sanity check
- validation script pre-check

4. Release packaging
- file listing
- manifest generation
- evidence directory generation

5. Deployment approval
- named approval required before production deploy
- evidence linked to deployment request

6. Post-deploy validation
- deployment validation script
- runtime health confirmation
- rollback decision gate if failed

7. Closeout
- evidence retained
- commit hash recorded
- release note reference attached

Release Constraints
- no direct production change outside governed pipeline
- no release without evidence output
- no release without validation pass
- no self-approval on protected environments

Rollback Requirement
A rollback path must exist for:
- app runtime failure
- failed migration or incompatible release
- broken config deployment
- secrets/config misbinding

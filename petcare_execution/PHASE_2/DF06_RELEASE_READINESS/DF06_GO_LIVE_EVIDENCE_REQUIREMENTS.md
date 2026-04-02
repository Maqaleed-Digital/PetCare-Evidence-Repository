PETCARE DF06
Go-Live Evidence Requirements

Purpose
Define the minimum evidence set required before production activation is approved.

Required Evidence Set
1. Source commit hash
2. Artifact digest
3. CI or validation proof
4. Nonprod verification proof
5. Release approval record
6. Deploy authority record
7. Post-deploy verification proof
8. Rollback target reference
9. Monitoring and alert routing proof
10. Access model confirmation
11. Change log or release note
12. Final go-live decision record

Recommended Evidence Pack Structure
git_head.txt
artifact_digest.txt
validation_summary.txt
release_approval.txt
deploy_operator.txt
post_deploy_checks.txt
rollback_target.txt
monitoring_baseline.txt
access_model_confirmation.txt
MANIFEST.json
MANIFEST.sha256

Gate Mapping
Operational readiness evidence required
Security evidence required
Regulatory and privacy controls preserved
AI and clinical governance constraints remain unchanged

Blocking Rule
If the evidence pack is incomplete, production activation remains blocked.

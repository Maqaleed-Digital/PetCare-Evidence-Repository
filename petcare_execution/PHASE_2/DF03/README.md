PETCARE-PHASE-2-DF03-DEPLOYMENT-PIPELINE

Status:
AUTHORITATIVE EXECUTION PACK

Source-of-truth baseline:
0aad6fecdc7e32368e2f2ca5075e908650531afc

Objective:
Enable governed deployment capability on the already-activated GCP foundation.

Outcomes:
- Artifact Registry immutability enforced
- Cloud Build nonprod CI trigger established
- Production deployment path remains controlled and human-triggered
- Environment-scoped deploy identities enforced
- Secret Manager runtime injection model established
- Deployment evidence pack generated

Governance invariants:
- sandbox_to_production_execution_path_allowed=false
- production_data_access_from_sandbox_allowed=false
- production_events_replayable_from_sandbox=false
- no_shared_credentials_across_environments=true
- no_shared_vpc_across_environments=true
- certification_required_before_active=true
- secrets_embedded_in_images=false
- direct_production_deploy_allowed=false
- artifacts_mutable_after_build=false

Required operator inputs:
- PRJ_PROD
- PRJ_NONPROD
- PRJ_SANDBOX
- REGION_PRIMARY
- ARTIFACT_REPO
- SERVICE_NAME_NONPROD
- SERVICE_NAME_PROD
- BUILD_SA_NAME
- DEPLOY_NONPROD_SA_NAME
- DEPLOY_PROD_SA_NAME
- GITHUB repo linkage
- runtime secret values or pre-created secrets

Trigger model:
- nonprod trigger: automatic on main branch
- prod deployment: manual controlled promotion using immutable image digest or controlled release tag process

Evidence output:
petcare_execution/EVIDENCE/PETCARE-PHASE-2-DF03-DEPLOYMENT-PIPELINE/<UTC_TIMESTAMP>/

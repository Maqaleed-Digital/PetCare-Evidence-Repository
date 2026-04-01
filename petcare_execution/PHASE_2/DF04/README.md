PETCARE-PHASE-2-DF04-REAL-NONPROD-APPLICATION-BUILD-AND-DEPLOYMENT-CONTRACT-ALIGNMENT

Status:
AUTHORITATIVE EXECUTION PACK

Baseline:
Uses current local HEAD at execution time as the continuity baseline when the prior pushed commit hash is not explicitly provided in-session.

Objective:
Replace the DF03B smoke-only nonprod trigger behavior with a real backend application build-and-deploy contract for the connected GitHub repository Maqaleed-Digital/PetCare-Platform.

Contract decision:
- deployment target in this phase is petcare-api-nonprod
- source path in connected repo is backend/
- deployment method is Cloud Run source deployment
- runtime config remains injected from Secret Manager
- prod path remains unchanged in this phase

Why this contract is no-guessing:
- the connected repo visibly contains a backend directory
- this phase aligns only the backend application contract
- no frontend release contract is assumed here
- buildpacks/runtime detection are delegated to Cloud Run source deployment

Governance invariants:
- sandbox_to_production_execution_path_allowed=false
- production_data_access_from_sandbox_allowed=false
- production_events_replayable_from_sandbox=false
- no_shared_credentials_across_environments=true
- no_shared_vpc_across_environments=true
- direct_production_deploy_allowed=false
- secrets_embedded_in_images=false
- prod_trigger_unchanged_in_df04=true

Evidence output:
petcare_execution/EVIDENCE/PETCARE-PHASE-2-DF04-REAL-NONPROD-APPLICATION-BUILD-AND-DEPLOYMENT-CONTRACT-ALIGNMENT/<UTC_TIMESTAMP>/

PETCARE-PHASE-2-DF03B-BUILD-CONFIG-REPO-ALIGNMENT-AND-FIRST-NONPROD-PIPELINE-EXECUTION

Status:
AUTHORITATIVE EXECUTION PACK

Source-of-truth baseline:
f26ff20979357803a846e80c6ad18704342802b5

Objective:
Resolve the Cloud Build config path mismatch by updating triggers to inline config mode, then execute the first controlled nonprod pipeline smoke run through the trigger.

Why this pack exists:
DF03A proved trigger creation and secret/version governance. The remaining blocker was that the connected GitHub repo does not contain the referenced build config file path.

DF03B approach:
- move nonprod trigger to inline config
- move prod trigger to inline config
- preserve prod approval gate
- execute first nonprod trigger smoke run using a deterministic no-guessing build
- avoid assumptions about Dockerfile or app build structure inside the connected repo

Outcomes:
- nonprod trigger inline config active
- prod trigger inline config active
- first controlled nonprod pipeline smoke run initiated
- evidence pack generated

Governance invariants:
- sandbox_to_production_execution_path_allowed=false
- production_data_access_from_sandbox_allowed=false
- production_events_replayable_from_sandbox=false
- no_shared_credentials_across_environments=true
- no_shared_vpc_across_environments=true
- direct_production_deploy_allowed=false
- artifacts_mutable_after_build=false
- prod_trigger_requires_approval=true
- no_app_release_without_explicit_build_contract=true

Evidence output:
petcare_execution/EVIDENCE/PETCARE-PHASE-2-DF03B-BUILD-CONFIG-REPO-ALIGNMENT-AND-FIRST-NONPROD-PIPELINE-EXECUTION/<UTC_TIMESTAMP>/

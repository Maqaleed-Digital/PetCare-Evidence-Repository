PETCARE-PHASE-2-DF03A-TRIGGER-ACTIVATION-AND-FIRST-CONTROLLED-NONPROD-DEPLOYMENT

Status:
AUTHORITATIVE EXECUTION PACK

Source-of-truth baseline:
a1d9cf4da8b75224b2473c0928beb571ca7ac069

Objective:
Complete the remaining DF-03 operator-dependent steps by activating Cloud Build triggers, replacing placeholder runtime secrets with real values, and initiating the first controlled nonprod deployment through the trigger path.

Outcomes:
- nonprod GitHub trigger active
- prod approval-gated GitHub trigger active
- nonprod runtime secret replaced with real version
- prod runtime secret replaced with real version
- first controlled nonprod trigger run initiated
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
- secrets_embedded_in_images=false

Accepted trigger modes:
- 2nd gen repository resource:
  projects/PROJECT/locations/REGION/connections/CONNECTION/repositories/REPOSITORY
- 1st gen GitHub repository:
  repo owner + repo name

Evidence output:
petcare_execution/EVIDENCE/PETCARE-PHASE-2-DF03A-TRIGGER-ACTIVATION-AND-FIRST-CONTROLLED-NONPROD-DEPLOYMENT/<UTC_TIMESTAMP>/

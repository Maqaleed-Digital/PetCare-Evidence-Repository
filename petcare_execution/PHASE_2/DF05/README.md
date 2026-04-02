PETCARE-PHASE-2-DF05-NONPROD-RUNTIME-VERIFICATION-AND-ACCESS-MODEL-CONFIRMATION

Status:
AUTHORITATIVE EXECUTION PACK

Source-of-truth baseline:
51c0eaf

Objective:
Verify the real nonprod runtime behavior of petcare-api-nonprod after DF04, and confirm the actual access model under current org policy.

Scope:
- control-plane verification
- revision and URL capture
- service account capture
- runtime secret wiring verification
- Cloud Run IAM policy inspection
- unauthenticated request test
- authenticated request test with identity token
- optional best-effort /health and /ready probes
- evidence generation

Governance invariants:
- sandbox_to_production_execution_path_allowed=false
- production_data_access_from_sandbox_allowed=false
- production_events_replayable_from_sandbox=false
- no_shared_credentials_across_environments=true
- no_shared_vpc_across_environments=true
- direct_production_deploy_allowed=false
- df05_is_read_only_runtime_verification=true

Interpretation rules:
- if unauthenticated root request returns 200-399, public access is effectively enabled
- if unauthenticated root request returns 401 or 403, public access is effectively restricted
- authenticated root request success proves authenticated runtime reachability
- /health and /ready are optional best-effort probes only

Evidence output:
petcare_execution/EVIDENCE/PETCARE-PHASE-2-DF05-NONPROD-RUNTIME-VERIFICATION-AND-ACCESS-MODEL-CONFIRMATION/<UTC_TIMESTAMP>/

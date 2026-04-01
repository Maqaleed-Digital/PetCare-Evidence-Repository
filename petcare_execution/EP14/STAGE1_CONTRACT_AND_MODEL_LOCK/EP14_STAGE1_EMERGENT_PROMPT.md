PETCARE EP-14 Stage 1
Emergent Contract and Model Lock Prompt

Repository:
"/Users/waheebmahmoud/dev/petcare-evidence-repository"

Authoritative source-of-truth commit before Stage 1:
"eb7aaaa370b89bd76871c801bd1c1f49c352887a"

Objective:
Create the EP-14 Stage 1 contract and model lock pack for Partner Operating Layer and Sandbox Environment.

Required outputs:
1. "petcare_execution/EP14/STAGE1_CONTRACT_AND_MODEL_LOCK/EP14_STAGE1_CONTRACT_SPEC.md"
2. "petcare_execution/EP14/STAGE1_CONTRACT_AND_MODEL_LOCK/partner_model_registry.json"
3. "petcare_execution/EP14/STAGE1_CONTRACT_AND_MODEL_LOCK/credential_contract_registry.json"
4. "petcare_execution/EP14/STAGE1_CONTRACT_AND_MODEL_LOCK/sandbox_endpoint_behavior_matrix.json"
5. "petcare_execution/EP14/STAGE1_CONTRACT_AND_MODEL_LOCK/onboarding_transition_contract.json"
6. "petcare_execution/EP14/STAGE1_CONTRACT_AND_MODEL_LOCK/webhook_replay_contract.json"
7. "petcare_execution/EP14/STAGE1_CONTRACT_AND_MODEL_LOCK/ep14_stage1_assert.py"
8. "petcare_execution/EP14/STAGE1_CONTRACT_AND_MODEL_LOCK/EP14_STAGE1_NOTION_UPDATE.md"
9. "petcare_execution/EP14/STAGE1_CONTRACT_AND_MODEL_LOCK/EP14_STAGE1_EMERGENT_PROMPT.md"

Evidence output root:
"petcare_execution/EVIDENCE/PETCARE-PHASE-1-BUILD-EP14-STAGE1-CONTRACT-AND-MODEL-LOCK/<UTC_RUN>/"

Rules:
- full files only
- overwrite-safe writes only
- commit and push once
- preserve EP-13 and EP-14 Stage 0 governance invariants
- preserve request-intake-only model
- sandbox must remain isolated from production
- no authority expansion
- no hidden mutation paths

Stage 1 must lock:
- partner model
- credential model
- sandbox endpoint behavior
- onboarding transitions
- webhook replay contract
- governance assertion rules

Stop condition:
Stop only if contract design introduces production risk or governance drift.
If that occurs, emit STOP_REPORT.md and stop.

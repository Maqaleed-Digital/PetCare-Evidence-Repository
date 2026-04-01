PETCARE EP-14 Stage 2
Emergent Deterministic Implementation Prompt

Repository:
"/Users/waheebmahmoud/dev/petcare-evidence-repository"

Authoritative source-of-truth commit before Stage 2:
"3cde8b8fd3499ab8313a2b7c192ac1a9a646b695"

Objective:
Create the EP-14 Stage 2 deterministic implementation pack for Partner Operating Layer and Sandbox Environment.

Required outputs:
1. "petcare_execution/EP14/STAGE2_DETERMINISTIC_IMPLEMENTATION/EP14_STAGE2_IMPLEMENTATION_SPEC.md"
2. "petcare_execution/EP14/STAGE2_DETERMINISTIC_IMPLEMENTATION/partner_registry_scaffold.py"
3. "petcare_execution/EP14/STAGE2_DETERMINISTIC_IMPLEMENTATION/credential_registry_scaffold.py"
4. "petcare_execution/EP14/STAGE2_DETERMINISTIC_IMPLEMENTATION/sandbox_gateway_scaffold.py"
5. "petcare_execution/EP14/STAGE2_DETERMINISTIC_IMPLEMENTATION/simulation_engine_scaffold.py"
6. "petcare_execution/EP14/STAGE2_DETERMINISTIC_IMPLEMENTATION/webhook_replay_scaffold.py"
7. "petcare_execution/EP14/STAGE2_DETERMINISTIC_IMPLEMENTATION/onboarding_state_machine_scaffold.py"
8. "petcare_execution/EP14/STAGE2_DETERMINISTIC_IMPLEMENTATION/ep14_stage2_assert.py"
9. "petcare_execution/EP14/STAGE2_DETERMINISTIC_IMPLEMENTATION/EP14_STAGE2_NOTION_UPDATE.md"
10. "petcare_execution/EP14/STAGE2_DETERMINISTIC_IMPLEMENTATION/EP14_STAGE2_EMERGENT_PROMPT.md"

Evidence output root:
"petcare_execution/EVIDENCE/PETCARE-PHASE-1-BUILD-EP14-STAGE2-DETERMINISTIC-IMPLEMENTATION/<UTC_RUN>/"

Rules:
- full files only
- overwrite-safe writes only
- commit and push once
- preserve EP-13 and EP-14 Stage 0 and Stage 1 governance invariants
- preserve request-intake-only model
- sandbox must remain isolated from production
- no authority expansion
- no hidden mutation paths

Stage 2 must implement:
- partner registry scaffold
- credential registry scaffold
- sandbox gateway scaffold
- simulation engine scaffold
- webhook replay scaffold
- onboarding state machine scaffold
- governance assertion rules

Stop condition:
Stop only if implementation introduces production risk or governance drift.
If that occurs, emit STOP_REPORT.md and stop.

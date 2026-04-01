EP-13 Stage 2 — Emergent Execution Prompt

Repository root:
"/Users/waheebmahmoud/dev/petcare-evidence-repository"

Authoritative source-of-truth commit before this work:
"5b9d6ea"

Objective:
Create the EP-13 Stage 2 deterministic implementation scaffolding pack from the locked Stage 1 contract only.

Required outputs:
1. "petcare_execution/EP13/STAGE2_IMPLEMENTATION/EP13_STAGE2_IMPLEMENTATION_SPEC.md"
2. "petcare_execution/EP13/STAGE2_IMPLEMENTATION/endpoint_family_registry.json"
3. "petcare_execution/EP13/STAGE2_IMPLEMENTATION/auth_scope_matrix.json"
4. "petcare_execution/EP13/STAGE2_IMPLEMENTATION/integration_gateway_scaffold.py"
5. "petcare_execution/EP13/STAGE2_IMPLEMENTATION/webhook_delivery_scaffold.py"
6. "petcare_execution/EP13/STAGE2_IMPLEMENTATION/audit_trace_scaffold.py"
7. "petcare_execution/EP13/STAGE2_IMPLEMENTATION/contract_assert.py"
8. "petcare_execution/EP13/STAGE2_IMPLEMENTATION/EP13_STAGE2_NOTION_UPDATE.md"
9. "petcare_execution/EP13/STAGE2_IMPLEMENTATION/EP13_STAGE2_EMERGENT_PROMPT.md"

Evidence output root:
"petcare_execution/EVIDENCE/PETCARE-PHASE-1-BUILD-EP13-STAGE2-DETERMINISTIC-IMPLEMENTATION/<UTC_RUN>/"

Non-negotiable rules:
- Do not change Stage 1 contract semantics
- Do not expand endpoint surface beyond 13 endpoint families
- Do not introduce payment execution
- Do not introduce approval bypass
- Do not introduce treasury mutation
- Do not introduce hidden mutation paths
- All controlled writes must remain request-intake-only
- Full files only
- Overwrite-safe writes only
- Deterministic manifest required
- Commit and push once complete

Stage 2 must lock:
- endpoint family registry
- scope matrix
- request-intake-only mutation mode
- integration gateway routing scaffold
- webhook signing scaffold
- audit and trace scaffold
- contract assertion pass

Required validation:
- exactly 13 endpoint families
- all controlled writes request-intake-only
- forbidden capabilities absent
- partner and tenant scope required for all families
- required scopes present
- webhook event set remains locked

Stop condition:
Stop only if protected governance semantics must change.
If stop condition is triggered, write STOP_REPORT.md explaining the exact semantic conflict and stop.

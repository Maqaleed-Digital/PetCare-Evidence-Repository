# PETCARE — EP-11 HARD GATES

Status: LOCKED

## G-F16 Execution Authorization Gate
Requirements:
- explicit human authorization required before payment execution
- authorizer identity and timestamp required
- approval reason or policy basis recorded

## G-F17 Treasury Sufficiency Gate
Requirements:
- available balance or funding sufficiency verified before dispatch
- execution blocked on insufficiency
- insufficiency outcome logged

## G-F18 Dual Control Enforcement
Requirements:
- configured execution classes require second approval where policy applies
- both approvals attributable and timestamped
- no silent bypass

## G-F19 Execution Reversibility Gate
Requirements:
- pause, cancel, retry, and failure paths explicitly defined
- irreversible steps clearly marked
- failure handling and recovery evidence recorded

## G-F20 Payment Rail Safety Gate
Requirements:
- connector contracts explicitly defined
- rail dispatch isolated behind governed interface
- no callback may autonomously finalize settlement or bypass review
- execution outcomes must return to PetCare audit trail

## Phase 0 Pass Conditions
- architecture lock document created
- hard gates created
- dependency map created
- execution spec created
- Notion map created
- evidence pack generated
- manifest generated

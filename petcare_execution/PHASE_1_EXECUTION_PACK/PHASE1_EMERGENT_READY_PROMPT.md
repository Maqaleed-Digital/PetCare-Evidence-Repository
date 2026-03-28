# EMERGENT READY PROMPT — PETCARE PHASE 1

Continue PetCare execution from the current pushed source-of-truth commit.

Repository:
"/Users/waheebmahmoud/dev/petcare-evidence-repository"

Execution root:
"/Users/waheebmahmoud/dev/petcare-evidence-repository/petcare_execution"

New pack to honor:
PETCARE-PHASE-1-EXECUTION-PACK

Authoritative files:
- "petcare_execution/PHASE_1_EXECUTION_PACK/PHASE1_EXECUTION_MASTER_PLAN.md"
- "petcare_execution/PHASE_1_EXECUTION_PACK/PHASE1_SCOPE_GATES_ACCEPTANCE.md"
- "petcare_execution/PHASE_1_EXECUTION_PACK/PHASE1_BACKLOG.csv"

Objective:
Proceed to the next governed implementation-ready pack for PHASE 1, starting with:
EP-01 Identity, Access, Consent Baseline
EP-02 UPHR Core

Execution contract:
- no guessing
- PetCare standalone only
- full file delivery only
- overwrite-safe writes only
- explicit file paths
- preserve protected-zone semantics
- evidence-first outputs
- stop only if protected-zone semantics must change

Protected zones:
- consent scopes and enforcement meaning
- RBAC role semantics
- audit event taxonomy semantics
- clinical sign-off immutability rule
- escalation rule meaning

Do not:
- introduce new domains
- rename locked domains
- add phase-2 capability into phase-1 scope
- weaken HITL controls
- weaken auditability
- invent cross-project dependencies

Target output for next pack:
- PHASE 1 implementation baseline for EP-01 and EP-02
- deterministic artifact tree
- data model baseline
- API contract baseline
- UI surface mapping baseline
- tests and evidence expectations
- manifest with SHA-256
- commit and push

Stop condition:
If any protected-zone semantic change is required, produce STOP_REPORT.md and stop.

Return:
- created files
- validations run
- evidence path
- pushed commit hash

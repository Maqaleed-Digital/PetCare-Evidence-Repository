# EMERGENT READY PROMPT — PETCARE EP-01 EP-02 NEXT BUILD WAVE

Continue PetCare execution from the pushed source-of-truth commit produced by the implementation baseline pack.

Repository:
"/Users/waheebmahmoud/dev/petcare-evidence-repository"

Authoritative baseline files:
- "petcare_execution/PHASE_1_IMPLEMENTATION_BASELINE_EP01_EP02/EP01_RBAC_ROLE_MATRIX.md"
- "petcare_execution/PHASE_1_IMPLEMENTATION_BASELINE_EP01_EP02/EP01_CONSENT_SCOPE_MODEL.md"
- "petcare_execution/PHASE_1_IMPLEMENTATION_BASELINE_EP01_EP02/EP01_AUDIT_EVENT_TAXONOMY.md"
- "petcare_execution/PHASE_1_IMPLEMENTATION_BASELINE_EP01_EP02/EP02_UPHR_DATA_MODEL_BASELINE.md"
- "petcare_execution/PHASE_1_IMPLEMENTATION_BASELINE_EP01_EP02/EP02_API_CONTRACT_BASELINE.yaml"
- "petcare_execution/PHASE_1_IMPLEMENTATION_BASELINE_EP01_EP02/EP02_UI_SURFACE_MAPPING.md"
- "petcare_execution/PHASE_1_IMPLEMENTATION_BASELINE_EP01_EP02/EP01_EP02_EVIDENCE_AND_GATE_MAP.md"

Objective:
Execute the next repo-native build wave for:
- EP-01 Identity Access Consent Baseline
- EP-02 UPHR Core

Required outputs:
- concrete schema files and migrations
- initial API route implementation
- access control middleware baseline
- consent service baseline
- audit emission baseline
- UPHR entity service baseline
- tests
- evidence outputs
- commit and push

Rules:
- no guessing
- PetCare standalone only
- do not change protected-zone semantics
- full files only
- overwrite-safe writes only
- explicit file paths
- deterministic evidence outputs

Stop only if protected-zone semantics must change.
If triggered, produce STOP_REPORT.md and stop.

Return:
- created files
- validations run
- evidence path
- pushed commit hash

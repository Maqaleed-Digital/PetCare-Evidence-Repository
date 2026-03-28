# EMERGENT READY PROMPT — PETCARE NEXT BUILD WAVE AFTER EP01 EP02 WAVE 02

Continue PetCare execution from the pushed source-of-truth commit produced by PETCARE-PHASE-1-BUILD-WAVE-EP01-EP02-WAVE-02.

Repository:
"/Users/waheebmahmoud/dev/petcare-evidence-repository"

Current implementation focus:
- remaining EP-01 and EP-02 hardening
- richer UPHR persistence and read behavior
- stronger consent-resource enforcement
- timeline filtering and search
- document validation and policy
- AI prompt-redaction baseline
- deeper tests
- evidence outputs

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

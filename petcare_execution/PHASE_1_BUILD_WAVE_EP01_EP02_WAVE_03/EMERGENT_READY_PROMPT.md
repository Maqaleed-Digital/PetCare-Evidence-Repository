# EMERGENT READY PROMPT — PETCARE NEXT BUILD WAVE AFTER EP01 EP02 WAVE 03

Continue PetCare execution from the pushed source-of-truth commit produced by PETCARE-PHASE-1-BUILD-WAVE-EP01-EP02-WAVE-03.

Repository:
"/Users/waheebmahmoud/dev/petcare-evidence-repository"

Current implementation focus:
- richer consent-to-document linkage
- document upload policy enforcement at route level
- timeline ordering and pagination baseline
- explicit audit samples and evidence pack enrichment
- prompt-safe structured summary generation
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

# EMERGENT READY PROMPT — PETCARE NEXT BUILD WAVE AFTER EP01 EP02 WAVE 04

Continue PetCare execution from the pushed source-of-truth commit produced by PETCARE-PHASE-1-BUILD-WAVE-EP01-EP02-WAVE-04.

Repository:
"/Users/waheebmahmoud/dev/petcare-evidence-repository"

Current implementation focus:
- structured prompt-safe summary generation (JSON schema output)
- consent scope audit trail enrichment
- timeline ordering by recorded_at / administered_at
- expanded document access patterns (pharmacy operator, emergency packet)
- deeper evidence samples and evidence pack enrichment

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

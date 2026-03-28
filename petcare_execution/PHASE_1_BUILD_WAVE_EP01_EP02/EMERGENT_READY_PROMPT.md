# EMERGENT READY PROMPT — PETCARE NEXT BUILD WAVE AFTER EP01 EP02 BUILD WAVE 01

Continue PetCare execution from the pushed source-of-truth commit produced by PETCARE-PHASE-1-BUILD-WAVE-EP01-EP02.

Repository:
"/Users/waheebmahmoud/dev/petcare-evidence-repository"

Current implementation files:
- "petcare_runtime/src/petcare/auth/access_control.py"
- "petcare_runtime/src/petcare/consent/consent_service.py"
- "petcare_runtime/src/petcare/audit/audit_service.py"
- "petcare_runtime/src/petcare/uphr/models.py"
- "petcare_runtime/src/petcare/uphr/service.py"
- "petcare_runtime/src/petcare/api/routes_ep01_ep02.py"
- "petcare_runtime/migrations/0001_ep01_ep02_baseline.sql"
- "petcare_runtime/tests/test_ep01_ep02_baseline.py"

Objective:
Deepen the EP-01 and EP-02 implementation by adding:
- remaining UPHR entities from the locked baseline
- framework integration wiring
- stronger persistence patterns
- expanded access-control coverage
- expanded tests
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

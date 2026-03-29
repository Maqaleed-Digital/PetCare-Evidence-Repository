Pack: PETCARE-PHASE-1-BUILD-EP04-WAVE-03
Status: Committed

Objective:
- extend EP-04 with additive medication safety rule scaffolding
- add deterministic dose context and dose-band foundation
- add advisory-only DOSE_MATRIX_GUARDRAIL warning
- add advisory-only CONTRAINDICATION_CONTEXT warning
- add pharmacist review read/list boundary
- add pharmacist review decision audit boundary without execution expansion

Outcome:
- pharmacy/rules.py with 8 exported symbols
- PHARMACY_REVIEW_AUDIT_EVENTS (3) + PHARMACY_REVIEW_DECISIONS (3) contracts locked
- 21 total tests passing (7 Wave-01 + 6 Wave-02 + 8 Wave-03)

Constraints enforced:
- no guessing
- minimum files only
- no protected-zone semantic changes
- closed EP-01 / EP-02 / EP-03 baselines preserved
- no blocking logic
- no AI autonomy
- deterministic evidence output

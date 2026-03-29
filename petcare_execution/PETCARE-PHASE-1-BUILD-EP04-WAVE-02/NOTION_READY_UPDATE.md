Pack: PETCARE-PHASE-1-BUILD-EP04-WAVE-02
Status: Committed

Objective:
- extend advisory safety screening with dose guardrail and contraindication checks
- add deterministic read model accessor and sorted list helper
- preserve all Wave-01 pharmacy lifecycle behaviour and tests

Outcome:
- extend_safety_warnings(), get_prescription_read_model(), list_prescriptions() added
- DOSE_GUARDRAIL and CONTRAINDICATION warning types operational (advisory only, non-blocking)
- 13 tests passing (7 Wave-01 + 6 Wave-02)

Constraints enforced:
- no guessing
- minimum files only
- no protected-zone semantic changes
- closed EP-01 / EP-02 / EP-03 baselines preserved
- deterministic evidence output

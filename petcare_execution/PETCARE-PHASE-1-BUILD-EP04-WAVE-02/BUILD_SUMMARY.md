PACK_ID: PETCARE-PHASE-1-BUILD-EP04-WAVE-02

Completed:
- extend_safety_warnings(): dose guardrail (DOSE_GUARDRAIL) + contraindication (CONTRAINDICATION) advisory checks added to pharmacy/service.py
- get_prescription_read_model(): deterministic read model accessor
- list_prescriptions(): sorted read model list by created_at / prescription_id
- Wave-01 implementation preserved intact; all 7 Wave-01 tests continue to pass
- 6 new Wave-02 tests added and passing

No protected-zone semantics modified.
No EP-01 / EP-02 / EP-03 baselines reopened.

Validation:
13 passed / 0 failed (7 Wave-01 + 6 Wave-02)

Protected-zone semantics: unchanged

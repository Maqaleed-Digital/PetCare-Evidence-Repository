PACK_ID: PETCARE-PHASE-1-BUILD-EP04-WAVE-03

Completed:
- pharmacy/rules.py created: medication safety rule engine foundation
- DoseContext frozen dataclass + deterministic dose-band scaffolding (JUVENILE_LIGHT / ADULT_LIGHT / STANDARD / LARGE)
- evaluate_medication_safety_rules(): advisory-only DOSE_MATRIX_GUARDRAIL + CONTRAINDICATION_CONTEXT warnings
- apply_wave03_safety_rules(): additive merge onto existing Prescription.safety_warnings
- get_pharmacy_review_read_model(): deterministic review-focused read model
- list_reviewable_prescriptions(): AUTHORIZED + SUBMITTED filter, deterministic sort
- record_pharmacy_review_decision(): ROLE_PHARMACY gate + audit event capture (no state mutation)
- PHARMACY_REVIEW_AUDIT_EVENTS: 3 events
- PHARMACY_REVIEW_DECISIONS: 3 decisions
- __init__.py updated to export all Wave-03 symbols
- 8 Wave-03 tests added and passing
- Wave-01 (7) + Wave-02 (6) + Wave-03 (8) all passing

No protected-zone semantics modified.
No EP-01 / EP-02 / EP-03 baselines reopened.
No blocking logic introduced.
No AI autonomy introduced.

Validation:
21 passed / 0 failed (7 Wave-01 + 6 Wave-02 + 8 Wave-03)

Protected-zone semantics: unchanged

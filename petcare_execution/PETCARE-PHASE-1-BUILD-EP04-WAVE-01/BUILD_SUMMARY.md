PACK_ID: PETCARE-PHASE-1-BUILD-EP04-WAVE-01

Completed:
- pharmacy package created: petcare_runtime/src/petcare/pharmacy/
- Prescription frozen dataclass with deterministic with_event() audit trail appending
- PrescriptionStatus enum: DRAFT → AUTHORIZED → SUBMITTED → DISPENSED / CANCELLED
- authorize_prescription(): ROLE_VETERINARIAN + signed_note_present hard gates enforced
- advisory-only safety warnings: ALLERGY_MATCH + MEDICATION_CONFLICT (no autonomous block)
- dispense_prescription(): ROLE_PHARMACY required
- cancel_prescription(): terminal state guard (DISPENSED / CANCELLED raise PrescriptionStateError)
- get_pharmacy_review_queue(): filters AUTHORIZED + SUBMITTED, deterministic sort
- PRESCRIPTION_AUDIT_EVENTS: 10 named events, contract-tested
- 7 unit tests written and passing

No protected-zone semantics modified.
No EP-01 / EP-02 / EP-03 baselines reopened.

Validation:
7 passed / 0 failed

Protected-zone semantics: unchanged

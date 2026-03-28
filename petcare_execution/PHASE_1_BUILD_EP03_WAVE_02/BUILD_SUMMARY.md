PACK_ID: PETCARE-PHASE-1-BUILD-EP03-WAVE-02

Completed:
- CONSULTATION_AUDIT_EVENTS constant: 14 named EP-03 event names, deterministic contract
- get_note_read_model(): deterministic sorted-key read model with read_only flag
- ConsultationRepository.list_sessions_for_pet() added
- authorize_view_consultation() added to access_control.py (owner + vet read access)
- 4 new route functions in routes_ep03.py:
    get_consultation_session_route, list_consultation_sessions,
    get_consultation_note_route, list_consultation_notes_route
- EP03_CLOSURE_READINESS.md: Decision = READY
- 15 new tests in test_ep03_wave_02.py

Changed files (scoped to Wave 02):
- petcare_runtime/src/petcare/consultation/consultation_service.py
- petcare_runtime/src/petcare/consultation/consultation_repository.py
- petcare_runtime/src/petcare/auth/access_control.py
- petcare_runtime/src/petcare/api/routes_ep03.py

Validation:
84 passed / 0 failed

Protected-zone semantics: unchanged
EP-01 / EP-02 closed baseline: unchanged
EP-03 Wave-01 semantics: unchanged

PACK_ID: PETCARE-PHASE-1-BUILD-EP03-WAVE-01

Completed:
- ConsultationSession domain model implemented (session_id, pet_id, owner_id,
  veterinarian_id, tenant_id, clinic_id, status, timestamps, escalation_requested)
- Deterministic state machine: REQUESTED→ACTIVE→COMPLETED/CANCELLED; terminal states enforced
- ConsultationNote model: NOTE_DRAFT (mutable) and NOTE_SIGNED (immutable) states
- sign_note() hard gate: only transitions DRAFT→SIGNED; raises on already-signed
- update_draft_note() immutability guard: raises ValueError("signed_note_immutable") on SIGNED
- complete_consultation requires at least one SIGNED note (no_signed_note guard)
- Escalation boundary: request_escalation() sets flag on ACTIVE session only; no Emergency logic
- ConsultationRepository: atomic tmp→replace writes; add/update/get session; add/update/list notes
- authorize_request_consultation / authorize_manage_consultation added to access_control.py
- routes_ep03.py: 8 route functions with audit events for all operations
- 17 new tests in test_ep03_wave_01.py

Changed files (scoped to Wave 01):
- petcare_runtime/src/petcare/auth/access_control.py
- petcare_runtime/src/petcare/consultation/__init__.py (new)
- petcare_runtime/src/petcare/consultation/consultation_service.py (new)
- petcare_runtime/src/petcare/consultation/consultation_repository.py (new)
- petcare_runtime/src/petcare/api/routes_ep03.py (new)

Validation:
69 passed / 0 failed

Protected-zone semantics: unchanged
EP-01 / EP-02 closed baseline: unchanged

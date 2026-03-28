PACK_ID: PETCARE-PHASE-1-NEXT-SCOPE-PLANNING
Assessment Date: 2026-03-28

Next Scope Execution Specification

Target scope:
EP-03 Tele-Vet and Care Delivery

Recommended initial build slices:
1. ConsultationSession model
   - session_id, pet_id, owner_id, veterinarian_id, tenant_id, clinic_id
   - status: REQUESTED, ACTIVE, COMPLETED, CANCELLED
   - created_at, started_at, completed_at

2. Session state transitions (governed lifecycle)
   - request_session: owner creates session request (ROLE_OWNER, PURPOSE_OWNER_SELF_SERVICE)
   - start_session: vet activates session (ROLE_VETERINARIAN, PURPOSE_CONSULTATION)
   - complete_session: vet completes session after sign-off
   - cancel_session: owner or vet may cancel before ACTIVE

3. Consultation note draft and persistence boundary
   - ConsultationNote: draft (mutable) and signed (immutable) states
   - draft owned by vet during ACTIVE session
   - no AI-authored clinical content; AI may summarize only with explicit vet review gate

4. Vet sign-off hard gate
   - sign_consultation_note: ROLE_VETERINARIAN only, requires PURPOSE_CONSULTATION
   - on sign: status transitions to SIGNED, note becomes immutable
   - immutability enforced at service layer; no update path after SIGNED

5. Immutable signed consultation behavior
   - signed ConsultationNote: read-only after signing
   - audit event emitted on sign: consultation.note.signed
   - no override path without STOP_REPORT

6. Escalation trigger preparation boundary
   - escalate_session: vet may flag session for specialist referral
   - escalation creates an EscalationRecord (status: PENDING)
   - no autonomous escalation; human vet decision required

Out-of-scope for EP-03 execution pack:
- autonomous diagnosis or prescription generation
- pharmacy lifecycle expansion (EP-04)
- emergency network activation (EP-06)
- partner marketplace integration (EP-07)
- any modification to EP-01 or EP-02 closed contracts

Protected constraints preserved from EP-01 / EP-02:
- assistive-only AI boundary: AI may not author clinical decisions
- human approval gate: mandatory before note signing
- consent required for vet document access (SCOPE_DOCUMENT_SHARING, PURPOSE_CONSULTATION)
- audit event contract: all session events must emit deterministic AuditEvent
- no protected-zone semantic drift permitted

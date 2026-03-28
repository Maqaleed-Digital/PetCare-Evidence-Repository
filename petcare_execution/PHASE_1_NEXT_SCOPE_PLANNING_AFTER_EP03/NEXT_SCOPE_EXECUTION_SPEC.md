PACK_ID: PETCARE-PHASE-1-NEXT-SCOPE-PLANNING-AFTER-EP03
Assessment Date: 2026-03-29

Next Scope Execution Specification After EP-03

Target scope:
EP-04 Pharmacy and Medication Lifecycle

Recommended initial build slices:
1. Prescription entity foundation
   - prescription_id, session_id (links to EP-03 ConsultationSession), pet_id, owner_id
   - veterinarian_id, tenant_id, clinic_id
   - medication_name, dosage, instructions, quantity
   - status: DRAFT, AUTHORIZED, SUBMITTED, DISPENSED, CANCELLED
   - created_at, authorized_at, submitted_at, dispensed_at, cancelled_at

2. Prescription status lifecycle and deterministic transitions
   - DRAFT → AUTHORIZED (vet authorizes), DRAFT → CANCELLED
   - AUTHORIZED → SUBMITTED (pharmacy receives), AUTHORIZED → CANCELLED
   - SUBMITTED → DISPENSED (pharmacist confirms dispense)
   - Terminal states: DISPENSED, CANCELLED (no further transitions)

3. Prescription creation and veterinarian authorization boundary
   - create_prescription: ROLE_VETERINARIAN, PURPOSE_CONSULTATION, session must be ACTIVE or COMPLETED
   - authorize_prescription: ROLE_VETERINARIAN only; hard gate analogous to sign_note in EP-03
   - Authorized prescription is immutable (no content edits after AUTHORIZED)

4. Medication safety baseline checks (read from EP-02 UPHR context)
   - allergy screening: read AllergyRecord for pet before AUTHORIZED
   - existing medication check: read MedicationRecord to flag potential duplicates
   - Safety check result attached to prescription at creation time (advisory only)
   - No autonomous block: vet reviews and must explicitly authorize despite any flag

5. Pharmacy review queue boundary
   - PharmacyQueue: list of AUTHORIZED prescriptions awaiting submission
   - ROLE_PHARMACY_OPERATOR access: PURPOSE_MEDICATION_FULFILLMENT + SCOPE_MEDICATION_FULFILLMENT
   - List and get operations for pharmacy operator

6. Dispense eligibility and audit boundary
   - dispense_prescription: ROLE_PHARMACY_OPERATOR, requires SUBMITTED state
   - Emit deterministic audit event: pharmacy.prescription.dispensed
   - No courier/cold-chain/delivery logic

7. Override-reason capture boundary (preparation only)
   - override_reason field on prescription (optional text, captured at authorization)
   - No autonomous override logic; vet-owned decision field

Out-of-scope for EP-04 execution pack:
- courier delivery workflows
- cold-chain operational routing
- recall workflow execution
- settlement or marketplace partner logic
- autonomous prescription issuance
- autonomous medication approval or dispensing
- Emergency network integration (EP-06)
- B2B marketplace integration (EP-07)

Protected constraints preserved from EP-01 / EP-02 / EP-03:
- assistive-only AI boundary: AI may not issue, approve, or dispense prescriptions
- human approval gate: mandatory for authorization (vet) and dispense (pharmacist)
- consent required: SCOPE_MEDICATION_FULFILLMENT for pharmacy access
- audit event contract: all prescription events must emit deterministic AuditEvent
- no protected-zone semantic drift permitted

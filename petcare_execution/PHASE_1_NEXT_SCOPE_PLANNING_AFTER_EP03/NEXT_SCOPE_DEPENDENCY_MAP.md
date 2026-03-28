PACK_ID: PETCARE-PHASE-1-NEXT-SCOPE-PLANNING-AFTER-EP03
Assessment Date: 2026-03-29

Next Scope Dependency Map After EP-03

Selected target:
EP-04 Pharmacy and Medication Lifecycle

Closed baseline dependencies consumed from EP-01:
- dependency_source: EP-01
  dependency_name: RBAC role enforcement (ROLE_VETERINARIAN, ROLE_PHARMACY_OPERATOR, ROLE_OWNER)
  consumption_mode: read-only governing input
- dependency_source: EP-01
  dependency_name: AccessContext / ResourceContext contract
  consumption_mode: read-only governing input
- dependency_source: EP-01
  dependency_name: PURPOSE_CONSULTATION, PURPOSE_MEDICATION_FULFILLMENT constraints
  consumption_mode: read-only governing input
- dependency_source: EP-01
  dependency_name: SCOPE_MEDICATION_FULFILLMENT consent scope
  consumption_mode: read-only governing input
- dependency_source: EP-01
  dependency_name: audit event contract (REQUIRED_AUDIT_FIELDS, validate_audit_event, serialize_audit_event)
  consumption_mode: read-only governing input

Closed baseline dependencies consumed from EP-02:
- dependency_source: EP-02
  dependency_name: UPHRService (MedicationRecord, AllergyRecord — read for safety checks)
  consumption_mode: read-only governing input
- dependency_source: EP-02
  dependency_name: MedicationRecord structure (medication name, dosage, recorded_at)
  consumption_mode: read-only governing input for duplicate/conflict checks
- dependency_source: EP-02
  dependency_name: AllergyRecord structure — read for allergy safety screening at dispense
  consumption_mode: read-only governing input
- dependency_source: EP-02
  dependency_name: ConsentRepository (latest_active_matching_record for SCOPE_MEDICATION_FULFILLMENT)
  consumption_mode: read-only governing input
- dependency_source: EP-02
  dependency_name: deterministic audit traceability (all changes tracked via AuditEvent)
  consumption_mode: read-only governing input

Closed baseline dependencies consumed from EP-03:
- dependency_source: EP-03
  dependency_name: ConsultationSession lifecycle (session_id links prescriptions to consultations)
  consumption_mode: read-only governing input
- dependency_source: EP-03
  dependency_name: ConsultationNote signed boundary (prescriptions may only reference SIGNED notes)
  consumption_mode: read-only governing constraint
- dependency_source: EP-03
  dependency_name: Veterinarian sign-off hard gate (vet must authorize prescription issuance)
  consumption_mode: read-only governing constraint
- dependency_source: EP-03
  dependency_name: govern consultation retrieval behavior (session status readable before prescription issue)
  consumption_mode: read-only governing input

Required dependency rule:
EP-04 must consume EP-01, EP-02, and EP-03 as closed, read-only governing input.
No prior baseline contract may be modified by EP-04 implementation without a formal STOP_REPORT.

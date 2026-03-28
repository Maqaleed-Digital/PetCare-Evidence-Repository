PACK_ID: PETCARE-PHASE-1-NEXT-SCOPE-PLANNING
Assessment Date: 2026-03-28

Next Scope Dependency Map

Selected target:
EP-03 Tele-Vet and Care Delivery

Closed baseline dependencies consumed from EP-01:
- dependency_source: EP-01
  dependency_name: RBAC role enforcement (ROLE_VETERINARIAN, ROLE_OWNER, ROLE_PLATFORM_ADMIN)
  consumption_mode: read-only governing input
- dependency_source: EP-01
  dependency_name: AccessContext / ResourceContext contract
  consumption_mode: read-only governing input
- dependency_source: EP-01
  dependency_name: authorize_manage_consent, authorize_view_document, authorize_upload_document
  consumption_mode: read-only governing input
- dependency_source: EP-01
  dependency_name: PURPOSE_CONSULTATION, PURPOSE_OWNER_SELF_SERVICE constraints
  consumption_mode: read-only governing input
- dependency_source: EP-01
  dependency_name: audit event contract (REQUIRED_AUDIT_FIELDS, validate_audit_event)
  consumption_mode: read-only governing input
- dependency_source: EP-01
  dependency_name: deterministic audit serialization (serialize_audit_event)
  consumption_mode: read-only governing input

Closed baseline dependencies consumed from EP-02:
- dependency_source: EP-02
  dependency_name: UPHRService (create_pet, get_timeline, create_document, create_clinical_note)
  consumption_mode: read-only governing input
- dependency_source: EP-02
  dependency_name: ClinicalNote immutability (no mutation path after creation)
  consumption_mode: read-only governing constraint
- dependency_source: EP-02
  dependency_name: ConsentRepository (latest_active_matching_record, list_history_for_pet)
  consumption_mode: read-only governing input
- dependency_source: EP-02
  dependency_name: BUCKET_SORT_KEY timeline ordering
  consumption_mode: read-only governing input
- dependency_source: EP-02
  dependency_name: document consent verification (consent_record_active on ResourceContext)
  consumption_mode: read-only governing input

Required dependency rule:
EP-03 must consume the closed EP-01 and EP-02 baseline as read-only governing input.
No baseline contract may be modified by EP-03 implementation without a formal STOP_REPORT.

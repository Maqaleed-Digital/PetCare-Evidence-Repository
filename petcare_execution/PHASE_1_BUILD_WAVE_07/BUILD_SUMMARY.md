PACK_ID: PETCARE-PHASE-1-BUILD-WAVE-EP01-EP02-WAVE-07

Completed:
- REQUIRED_AUDIT_FIELDS constant formalized in audit_service.py
- validate_audit_event() added: returns list of missing/empty required field names
- serialize_audit_event() made deterministic: keys returned in sorted order
- ConsentRepository.list_history_for_pet() added: returns all records regardless of status
- get_document route: auto-populates consent fields from consent store for ROLE_VETERINARIAN
  (caller no longer required to pre-fetch consent record before calling get_document)
- 9 new tests in test_ep01_ep02_wave_07

Changed files (scoped to Wave 07):
- petcare_runtime/src/petcare/audit/audit_service.py
- petcare_runtime/src/petcare/consent/consent_repository.py
- petcare_runtime/src/petcare/api/routes_ep01_ep02.py

Validation:
52 passed / 0 failed

Protected-zone semantics: unchanged

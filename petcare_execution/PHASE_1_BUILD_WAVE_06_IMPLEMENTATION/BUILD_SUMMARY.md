PACK_ID: PETCARE-PHASE-1-BUILD-WAVE-EP01-EP02-WAVE-06-IMPLEMENTATION

Completed:
- consent revocation-aware lookup implemented (latest_active_matching_record)
- ConsentRepository.update_record() added for in-place revocation
- revoke_consent route now uses update_record to replace rather than append
- upload route authorization enforced before persistence (authorize_upload_document)
- access.owner_id derived from uploaded_by_actor_id for ROLE_OWNER — ensures actor identity match
- audit event required-field contract enforced in test
- timeline sort key formalized: BUCKET_SORT_KEY per bucket, most recent first
- 9 new tests in test_ep01_ep02_wave_06

Changed files (scoped to Wave 06):
- petcare_runtime/src/petcare/auth/access_control.py
- petcare_runtime/src/petcare/consent/consent_repository.py
- petcare_runtime/src/petcare/uphr/service.py
- petcare_runtime/src/petcare/api/routes_ep01_ep02.py

Validation:
43 passed / 0 failed

Protected-zone semantics: unchanged

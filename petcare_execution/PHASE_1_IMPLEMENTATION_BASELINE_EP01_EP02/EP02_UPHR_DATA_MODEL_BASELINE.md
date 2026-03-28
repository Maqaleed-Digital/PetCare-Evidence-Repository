# EP-02 UPHR DATA MODEL BASELINE

Pack ID: PETCARE-EP01-EP02-IMPLEMENTATION-BASELINE

## 1. Objective

Define the implementation-ready baseline data model for Unified Pet Health Record core.

## 2. Primary entities

### pet
Required fields:
- pet_id
- tenant_id
- owner_id
- clinic_id_nullable
- name
- species
- breed_nullable
- sex_nullable
- birth_date_nullable
- weight_latest_nullable
- status
- created_at
- updated_at

### pet_profile
Required fields:
- pet_profile_id
- pet_id
- microchip_id_nullable
- color_nullable
- neutered_status_nullable
- diet_notes_nullable
- created_at
- updated_at

### allergy_record
Required fields:
- allergy_record_id
- pet_id
- allergen
- severity
- reaction_nullable
- status
- recorded_by_actor_id
- recorded_at
- updated_at
- version_no

### medication_record
Required fields:
- medication_record_id
- pet_id
- medication_name
- medication_type_nullable
- dose_nullable
- dose_unit_nullable
- route_nullable
- frequency_nullable
- start_date_nullable
- end_date_nullable
- status
- prescribed_by_actor_id_nullable
- recorded_at
- updated_at
- version_no

### vaccination_record
Required fields:
- vaccination_record_id
- pet_id
- vaccine_name
- administered_at
- next_due_at_nullable
- provider_name_nullable
- batch_number_nullable
- status
- recorded_at
- updated_at
- version_no

### lab_result
Required fields:
- lab_result_id
- pet_id
- lab_name
- test_name
- result_value_nullable
- result_unit_nullable
- result_flag_nullable
- collected_at_nullable
- reported_at_nullable
- attachment_document_id_nullable
- recorded_at
- updated_at
- version_no

### clinical_note
Required fields:
- clinical_note_id
- pet_id
- consultation_id_nullable
- note_type
- content_structured_or_text
- author_actor_id
- signed_by_actor_id_nullable
- signed_at_nullable
- status
- created_at
- updated_at
- version_no

### uphr_document
Required fields:
- uphr_document_id
- pet_id
- document_type
- object_storage_key
- mime_type
- size_bytes
- uploaded_by_actor_id
- visibility_scope
- checksum_sha256
- created_at

### consent_record
Required fields:
- consent_record_id
- pet_id
- owner_id
- consent_scope
- purpose_of_use
- granted_to_role
- status
- granted_at
- revoked_at_nullable
- captured_by_actor_id
- audit_reference_id

### audit_event
Required fields:
- audit_event_id
- event_name
- actor_id
- actor_role
- tenant_id
- clinic_id_nullable
- resource_type
- resource_id
- action_result
- reason_code_nullable
- correlation_id
- occurred_at

## 3. Timeline model

Timeline is a read model composed from:
- allergy_record
- medication_record
- vaccination_record
- lab_result
- clinical_note
- uphr_document references
- selected system events when later approved

Timeline baseline requirements:
- sort descending by event time
- filter by category
- search by allowed indexed metadata
- preserve audit traceability to source entity

## 4. Versioning baseline

Versioning applies to mutable clinical entities.
Minimum baseline:
- version_no increments on each update
- previous versions remain historically recoverable
- audit event links each mutation to actor and timestamp

## 5. Access and tenancy baseline

All entities must carry tenant context directly or by guaranteed relationship.
No cross-tenant record reads allowed.

## 6. AI prompt-safety baseline

Only prompt-safe views may be used for AI context assembly.
Direct raw export of sensitive identifiers into AI context is not allowed unless policy later explicitly authorizes it.
Redaction must occur before AI use.

## 7. Implementation note

This is an implementation-ready baseline, not final DDL.
The next code-build wave may translate this into concrete schema files and migrations without changing semantics.

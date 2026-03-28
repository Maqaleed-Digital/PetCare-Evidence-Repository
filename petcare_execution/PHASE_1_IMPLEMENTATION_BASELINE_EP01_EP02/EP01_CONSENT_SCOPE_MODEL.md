# EP-01 CONSENT SCOPE MODEL

Pack ID: PETCARE-EP01-EP02-IMPLEMENTATION-BASELINE

## 1. Purpose

Define the PHASE 1 consent baseline for access to pet records and care-related workflows.

## 2. Consent model entities

- consent_record
- consent_subject_owner_id
- pet_id
- consent_scope
- granted_to_role
- purpose_of_use
- granted_at
- revoked_at
- status
- captured_by_actor_id
- audit_reference_id

## 3. Authoritative consent scopes for PHASE 1

### SCOPE_PROFILE
Covers:
- pet profile demographics
- non-clinical profile visibility and updates by the owner

### SCOPE_CARE_DELIVERY
Covers:
- veterinary consultation access
- consultation-linked record updates
- care delivery workflows for authorized clinical staff

### SCOPE_MEDICATION_FULFILLMENT
Covers:
- prescription-linked pharmacy workflow access
- medication dispensing context
- status tracking relevant to fulfillment

### SCOPE_EMERGENCY_PACKET
Covers:
- summary sharing for emergency referral packet when referral workflow is active

### SCOPE_DOCUMENT_SHARING
Covers:
- attached files and documents explicitly shared for authorized care or workflow use

## 4. Purpose limitation values for PHASE 1

- purpose_consultation
- purpose_medication_fulfillment
- purpose_emergency_referral
- purpose_owner_self_service
- purpose_platform_audit
- purpose_security_investigation

## 5. Core rules

- owner grants and revokes consent
- consent is scope-specific
- access must match both granted scope and allowed purpose
- revocation blocks future use except where retention and audit obligations require continued lawful preservation
- platform audit and security investigation access remain purpose-limited and auditable
- emergency packet sharing is workflow-triggered and scope-limited

## 6. Revocation baseline

When revoked:
- future access checks fail unless another lawful basis is defined by policy
- audit events remain preserved
- historical records are not deleted automatically by revocation alone
- revocation timestamp is stored

## 7. UX and API baseline

Consent interactions required:
- grant
- revoke
- view current active consents
- view consent history

## 8. Protected semantics

The meaning of each consent scope in this file is protected.
No executor may add or redefine scope meaning without STOP_REPORT.md.

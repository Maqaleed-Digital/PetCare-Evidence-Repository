# EP-01 AUDIT EVENT TAXONOMY

Pack ID: PETCARE-EP01-EP02-IMPLEMENTATION-BASELINE

## 1. Taxonomy rules

Each event must capture:
- event_name
- occurred_at
- actor_id
- actor_role
- tenant_id
- clinic_id when applicable
- resource_type
- resource_id
- action_result
- reason_code when applicable
- correlation_id

## 2. EP-01 identity and consent events

### Identity and access events
- auth.login.succeeded
- auth.login.failed
- access.denied
- access.authorized

### Consent events
- consent.created
- consent.revoked
- consent.viewed
- consent.history.viewed

## 3. EP-02 UPHR events

### Profile and record events
- pet.profile.created
- pet.profile.viewed
- pet.profile.updated
- uphr.record.created
- uphr.record.viewed
- uphr.record.updated
- uphr.timeline.viewed

### Attachment and document events
- uphr.document.uploaded
- uphr.document.viewed
- uphr.document.access_denied

### AI prompt-safety events
- uphr.ai_redaction.applied
- uphr.ai_redaction.failed

## 4. Denial and exception events

- access.denied must be recorded when access policy blocks an operation
- uphr.document.access_denied must be recorded for document authorization failures
- uphr.ai_redaction.failed must trigger failure-safe handling and no unsafe AI context release

## 5. Naming discipline

- lower case only
- dot-separated
- action-oriented
- no cross-project legacy names
- no financial-domain semantics

## 6. Protected semantics

Event names and meanings in this file are protected for PHASE 1.
No executor may rename or repurpose these events without STOP_REPORT.md.

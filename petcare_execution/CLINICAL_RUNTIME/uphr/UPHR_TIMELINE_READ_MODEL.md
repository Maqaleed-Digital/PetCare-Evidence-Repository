UPHR TIMELINE READ MODEL

Purpose:
Provide a stable read model for the pet health timeline.

Timeline event classes:
- consultation
- prescription
- vaccination
- laboratory_result
- emergency_referral
- signed_note

Read requirements:
- deterministic ordering by timestamp_utc
- pagination support
- filter by event class
- audit trace linkage to source event

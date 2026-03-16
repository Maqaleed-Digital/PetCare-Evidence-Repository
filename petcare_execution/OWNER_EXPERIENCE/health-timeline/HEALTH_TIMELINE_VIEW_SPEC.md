HEALTH TIMELINE VIEW SPEC

Purpose:
Define the deterministic owner-facing health timeline surface.

Timeline classes:
- consultation
- prescription
- vaccination
- lab_result
- emergency_event

Requirements:
- deterministic ordering by timestamp
- pagination support
- filter by event class
- timeline detail must reference source event

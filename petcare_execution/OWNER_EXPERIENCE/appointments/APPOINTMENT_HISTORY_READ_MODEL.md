APPOINTMENT HISTORY READ MODEL

Purpose:
Define the deterministic owner-facing appointment history surface.

Required fields:
- appointment_id
- appointment_type
- clinic_id
- scheduled_slot
- state
- completion_status

Requirements:
- deterministic ordering
- historical appointments remain visible after completion or cancellation
- pagination supported

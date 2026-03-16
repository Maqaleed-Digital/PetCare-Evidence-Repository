APPOINTMENT BOOKING WORKFLOW

States:
- requested
- confirmed
- reschedule_requested
- cancelled
- completed

Rules:
- booking request must reference pet_id and clinic_id
- reschedule and cancel actions remain owner-auditable
- conflict handling must return explicit outcome
- appointment history remains readable to the owner

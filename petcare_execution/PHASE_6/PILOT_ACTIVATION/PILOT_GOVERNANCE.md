PILOT GOVERNANCE

REQUIRED TRACKING:

- clinic_id
- vet_id
- user_id
- session_id
- consultation_id
- prescription_id

MANDATORY EVENTS:

- appointment.created
- consultation.started
- consultation.completed
- consultation.signed
- prescription.issued
- audit.logged

FAIL CONDITIONS:

- missing audit event
- unsigned consultation
- prescription without vet approval

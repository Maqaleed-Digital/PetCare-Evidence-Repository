PH6.3 CONTROLLED PILOT CREDENTIAL ISSUANCE REGISTER

PURPOSE
Track governed issuance of pilot credentials for live production role-journey validation.

REQUIRED FIELDS PER ISSUED ACCOUNT
- issuance_id
- issued_at_utc
- issued_by
- participant_real_name
- participant_role
- participant_email
- participant_entity
- clinic_id_or_platform_scope
- approval_reference
- credential_delivery_method
- first_login_required
- password_reset_required
- mfa_status
- account_status
- validation_status
- notes

ALLOWED ROLES
- owner
- vet
- admin

ROLE RULES

OWNER
- may access owner-safe area only
- must not resolve to vet or admin surfaces

VET
- must be linked to verified clinic / licensed operator context
- may access vet-safe area only

ADMIN
- must be explicitly approved
- may access admin governance area only

MANDATORY CONTROLS
- human approval before issuance
- issuance logged
- first login tracked
- reset and activation trace retained
- no shared credentials
- no prototype/demo credentials reused

FAIL CONDITIONS
- role mismatch
- shared credential
- unapproved issuance
- missing issuance trace
- authenticated user resolves to wrong area

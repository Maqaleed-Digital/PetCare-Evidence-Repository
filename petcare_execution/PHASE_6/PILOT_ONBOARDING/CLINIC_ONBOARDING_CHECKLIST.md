CLINIC ONBOARDING CHECKLIST

REQUIRED:

- clinic_name
- commercial_registration
- license_status (verified)
- location
- contact_person

VET REQUIREMENTS:

- vet_id
- license_number
- specialization
- verification_status = VERIFIED

SYSTEM REQUIREMENTS:

- account created via UI
- RBAC role assigned (vet)
- audit logs present

FAIL CONDITIONS:

- missing license
- manual DB insertion
- missing audit trace

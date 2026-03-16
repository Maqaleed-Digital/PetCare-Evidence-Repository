RBAC ROLE MATRIX

Roles:
- owner
- vet
- pharmacy_operator
- clinic_admin
- platform_admin

Core enforcement rules:
- tenant isolation mandatory before role evaluation
- least privilege mandatory
- all denied actions return explicit reason_code
- all authorization decisions may be audit-logged

Minimum capability model:
- owner: own pet records, appointments, consent management
- vet: consultations, notes, sign-off initiation, prescription issuance
- pharmacy_operator: prescription queue, dispense workflow, inventory safety handling
- clinic_admin: clinic profile, vet roster, operating hours, SLA visibility
- platform_admin: tenant administration, audit export, configuration visibility

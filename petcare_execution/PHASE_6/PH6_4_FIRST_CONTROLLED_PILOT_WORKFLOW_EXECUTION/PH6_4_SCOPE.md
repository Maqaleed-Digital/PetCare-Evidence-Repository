PETCARE-PHASE-6.4 — FIRST CONTROLLED PILOT WORKFLOW EXECUTION

OBJECTIVE
Validate the first controlled authenticated pilot workflow on the live production platform using real issued pilot identities and governed role-safe access boundaries.

TARGET WORKFLOW
appointment -> consultation -> sign-off -> prescription
OR
appointment -> consultation -> sign-off -> controlled clinical outcome record

MINIMUM REQUIRED PARTICIPANTS
- 1 real owner account
- 1 real vet account
- 1 real admin account for governance oversight if needed

ENTRY CONDITION
Begin PH6.4 only after:
- owner credential issued and validated
- vet credential issued and validated
- admin credential issued and validated
- A-01 completed
- A-02 completed
- A-03 completed

ROLE BOUNDARIES

OWNER
- may create or participate in owner-safe workflow steps only
- must not enter vet or admin space

VET
- may perform consultation and clinical sign-off actions permitted by role
- human sign-off remains mandatory

ADMIN
- may observe or support governance and operational oversight only
- must not substitute for clinical role actions

NON-NEGOTIABLES
- no fake usage
- no demo or prototype accounts used as pilot proof
- no hidden execution
- no bypass of UI
- no direct database shortcut
- no weakening of sign-off or governance boundaries
- fail-closed remains active

SUCCESS CONDITION
PH6.4 proves that the live platform can execute the first controlled authenticated pilot workflow across owner, vet, and admin-governed boundaries with evidence captured for the critical workflow steps.

OUTPUTS
- scope file
- workflow validation checklist
- role participation register
- deterministic evidence runner
- timestamped evidence run directory with SHA256 manifest

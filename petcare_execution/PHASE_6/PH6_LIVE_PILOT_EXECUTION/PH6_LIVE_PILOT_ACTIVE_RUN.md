PETCARE — PH6 LIVE PILOT ACTIVE RUN

Application Source of Truth
ec53458d

Objective
Execute the first real governed pilot workflow with the approved live pilot cohort and capture operational evidence.

Required Live Inputs
- PILOT_OPERATOR
- PILOT_INCIDENT_CHANNEL
- PILOT_APPROVAL_REF
- PILOT_EXECUTION_WINDOW_UTC
- PILOT_CLINIC_NAME
- PILOT_CLINIC_LICENSE_REF
- PILOT_VET_1_NAME
- PILOT_VET_1_LICENSE_REF
- PILOT_OWNER_CASE_1_REF
- PILOT_PRODUCTION_URL
- PILOT_APPOINTMENT_REF
- PILOT_CONSULTATION_REF
- PILOT_SIGNOFF_REF
- PILOT_PRESCRIPTION_REF (optional)
- PILOT_RUN_RESULT
- PILOT_BLOCKERS (optional)
- PILOT_OPERATOR_NOTES

Required Workflow
appointment → consultation → sign-off → prescription if clinically applicable

Execution Rules
- real values only
- no demo
- no test
- no placeholder
- no direct DB injection
- no auth bypass
- no UI bypass
- no synthetic evidence
- evidence must reflect the actual live run outcome only

Required Outcome Recording
- appointment reference
- consultation reference
- sign-off reference
- prescription reference if clinically applicable
- clinic reference
- veterinarian reference
- owner case reference
- run result
- blockers if any
- operator notes

Success Condition
The real pilot workflow is executed and evidence is captured with a truthful PASS or BLOCKED/FAILED outcome.

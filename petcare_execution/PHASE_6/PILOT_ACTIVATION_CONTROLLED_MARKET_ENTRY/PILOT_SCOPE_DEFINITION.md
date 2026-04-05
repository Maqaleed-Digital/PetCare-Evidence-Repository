PILOT ACTIVATION SCOPE (PH6)

Constraints:
- Max clinics: enforced via environment variable
- Max vets: enforced via environment variable
- Real workflows only
- No simulation allowed

Allowed Workflows:
- Appointment booking
- Consultation
- Prescription issuance
- Pharmacy fulfillment

Prohibited:
- Autonomous execution
- Data simulation
- UI bypass
- Manual shadow operations

Success Criteria:
- Real workflow completion
- Audit trace present for all actions
- No governance violations

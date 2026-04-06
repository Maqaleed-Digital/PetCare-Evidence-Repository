PETCARE-PHASE-6.3 — CONTROLLED PILOT CREDENTIAL ISSUANCE + AUTHENTICATED ROLE JOURNEY VALIDATION

OBJECTIVE
Issue controlled pilot credentials to real approved pilot participants and validate authenticated role-safe journeys on the live production platform without weakening governance, bypassing UI, or relying on prototype/demo accounts.

IN SCOPE

1. Controlled Credential Issuance
- owner pilot credential issuance
- vet pilot credential issuance
- admin pilot credential issuance
- issuance record structure
- activation status tracking

2. Authenticated Journey Validation
- owner login and role-safe resolution
- vet login and role-safe resolution
- admin login and role-safe resolution

3. Evidence and Governance
- issuance register template
- validation checklist
- deterministic evidence runner
- timestamped evidence pack with SHA256 manifest

NON-NEGOTIABLES
- no direct database insertion as operational shortcut
- no fake or demo users counted as pilot users
- no prototype seeded credentials treated as production truth
- no hidden execution
- fail-closed remains active
- protected routes remain protected
- credential issuance must be human-governed and traceable

SUCCESS CONDITION
This phase proves that controlled real pilot identities can enter the live system through governed credentials and resolve only to their permitted role-safe journeys.

OUTPUTS
- scope file
- credential issuance register template
- authenticated validation checklist
- deterministic evidence runner
- timestamped evidence run directory with SHA256 manifest

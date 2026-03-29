Pack: PETCARE-PHASE-1-BUILD-EP04-WAVE-01
Status: Committed

Objective:
- implement Prescription lifecycle foundation for EP-04 Pharmacy and Medication Lifecycle
- enforce ROLE_VETERINARIAN authorization gate with signed note requirement
- implement advisory-only safety screening (allergy + active medication conflict)
- implement pharmacy dispense gate (ROLE_PHARMACY)
- implement deterministic pharmacy review queue
- preserve EP-01 / EP-02 / EP-03 closed baselines

Outcome:
- pharmacy package at petcare_runtime/src/petcare/pharmacy/ fully operational
- 7 tests passing
- PRESCRIPTION_AUDIT_EVENTS contract established (10 events)

Constraints enforced:
- no guessing
- minimum files only
- no protected-zone semantic changes
- closed EP-01 / EP-02 / EP-03 baselines preserved
- deterministic evidence output

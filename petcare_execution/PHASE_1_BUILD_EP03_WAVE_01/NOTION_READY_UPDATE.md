Pack: PETCARE-PHASE-1-BUILD-EP03-WAVE-01
Status: Implemented Pending Commit

Objective:
- implement ConsultationSession foundation for EP-03 Tele-Vet and Care Delivery
- define deterministic consultation state transitions
- establish consultation note draft vs signed boundary
- enforce veterinarian sign-off hard gate
- preserve immutable signed consultation behavior
- prepare escalation trigger boundary without expanding into Emergency domain

Constraints enforced:
- no guessing
- minimum files only
- EP-01 and EP-02 closed baseline preserved
- no Emergency domain expansion
- no protected-zone semantic drift
- deterministic evidence output

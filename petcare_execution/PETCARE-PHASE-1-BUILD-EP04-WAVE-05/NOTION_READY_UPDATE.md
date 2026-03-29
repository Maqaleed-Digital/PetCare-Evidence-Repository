Pack: PETCARE-PHASE-1-BUILD-EP04-WAVE-05
Status: Committed

Objective:
- extend EP-04 with additive review-to-dispense queue handoff boundary
- add formal handoff read/list surfaces
- add latest review decision summary read model
- add explicit return-to-vet outcome handling
- preserve all Wave-01 through Wave-04 semantics

Outcome:
- pharmacy/handoff.py with 8 exported symbols
- REVIEW_HANDOFF_AUDIT_EVENTS (3) + REVIEW_HANDOFF_OUTCOMES (3) contracts locked
- 37 total tests passing (7+6+8+8+8)
- no prescription state mutated by handoff boundary

Constraints enforced:
- no guessing
- minimum files only
- no protected-zone semantic changes
- closed EP-01 / EP-02 / EP-03 baselines preserved
- no blocking logic
- no AI autonomy
- deterministic evidence output

Pack: PETCARE-PHASE-1-BUILD-EP04-WAVE-06
Status: Committed

Objective:
- extend EP-04 with additive review visibility surfaces
- add access audit envelopes at function level
- add review history + timeline retrieval models
- add return-to-vet follow-up linkage structure
- add disposition registry helper
- add deterministic operational aggregation

Outcome:
- pharmacy/visibility.py with 10 exported symbols
- REVIEW_ACCESS_AUDIT_EVENTS (5) + RETURN_TO_VET_REASON_CODES (2) contracts locked
- 44 total tests passing (7+6+8+8+8+7)
- no prescription state mutated by visibility surfaces

Constraints enforced:
- no guessing
- minimum files only
- no protected-zone semantic changes
- closed EP-01 / EP-02 / EP-03 baselines preserved
- no blocking logic
- no AI autonomy
- deterministic evidence output

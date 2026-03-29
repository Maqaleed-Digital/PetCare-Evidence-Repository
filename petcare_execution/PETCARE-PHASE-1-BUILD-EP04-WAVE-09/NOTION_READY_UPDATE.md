Pack: PETCARE-PHASE-1-BUILD-EP04-WAVE-09
Status: Committed

Objective:
- extend EP-04 with API contract normalization and endpoint registry
- add success/error envelope contract
- add read-only endpoint registry
- add normalize_response / normalize_error helpers on api.py
- preserve all Wave-01 through Wave-08 semantics

Outcome:
- pharmacy/contracts.py and pharmacy/registry.py added
- api.py extended with normalize_response() + normalize_error()
- 55 total tests passing
- no prescription state mutated

Constraints enforced:
- no guessing
- minimum files only
- no protected-zone semantic changes
- closed EP-01 / EP-02 / EP-03 baselines preserved
- no blocking logic
- no AI autonomy
- deterministic evidence output

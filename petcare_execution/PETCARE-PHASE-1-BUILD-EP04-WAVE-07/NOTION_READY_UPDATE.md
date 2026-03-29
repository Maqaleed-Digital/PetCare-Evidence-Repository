Pack: PETCARE-PHASE-1-BUILD-EP04-WAVE-07
Status: Committed

Objective:
- extend EP-04 with deterministic repository store and query composition layer
- add PharmacyRepository for in-memory prescription + review storage
- add get_full_review_context() composition query
- add list_reviews_for_prescription() query
- preserve all Wave-01 through Wave-06 semantics

Outcome:
- pharmacy/repository.py and pharmacy/query.py added
- 46 total tests passing (7+6+8+8+8+7+2)
- no prescription state mutated

Constraints enforced:
- no guessing
- minimum files only
- no protected-zone semantic changes
- closed EP-01 / EP-02 / EP-03 baselines preserved
- no blocking logic
- no AI autonomy
- deterministic evidence output

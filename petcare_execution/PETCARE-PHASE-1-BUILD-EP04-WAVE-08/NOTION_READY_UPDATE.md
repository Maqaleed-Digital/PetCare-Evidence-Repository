Pack: PETCARE-PHASE-1-BUILD-EP04-WAVE-08
Status: Committed

Objective:
- extend EP-04 with additive read-only API exposure layer
- expose review, handoff, history, timeline, follow-up, registry, queue, operational summary
- all surfaces via deterministic read-only envelope
- preserve all Wave-01 through Wave-07 semantics

Outcome:
- pharmacy/api.py with 12 exported symbols (11 surfaces + READ_ONLY_API_SURFACES)
- 51 total tests passing (7+6+8+8+8+7+2+5)
- no prescription state mutated by API layer

Constraints enforced:
- no guessing
- minimum files only
- no protected-zone semantic changes
- closed EP-01 / EP-02 / EP-03 baselines preserved
- no blocking logic
- no AI autonomy
- deterministic evidence output

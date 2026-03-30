# PETCARE — EP-10 HARD GATES

## G-F11 Integration Contract Integrity
- adapter contracts explicitly defined
- reference identifiers stable and traceable
- no implicit execution behavior embedded in adapter model

## G-F12 External Signal Trust Boundary
- webhook and external signals classified before use
- trust outcome recorded
- no external signal may bypass human review where required
- external signals cannot autonomously release money or approvals

## G-F13 Human Action Traceability
- every operator action attributable to actor identity
- timestamp required
- action outcome recorded
- escalation chain preserved

## G-F14 Queue Determinism
- queue ordering rules explicitly defined
- priority logic deterministic
- no hidden reordering
- claim and release rules auditable

## G-F15 Adapter Non-Autonomy Guarantee
- adapters are passive, export-oriented, or ingestion-oriented only
- no direct external execution from EP-10
- no adapter may mutate sealed financial boundary decisions autonomously

## Pass Conditions
- tests pass
- evidence pack generated
- manifest generated
- working tree committed and pushed

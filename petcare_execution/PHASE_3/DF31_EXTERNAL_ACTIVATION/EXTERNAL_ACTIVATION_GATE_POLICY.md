EXTERNAL ACTIVATION GATE POLICY — DF31

MANDATORY GATES

G-ACT-1 APPROVAL GATE
- explicit human approval required

G-ACT-2 SANDBOX VALIDATION GATE
- sandbox execution verified
- no production interaction

G-ACT-3 AUDIT TRACE GATE
- full logging enabled
- traceability verified

G-ACT-4 POLICY ALIGNMENT GATE
- policy checksum verified
- no drift

G-ACT-5 REVERSIBILITY GATE
- kill-switch verified
- rollback tested

ACTIVATION STATES

- sandbox_active
- validation_active
- limited_production
- fully_active
- blocked

FAIL CONDITIONS

ANY FAILED GATE → BLOCK ACTIVATION

PETCARE DF10
Validation

Validation Steps
1. Run exposure control in default mode and confirm PRIVATE_ONLY pass
2. Run controlled public mode without approval and confirm fail-closed
3. Run controlled public mode with approval variables and confirm simulation pass
4. Confirm evidence pack generation
5. Confirm no real production exposure change occurs

Expected Results
Default mode returns PASS and remains private
Public mode without approval returns non-zero
Public mode with approval returns zero in simulation only
Evidence manifest and checksum are generated

Governance Constraint
Passing DF10 does not authorize real public production exposure by itself.

PETCARE DF07
Validation

Validation Steps
1. Run release gate check with missing variables and confirm fail-closed
2. Run release gate check with sample variables and confirm pass output
3. Run post-deploy verification against a known healthy endpoint
4. Run evidence pack generation and confirm manifest and checksum exist

Expected Results
Release gate script returns non-zero when required fields are missing
Release gate script returns zero only when all required fields are present
Post-deploy verification checks health and readiness independently
Evidence pack generator writes deterministic outputs into timestamped run folder

Governance Constraint
Passing DF07 validation does not authorize production deployment by itself.

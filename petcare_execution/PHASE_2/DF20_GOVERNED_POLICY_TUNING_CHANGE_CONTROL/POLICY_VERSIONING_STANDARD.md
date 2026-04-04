# PETCARE DF20 — Policy Versioning Standard

## Purpose
Ensure all governed policy changes are explicit, traceable, and reversible.

## Versioning Rules
- every approved change increments policy version
- no in-place silent overwrite
- before and after states must both be preserved
- rollback target must always be known

## Required Versioning Artifacts
- policy_before.json
- policy_after.json
- version_transition.json

## Reversion Rule
Rollback must restore the last approved version exactly.

# PETCARE DF21 — Release Versioning Standard

## Purpose
Ensure baseline promotion is explicit, reversible, and traceable.

## Versioning Rules
- every ratified baseline promotion increments release version
- no in-place silent overwrite of active baseline
- before and after baselines must both be preserved
- rollback target must always be known

## Required Versioning Artifacts
- baseline_before.json
- baseline_after.json
- baseline_transition.json

## Rollback Rule
Rollback must restore the last ratified baseline exactly.

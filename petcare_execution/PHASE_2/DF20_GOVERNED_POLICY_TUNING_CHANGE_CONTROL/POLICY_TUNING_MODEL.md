# PETCARE DF20 — Governed Policy Tuning Model

## Purpose
Provide a fail-closed mechanism for changing execution policies using evidence-backed review.

## Scope
This phase governs changes to:
- scoring weights
- variance thresholds
- capacity limits
- review tolerances
- sequencing policy parameters

## Core Rule
No policy change is valid unless it is:
- requested
- justified
- reviewed
- approved
- versioned
- evidenced

## Forbidden
- silent tuning
- runtime mutation
- automatic self-adjustment
- undocumented threshold changes
- unversioned policy edits

## Output
Every approved policy change must produce:
- policy_change_record.json
- policy_before.json
- policy_after.json
- approval_log.txt
- impact_statement.txt

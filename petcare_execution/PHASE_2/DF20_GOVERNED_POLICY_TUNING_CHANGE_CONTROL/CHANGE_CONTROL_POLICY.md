# PETCARE DF20 — Change Control Policy

## Purpose
Define how policy changes are requested, reviewed, approved, and activated.

## Required Change Stages
- PROPOSED
- UNDER_REVIEW
- APPROVED
- REJECTED
- ACTIVATED

## Mandatory Fields
- change_id
- change_type
- requested_by
- approved_by
- reason
- expected_effect
- affected_policy_scope
- effective_date_utc
- policy_version_before
- policy_version_after

## Activation Rule
A policy change may activate only after:
- approval is recorded
- evidence is generated
- version change is declared

## Fail-Closed Rule
If any mandatory field is missing, change activation must be blocked.

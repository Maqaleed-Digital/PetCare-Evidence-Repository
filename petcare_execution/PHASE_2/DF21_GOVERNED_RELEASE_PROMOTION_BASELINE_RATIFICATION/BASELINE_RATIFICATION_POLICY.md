# PETCARE DF21 — Baseline Ratification Policy

## Purpose
Define how an approved release candidate becomes the official baseline.

## Required Ratification States
- CANDIDATE_DEFINED
- UNDER_REVIEW
- APPROVED_FOR_PROMOTION
- RATIFIED
- ACTIVE_BASELINE

## Mandatory Fields
- release_id
- baseline_version_before
- baseline_version_after
- candidate_scope
- requested_by
- approved_by
- ratified_by
- ratification_reason
- effective_date_utc

## Ratification Rule
A release candidate may become active baseline only after:
- approval is recorded
- ratification is recorded
- before/after baseline states are captured
- evidence pack is generated

## Fail-Closed Rule
If any mandatory field is missing, ratification must be blocked.

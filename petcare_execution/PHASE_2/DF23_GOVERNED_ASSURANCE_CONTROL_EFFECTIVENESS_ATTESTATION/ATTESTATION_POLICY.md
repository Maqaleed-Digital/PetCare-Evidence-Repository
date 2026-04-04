# PETCARE DF23 — Attestation Policy

## Purpose
Define fail-closed attestation requirements for control assurance.

## Attestation Statuses
- READY_FOR_ATTESTATION
- ATTESTED_EFFECTIVE
- ATTESTED_WITH_EXCEPTIONS
- NOT_ATTESTED

## Required Attestation Inputs
- assurance_scope
- assurance_result
- exception_count
- approver
- attestor
- attestation_reason

## Rule
Attestation may occur only after assurance evidence is complete and effectiveness result is recorded.

## Exception Rule
If exceptions exist, attestation must explicitly record them.

## Forbidden
- attestation without assurance evidence
- silent exception omission
- attestation without named attestor

# PETCARE DF23 — Control Effectiveness Policy

## Purpose
Define how control effectiveness is evaluated.

## Effectiveness States
- EFFECTIVE
- PARTIALLY_EFFECTIVE
- INEFFECTIVE

## Required Inputs
- control_id
- control_objective
- expected_behavior
- observed_behavior
- test_result
- evidence_reference

## Evaluation Rule
Every control under assurance review must be explicitly evaluated against expected behavior.

## Degradation Rule
If observed behavior deviates from expected behavior, degradation must be recorded.

## Forbidden
- assumed effectiveness
- undocumented degraded control state
- closing ineffective control without remediation trigger

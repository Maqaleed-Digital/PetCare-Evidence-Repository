# PETCARE DF24 — Degraded Mode Policy

## Purpose
Define how the platform behaves when disruption prevents normal steady-state operation.

## Degraded Mode States
- CONTROLLED_DEGRADED
- LIMITED_OPERATION
- RECOVERY_IN_PROGRESS
- NORMAL_OPERATION_RESTORED

## Required Inputs
- disruption_type
- affected_scope
- service_reduction_level
- governance_controls_retained
- escalation_status

## Rule
Any degraded mode activation must preserve governance-critical controls and record the reduced operating state explicitly.

## Forbidden
- degraded operation without explicit state declaration
- bypass of governance controls during degradation
- restoration without recorded degraded-mode exit

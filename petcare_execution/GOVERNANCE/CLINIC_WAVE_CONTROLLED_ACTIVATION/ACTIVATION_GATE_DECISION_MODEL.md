# ACTIVATION_GATE_DECISION_MODEL

## Purpose
This document defines the gate logic required before a clinic placeholder may enter controlled activation.

## Required gate inputs
The activation gate must review:

1. execution readiness status
2. AI safety readiness
3. staffing coverage confirmation
4. escalation routing confirmation
5. partner dependency readiness
6. reporting visibility confirmation
7. first-day operational control readiness
8. portfolio command approval

## Decision outcomes
The gate may issue one of the following outcomes only:

- approved_for_activation
- blocked_pending_remediation
- deferred_for_wave_resequencing

## Gate rule
No clinic may self-approve. Final gate approval remains a portfolio-level decision.

## Recheck rule
If a clinic is blocked or deferred, it must re-enter gate review before any new activation attempt.

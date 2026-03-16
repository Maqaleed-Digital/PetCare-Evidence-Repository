# CONTROLLED ACTIVATION POLICY

## Purpose
This document governs controlled activation of clinic waves after execution readiness has been positively established.

## Activation principle
Activation is not a bulk rollout. Each clinic enters service through a controlled, sequenced, observable activation model.

## Controlled activation posture
The approved posture is:

1. one controlled sequence at a time
2. explicit gate decision before activation
3. first-day operating controls enabled
4. escalation available at all times
5. hypercare starts immediately after activation

## Deterministic clinic placeholders
This pack preserves governance-safe identifiers only:

- CLINIC-WAVE2-001
- CLINIC-WAVE2-002
- CLINIC-WAVEN-001
- CLINIC-WAVEN-002

## Activation preconditions
A clinic may only be activated when all of the following are true:

- clinic is marked ready_for_execution
- activation gate decision is approved
- activation window is assigned
- first-day control spec is assigned
- local escalation owner is assigned
- reporting and evidence paths are active

## Hard stop conditions
Activation must not proceed if any of the following exist:

- unresolved readiness defect
- unresolved safety defect
- missing first-day controls
- missing local command assignment
- missing escalation route
- missing reporting visibility

## Output of this pack
This pack authorizes the governance model for controlled activation but does not claim any real clinic has already gone live.

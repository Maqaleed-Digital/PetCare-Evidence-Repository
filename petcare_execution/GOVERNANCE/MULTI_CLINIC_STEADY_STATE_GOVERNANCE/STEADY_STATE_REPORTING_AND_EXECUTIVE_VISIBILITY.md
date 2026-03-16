# STEADY STATE REPORTING AND EXECUTIVE VISIBILITY

## Purpose
This document defines the minimum reporting and executive visibility model for multi-clinic steady-state operation.

## Required reporting outputs
Steady-state reporting must show:

1. clinic steady-state status
2. control posture status
3. override posture status
4. escalation posture status
5. KPI completeness status
6. partner fallback posture status
7. drift status
8. remediation status

## Required clinic states
Each clinic in this phase must be visible as one of:

- steady_state_operational
- steady_state_watch
- drift_issue_open
- remediation_reentry_required
- executive_review_required

## Executive visibility use
Executive visibility must support:

- portfolio operating snapshot
- exception detection
- cross-clinic comparison
- intervention prioritization

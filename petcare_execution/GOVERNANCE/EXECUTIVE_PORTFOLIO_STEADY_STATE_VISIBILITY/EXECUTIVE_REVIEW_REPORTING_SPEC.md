# EXECUTIVE REVIEW REPORTING SPEC

## Purpose
This document defines the minimum executive review reporting outputs for the steady-state portfolio.

## Required executive reporting outputs
Executive review reporting must show:

1. portfolio clinic count
2. steady-state posture summary
3. watch posture summary
4. drift issue summary
5. remediation reentry summary
6. override posture summary
7. escalation posture summary
8. KPI completeness summary

## Required clinic states
Each clinic in the executive layer must be visible as one of:

- steady_state_operational
- steady_state_watch
- drift_issue_open
- remediation_reentry_required
- executive_review_required

## Executive review use
Executive reporting must support:

- portfolio confidence review
- exception-led oversight
- prioritization of intervention attention
- comparison against the baseline clinic

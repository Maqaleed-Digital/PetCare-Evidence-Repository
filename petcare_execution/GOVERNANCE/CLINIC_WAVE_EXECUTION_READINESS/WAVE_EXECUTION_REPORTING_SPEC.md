# WAVE EXECUTION REPORTING SPEC

## Purpose
This document defines the minimum reporting outputs required during clinic-wave execution.

## Required reporting entities
Reporting must exist at:

- clinic level
- wave level
- portfolio level

## Minimum reporting metrics
1. clinic admission status
2. execution readiness status
3. hypercare status
4. override event count
5. escalation event count
6. KPI capture completeness
7. staffing exception count
8. partner fallback count

## Reporting frequency model
- clinic: operational review cadence
- wave: wave command review cadence
- portfolio: governance review cadence

## Required reporting outcome states
Every clinic must be visible as one of:

- not_ready
- ready_for_execution
- in_hypercare
- ready_for_steady_state
- remediation_required

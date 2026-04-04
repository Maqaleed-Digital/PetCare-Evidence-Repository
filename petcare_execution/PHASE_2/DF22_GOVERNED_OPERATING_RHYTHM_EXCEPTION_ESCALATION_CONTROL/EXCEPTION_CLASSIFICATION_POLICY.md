# PETCARE DF22 — Exception Classification Policy

## Purpose
Define how operating exceptions are identified and classified.

## Exception Classes
- LOW
- MODERATE
- HIGH
- CRITICAL

## Classification Inputs
- affected_scope
- severity
- duration
- control_breach_flag
- patient_or_clinical_risk_flag
- operational_disruption_flag

## Classification Rule
Every exception must be explicitly classified before escalation routing is allowed.

## Forbidden
- unclassified exceptions
- silent control breaches
- unrecorded critical exceptions

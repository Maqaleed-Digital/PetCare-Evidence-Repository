# MULTI_CLINIC_OPERATING_COMMAND_MODEL

## Purpose
This document defines the minimum operating command model for governing multiple PetCare clinics during wave execution.

## Command layers
The command structure contains:

1. portfolio governance layer
2. wave execution command layer
3. clinic local operating layer

## Minimum command assignments
The model requires the following named roles by function, not by person:

- portfolio_governance_owner
- wave_execution_owner
- clinical_safety_owner
- ai_safety_owner
- reporting_owner
- escalation_owner
- clinic_local_owner

## Command rules
- portfolio governance retains overall authority
- wave execution command coordinates rollout sequence
- clinic local ownership cannot bypass portfolio safety rules
- AI safety rules remain centrally governed
- incidents escalate upward, not sideways
- no clinic is self-authorizing for steady-state admission

## Decision boundaries
Only portfolio governance may authorize:
- execution start
- hypercare exit
- remediation closure
- steady-state admission

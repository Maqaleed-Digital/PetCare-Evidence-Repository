# PETCARE DF23 — Remediation Trigger Guardrails

## Purpose
Define how ineffective or degraded controls trigger governed remediation.

## Trigger Conditions
- effectiveness_result = INEFFECTIVE
- repeated partial effectiveness
- control degradation detected
- attestation with exceptions

## Required Outputs
- remediation_trigger_record.json
- remediation_scope
- remediation_priority
- remediation_owner

## Guardrails
- no ineffective control may be silently accepted
- no remediation trigger may bypass governance recording
- remediation may not alter policy or baseline directly without governed downstream phases
- remediation trigger must remain traceable to failed assurance evidence

## Scope
Remediation trigger may be scoped to:
- global
- portfolio segment
- named unit
- named control family

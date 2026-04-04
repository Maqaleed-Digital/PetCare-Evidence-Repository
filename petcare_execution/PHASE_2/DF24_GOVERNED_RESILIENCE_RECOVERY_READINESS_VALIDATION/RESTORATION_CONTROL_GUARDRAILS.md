# PETCARE DF24 — Restoration Control Guardrails

## Purpose
Define how restoration back to normal operation is governed.

## Guardrails
- no restoration without recorded degraded-mode state
- no restoration without readiness validation
- no restoration without explicit restoration result
- restoration must remain traceable to disruption and recovery evidence
- failed restoration must trigger exception governance

## Required Outputs
- restoration_record.json
- restoration_summary.txt

## Scope
Restoration may be scoped to:
- global
- portfolio segment
- named unit
- named service/control family

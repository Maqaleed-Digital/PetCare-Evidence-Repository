# PETCARE DF18 — Capacity Governance Model

## Purpose
Define safe execution limits across the platform.

## Capacity Dimensions
- max_concurrent_executions
- per_unit_execution_limit
- execution_window (time-based)
- resource_load_threshold

## Default Policy
- max_concurrent_executions = 3
- per_unit_execution_limit = 1
- execution_window = controlled
- resource_load_threshold = defined externally

## Rules
- exceeding capacity → BLOCK
- exceeding unit limit → BLOCK
- execution outside window → BLOCK

## Override Rule
Capacity overrides require:
- explicit approval
- defined scope
- time-bound validity
- evidence record

## Fail-Closed
If capacity cannot be determined → BLOCK
